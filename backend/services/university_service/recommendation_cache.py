"""Short-TTL cache for the (fairly expensive, full-catalog-scanning)
recommendations and strategy views (PERFORMANCE-011 PART 7).

The TTL is deliberately short (seconds, not minutes): both responses embed
per-university "already shortlisted" / "already tracked" flags that must
reflect the user's *own* very-recent actions, so this cache exists to
absorb near-duplicate requests (e.g. Dashboard and the Recommendations page
both loading within the same few seconds), not to serve minutes-old data.
Shortlist/application-tracking actions explicitly bust it (see
`invalidate_recommendation_caches`) so a user never sees their own action
reflected late because of this cache.

Cache key includes `profile_hash` (not just user_id): a profile edit changes
the hash, which is a *different* cache key -- so a stale entry is never
served after a profile change, it's simply never looked up again.

Uses a local (lazy) import of `compute_profile_snapshot_hash` to avoid a
module-level import cycle between `university_service` and
`profile_assessment_service` (the same defensive pattern already used
elsewhere in `university_service.services`).
"""

from __future__ import annotations

from django.core.cache import cache

RECOMMENDATIONS_CACHE_SECONDS = 20
STRATEGY_CACHE_SECONDS = 20


def _profile_hash(user) -> str:
    from services.profile_assessment_service.services import compute_profile_snapshot_hash

    return compute_profile_snapshot_hash(user)


def recommendations_cache_key(user) -> str:
    return f"university-recommendations:{user.id}:{_profile_hash(user)}"


def strategy_cache_key(user) -> str:
    return f"university-strategy:{user.id}:{_profile_hash(user)}"


def invalidate_recommendation_caches(user) -> None:
    """Call from any action that changes shortlist/application-tracking
    state for this user, so recommendations/strategy reflect it immediately
    instead of waiting out the short TTL above.
    """

    cache.delete(recommendations_cache_key(user))
    cache.delete(strategy_cache_key(user))
