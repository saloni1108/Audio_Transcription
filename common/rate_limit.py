import time

from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import redis

_pool = None

def _client():
    global _pool
    if _pool is None:
        _pool = redis.Redis.from_url(settings.REDIS_URL)
    return _pool

class RateLimitMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith("/api/") and request.method in {"GET","POST","PUT","PATCH","DELETE"}:
            user = getattr(request, "user", None)
            ident = "anon"
            if user and user.is_authenticated:
                ident = f"user:{user.id}"
            else:
                # allow auth endpoints without token
                if request.path.startswith("/api/v1/auth/"):
                    return None
                ident = f"ip:{request.META.get('REMOTE_ADDR','unknown')}"
            key = f"ratelimit:{ident}:{int(time.time()//60)}"
            r = _client()
            cur = r.incr(key)
            if cur == 1:
                r.expire(key, 70)
            if cur > settings.RATE_LIMIT_RPM:
                return JsonResponse({"detail":"rate limit exceeded"}, status=429)
        return None
