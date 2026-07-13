from rest_framework.throttling import ScopedRateThrottle


class ScopedIPRateThrottle(ScopedRateThrottle):
    """Use a view's scoped rate as an independent client-IP limit."""

    def get_cache_key(self, request, view):
        if not self.scope:
            return None
        return self.cache_format % {
            "scope": f"{self.scope}:ip",
            "ident": self.get_ident(request),
        }
