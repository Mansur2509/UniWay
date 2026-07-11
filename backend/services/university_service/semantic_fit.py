from __future__ import annotations

import json
import logging
import time

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from services.ai_gateway_service.exceptions import AIProviderError, AIProviderUnavailable
from services.ai_gateway_service.logging import log_ai_call
from services.ai_gateway_service.schemas import (
    SEMANTIC_FIT_RESPONSE_SCHEMA,
    SEMANTIC_FIT_SYSTEM_PROMPT,
)
from services.ai_gateway_service.semantic_fit_client import GeminiSemanticFitClient
from services.profile_assessment_service.services import compute_profile_snapshot_hash

from .models import University, UniversitySemanticFit
from .services import calculate_university_fit

logger = logging.getLogger(__name__)

# Bump this if the prompt/schema shape changes so old cached rows are treated
# as stale rather than served with an outdated meaning.
PROMPT_VERSION = "1"

MAX_NEXT_ACTIONS = 4
DAILY_COUNT_CACHE_TTL_SECONDS = 86_400

# calculate_university_fit's `category` uses "safety" internally (shared with
# recommendations.py/strategy.py); the public tier vocabulary for this task
# is Reach/Competitive/Target/Safer, so this is a display-only remap, never a
# second scoring pass.
_TIER_BY_CATEGORY = {
    "reach": "reach",
    "dream": "reach",
    "competitive": "competitive",
    "target": "target",
    "safety": "safer",
}


def map_tier(category: str | None) -> str:
    if category is None:
        return "unknown"
    return _TIER_BY_CATEGORY.get(category, "unknown")


def semantic_fit_ai_available() -> bool:
    return bool(settings.AI_SEMANTIC_FIT_ENABLED and settings.GEMINI_API_KEY)


def _daily_count_cache_key(user) -> str:
    return f"semantic-fit-daily-count:{user.id}:{timezone.now().date().isoformat()}"


def _daily_limit_reached(user) -> bool:
    return cache.get(_daily_count_cache_key(user), 0) >= settings.AI_SEMANTIC_FIT_DAILY_LIMIT


def _increment_daily_count(user) -> None:
    key = _daily_count_cache_key(user)
    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=DAILY_COUNT_CACHE_TTL_SECONDS)


def get_cached_semantic_fit(user, university: University) -> UniversitySemanticFit | None:
    """Returns the cached row only if still valid for the *current* profile
    snapshot, university data, and prompt version. A row that exists but no
    longer matches (profile changed, university re-imported, prompt changed)
    is treated as absent here -- callers report that as "missing", never as
    a silently-outdated "cached" result. The row itself isn't deleted; the
    next refresh overwrites it in place.
    """

    try:
        record = UniversitySemanticFit.objects.get(user=user, university=university)
    except UniversitySemanticFit.DoesNotExist:
        return None
    current_hash = compute_profile_snapshot_hash(user)
    if (
        record.profile_snapshot_hash != current_hash
        or record.university_updated_at != university.updated_at
        or record.prompt_version != PROMPT_VERSION
    ):
        return None
    return record


def semantic_fit_status(user, university: University) -> tuple[str, UniversitySemanticFit | None]:
    """Read-only status check -- never calls AI. Used by GET .../fit/, which
    must stay fast and must never block on a provider call."""

    record = get_cached_semantic_fit(user, university)
    if record is None:
        return "missing", None
    if record.status == UniversitySemanticFit.Status.FAILED:
        return "failed", record
    return "cached", record


def build_fit_response(
    deterministic_fit: dict,
    status_value: str,
    semantic_record: UniversitySemanticFit | None,
) -> dict:
    if status_value == "cached" and semantic_record is not None:
        semantic_fit = {
            "summary": semantic_record.summary,
            "main_strength": semantic_record.main_strength,
            "main_risk": semantic_record.main_risk,
            "next_actions": semantic_record.next_actions,
        }
        main_strength = semantic_record.main_strength
        main_risk = semantic_record.main_risk
        last_updated = semantic_record.updated_at
    else:
        # No cached semantic explanation yet (or the last attempt failed) --
        # fall back to the deterministic strengths/risks the frontend already
        # knows how to render, so the page never has an empty "why" section.
        semantic_fit = None
        main_strength = next(iter(deterministic_fit.get("strengths") or []), None)
        main_risk = next(iter(deterministic_fit.get("risks") or []), None)
        last_updated = None

    return {
        **deterministic_fit,
        "tier": map_tier(deterministic_fit.get("category")),
        "deterministic_fit": deterministic_fit,
        "semantic_fit": semantic_fit,
        "semantic_fit_status": status_value,
        "main_strength": main_strength,
        "main_risk": main_risk,
        "last_updated": last_updated,
    }


