"""Shared 'AI call' log-line formatter (PERFORMANCE-011 PART 6).

Every AI-calling feature (profile assessment, essay scoring, semantic
university fit) times its own attempt and logs the same sanitized,
aggregate-only shape -- status, cache_hit, duration_ms, plus feature-specific
IDs/counts -- so `ai_task_type=` is greppable across every provider call in
one place. Never pass raw profile/essay/prompt text as an extra field here;
only IDs, counts, and enums are safe.

Takes the caller's own `logger` (rather than logging through one shared
logger instance) so each feature's existing `assertLogs("services.<app>...")`
tests keep working unchanged -- only the message formatting is centralized.
"""

from __future__ import annotations

import logging


def log_ai_call(
    logger: logging.Logger,
    *,
    task_type: str,
    provider: str,
    model: str,
    status: str,
    cache_hit: bool,
    duration_ms: int,
    **extra_fields: object,
) -> None:
    extra = "".join(f" {key}={value}" for key, value in extra_fields.items())
    logger.info(
        "AI call ai_task_type=%s provider=%s model=%s status=%s cache_hit=%s duration_ms=%s%s",
        task_type,
        provider,
        model,
        status,
        cache_hit,
        duration_ms,
        extra,
    )
