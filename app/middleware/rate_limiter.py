import time
import uuid
from threading import Lock

from fastapi import Request
from fastapi.responses import JSONResponse
from redis import Redis
from redis.exceptions import RedisError
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import RATE_LIMIT_WINDOW_SECONDS
from app.core.redis_client import get_redis_client
from app.core.security import JWTError, decode_access_token


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_client: Redis | None = None):
        super().__init__(app)
        self.redis = redis_client or get_redis_client()
        self.window_seconds = RATE_LIMIT_WINDOW_SECONDS
        self.window_ms = self.window_seconds * 1000
        self._fallback_lock = Lock()
        self._fallback_events: dict[str, list[int]] = {}
        self.register_limit = 2
        self.token_limit = 3
        self.request_limit = 5
        self.skipped_prefixes = (
            "/docs",
            "/openapi.json",
            "/redoc",
        )

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith(self.skipped_prefixes):
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        if request.url.path == "/auth/register":
            key_suffix = f"register:{client_ip}"
            max_requests = self.register_limit
            scope = "register"
        elif request.url.path == "/auth/token":
            key_suffix = f"token:{client_ip}"
            max_requests = self.token_limit
            scope = "token"
        else:
            username = self._extract_username_from_request(request)
            key_suffix = f"request:{client_ip}:{username}"
            max_requests = self.request_limit
            scope = "request"

        try:
            allowed, current_count = self._check_and_increment_by_key(key_suffix, max_requests)
        except RedisError:
            allowed, current_count = self._fallback_check_and_increment_by_key(key_suffix, max_requests)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too Many Requests",
                    "scope": scope,
                    "limit": max_requests,
                    "window_seconds": self.window_seconds,
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, max_requests - current_count))
        response.headers["X-RateLimit-Window"] = str(self.window_seconds)
        return response

    def _check_and_increment_by_key(self, key_suffix: str, max_requests: int) -> tuple[bool, int]:
        key = f"rate_limit:{key_suffix}"
        now_ms = int(time.time() * 1000)
        window_start = now_ms - self.window_ms

        pipeline = self.redis.pipeline(transaction=True)
        pipeline.zremrangebyscore(key, 0, window_start)
        pipeline.zcard(key)
        _, current_count = pipeline.execute()

        if current_count >= max_requests:
            return False, int(current_count)

        member = f"{now_ms}-{uuid.uuid4()}"
        pipeline = self.redis.pipeline(transaction=True)
        pipeline.zadd(key, {member: now_ms})
        pipeline.expire(key, self.window_seconds + 1)
        pipeline.execute()
        return True, int(current_count) + 1

    def _fallback_check_and_increment_by_key(self, key_suffix: str, max_requests: int) -> tuple[bool, int]:
        now_ms = int(time.time() * 1000)
        window_start = now_ms - self.window_ms
        with self._fallback_lock:
            events = self._fallback_events.get(key_suffix, [])
            events = [event for event in events if event > window_start]
            if len(events) >= max_requests:
                self._fallback_events[key_suffix] = events
                return False, len(events)
            events.append(now_ms)
            self._fallback_events[key_suffix] = events
            return True, len(events)

    def _extract_username_from_request(self, request: Request) -> str:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return "anonymous"
        token = auth_header.split(" ", 1)[1].strip()
        try:
            payload = decode_access_token(token)
            return str(payload.get("name") or payload.get("sub") or "anonymous")
        except (JWTError, TypeError, ValueError):
            return "anonymous"

    def _get_client_ip(self, request: Request) -> str:
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        if request.client and request.client.host:
            return request.client.host
        return "unknown"