def _build_prompts(deterministic_fit: dict, university: University) -> tuple[str, str]:
    # Deliberately compact and already-computed: only the structured fit
    # result plus the university's public name -- never the student's raw
    # profile or the university's full catalogue row, so there is nothing
    # here for the model to leak or invent facts from.
    compact = {
        "university_name": university.name,
        "category": deterministic_fit.get("category"),
        "fit_score": deterministic_fit.get("fit_score"),
        "confidence": deterministic_fit.get("confidence"),
        "subscores": deterministic_fit.get("subscores"),
        "strengths": deterministic_fit.get("strengths"),
        "risks": deterministic_fit.get("risks"),
        "missing_fields": (deterministic_fit.get("missing_fields") or [])[:5],
    }
    user_prompt = (
        "Deterministic fit result (already computed, do not recompute or contradict it):\n"
        f"{json.dumps(compact, sort_keys=True)}\n\n"
        "Return JSON with exactly these keys: main_strength (one short phrase), "
        "main_risk (one short phrase), summary (1-2 sentences), next_actions "
        f"(up to {MAX_NEXT_ACTIONS} short action strings)."
    )
    return SEMANTIC_FIT_SYSTEM_PROMPT, user_prompt


class SemanticFitValidationError(Exception):
    pass


_FORBIDDEN_TOKENS = ("%", "percent", "guarantee", "guaranteed", "chance of", "odds of")


def _validate_and_normalize(output: object) -> dict:
    if not isinstance(output, dict):
        raise SemanticFitValidationError("Response must be a JSON object.")
    for field in ("main_strength", "main_risk", "summary"):
        value = output.get(field)
        if not isinstance(value, str) or not value.strip():
            raise SemanticFitValidationError(f"{field} must be a non-empty string.")
    next_actions = output.get("next_actions")
    if not isinstance(next_actions, list) or not all(isinstance(item, str) for item in next_actions):
        raise SemanticFitValidationError("next_actions must be a list of strings.")

    combined = " ".join([output["main_strength"], output["main_risk"], output["summary"]]).lower()
    if any(token in combined for token in _FORBIDDEN_TOKENS):
        raise SemanticFitValidationError("Response must not include a probability or guarantee.")

    return {
        "main_strength": output["main_strength"].strip()[:300],
        "main_risk": output["main_risk"].strip()[:300],
        "summary": output["summary"].strip()[:600],
        "next_actions": [item.strip() for item in next_actions if item.strip()][:MAX_NEXT_ACTIONS],
    }


def _store_result(
    user, university: University, profile_hash: str, *, status: str, normalized: dict | None,
    provider: str = "", model: str = "",
) -> UniversitySemanticFit:
    defaults = {
        "profile_snapshot_hash": profile_hash,
        "university_updated_at": university.updated_at,
        "prompt_version": PROMPT_VERSION,
        "status": status,
        "model_provider": provider,
        "model_name": model,
    }
    if normalized is not None:
        defaults.update(
            main_strength=normalized["main_strength"],
            main_risk=normalized["main_risk"],
            summary=normalized["summary"],
            next_actions=normalized["next_actions"],
        )
    record, _created = UniversitySemanticFit.objects.update_or_create(
        user=user, university=university, defaults=defaults
    )
    return record


