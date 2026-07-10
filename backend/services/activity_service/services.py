"""Analytics event tracking.

`track_event()` is the only supported way to write an AnalyticsEvent: it
caps every metadata string so a caller can never accidentally leak a full
essay draft, profile dump, or secret into analytics storage. Callers still
choose what to pass -- this is a safety net, not a substitute for passing
minimal metadata in the first place.
"""

from __future__ import annotations

import logging

from .models import AnalyticsEvent

logger = logging.getLogger(__name__)

MAX_METADATA_STRING_LENGTH = 200


def _sanitize_metadata(metadata: dict | None) -> dict:
    if not metadata:
        return {}
    sanitized = {}
    for key, value in metadata.items():
        if isinstance(value, str) and len(value) > MAX_METADATA_STRING_LENGTH:
            sanitized[key] = value[:MAX_METADATA_STRING_LENGTH]
        elif isinstance(value, (str, int, float, bool)) or value is None:
            sanitized[key] = value
        # Nested dicts/lists/objects are dropped: analytics metadata must
        # stay flat and small, never a vehicle for a full profile/essay dump.
    return sanitized


def track_event(
    *,
    user=None,
    event_type: str,
    entity_type: str = "",
    entity_id: int | None = None,
    metadata: dict | None = None,
) -> AnalyticsEvent | None:
    try:
        return AnalyticsEvent.objects.create(
            user=user if user is not None and user.is_authenticated else None,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata=_sanitize_metadata(metadata),
        )
    except Exception:
        # Analytics is best-effort and must never break the request it's
        # attached to (e.g. a profile save should succeed even if the
        # analytics write somehow fails).
        logger.warning("Failed to record analytics event %s", event_type, exc_info=True)
        return None