def refresh_semantic_fit(user, university: University, *, client=None) -> dict:
    """Times and logs every refresh attempt through the shared AI-call
    registry, then delegates to `_refresh_semantic_fit_impl`. Never logs the
    profile, prompt, or AI output text -- only IDs/status/timing.

    Returns {"reason": ..., "record": UniversitySemanticFit | None}. Reason
    is one of: "cached" (already valid, no call made), "ai_unavailable",
    "daily_limit_reached", "validation_failed" (rejected twice, stored as
    failed), or "refreshed" (stored a new OK result).
    """

    started_at = time.monotonic()
    result = _refresh_semantic_fit_impl(user, university, client=client)
    duration_ms = int((time.monotonic() - started_at) * 1000)
    log_ai_call(
        logger,
        task_type="semantic_university_fit",
        provider="gemini",
        model=settings.AI_SEMANTIC_FIT_MODEL,
        status=result["reason"],
        cache_hit=result["reason"] == "cached",
        duration_ms=duration_ms,
        user_id=user.id,
        university_id=university.id,
    )
    return result


def _log_provider_error(model_name: str, user_id: int, university_id: int, error) -> None:
    logger.warning(
        "Gemini provider error feature=semantic_university_fit model=%s user_id=%s university_id=%s "
        'exception=%s message="%s"',
        model_name,
        user_id,
        university_id,
        type(error).__name__,
        str(error)[:500],
    )


def _refresh_semantic_fit_impl(user, university: University, *, client=None) -> dict:
    cached = get_cached_semantic_fit(user, university)
    if cached is not None:
        return {"reason": "cached", "record": cached}

    if not semantic_fit_ai_available():
        return {"reason": "ai_unavailable", "record": None}

    if _daily_limit_reached(user):
        return {"reason": "daily_limit_reached", "record": None}

    from services.user_profile_service.services import ensure_profile_records

    profile_hash = compute_profile_snapshot_hash(user)
    profile, _preferences = ensure_profile_records(user)
    deterministic_fit = calculate_university_fit(profile, university)
    system_prompt, user_prompt = _build_prompts(deterministic_fit, university)
    fit_client = client or GeminiSemanticFitClient()

    try:
        output = fit_client.generate_semantic_fit(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_schema=SEMANTIC_FIT_RESPONSE_SCHEMA,
        )
        normalized = _validate_and_normalize(output)
    except (AIProviderError, AIProviderUnavailable) as error:
        _log_provider_error(fit_client.model_name, user.id, university.id, error)
        record = _store_result(
            user, university, profile_hash, status=UniversitySemanticFit.Status.FAILED, normalized=None
        )
        return {"reason": "ai_unavailable", "record": record}
    except SemanticFitValidationError as first_error:
        logger.warning(
            'Gemini schema validation error feature=semantic_university_fit model=%s message="%s"',
            fit_client.model_name,
            str(first_error)[:300],
        )
        try:
            repaired_prompt = (
                f"{user_prompt}\n\nYour previous response was rejected for this reason: "
                f"{first_error}. Return corrected JSON that strictly matches the required keys."
            )
            output = fit_client.generate_semantic_fit(
                system_prompt=system_prompt,
                user_prompt=repaired_prompt,
                response_schema=SEMANTIC_FIT_RESPONSE_SCHEMA,
            )
            normalized = _validate_and_normalize(output)
        except (AIProviderError, AIProviderUnavailable) as error:
            _log_provider_error(fit_client.model_name, user.id, university.id, error)
            record = _store_result(
                user, university, profile_hash, status=UniversitySemanticFit.Status.FAILED, normalized=None
            )
            return {"reason": "ai_unavailable", "record": record}
        except SemanticFitValidationError:
            logger.warning(
                "Semantic fit validation failed twice feature=semantic_university_fit model=%s "
                "user_id=%s university_id=%s",
                fit_client.model_name,
                user.id,
                university.id,
            )
            record = _store_result(
                user, university, profile_hash, status=UniversitySemanticFit.Status.FAILED, normalized=None
            )
            return {"reason": "validation_failed", "record": record}

    _increment_daily_count(user)
    record = _store_result(
        user,
        university,
        profile_hash,
        status=UniversitySemanticFit.Status.OK,
        normalized=normalized,
        provider=fit_client.provider_name,
        model=fit_client.model_name,
    )
    return {"reason": "refreshed", "record": record}
