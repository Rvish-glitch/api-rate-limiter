from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.services.rate_limit_service import RateLimitService
from app.utils.datetime_utils import current_time_ms
from app.utils.network import get_client_ip
from app.utils.security import JWTError, decode_access_token


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limit_service: RateLimitService | None = None):
        super().__init__(app)
        self.rate_limit_service = rate_limit_service or RateLimitService()
        self.window_seconds = settings.RATE_LIMIT_WINDOW_SECONDS
        self.register_limit = 5
        self.token_limit = 10
        self.default_request_limit = 60
        self.skipped_prefixes = (
            "/docs",
            "/openapi.json",
            "/redoc",
            "/api/v1/system/health",
        )

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith(self.skipped_prefixes):
            return await call_next(request)

        client_ip = get_client_ip(request)
        path = request.url.path

        if path in ("/api/v1/auth/register", "/auth/register"):
            key_suffix = f"register:{client_ip}"
            max_requests = self.register_limit
        elif path in ("/api/v1/auth/tokens", "/auth/token"):
            key_suffix = f"tokens:{client_ip}"
            max_requests = self.token_limit
        else:
            client_id, tier = self._extract_client_info_from_token(request)
            tier_limit = settings.rate_limits_by_tier.get(tier, self.default_request_limit)
            key_suffix = f"request:{client_ip}:{client_id}"
            max_requests = tier_limit

        allowed, current_count, retry_after = self.rate_limit_service.check_and_increment(
            key_suffix=key_suffix,
            max_requests=max_requests,
            window_seconds=self.window_seconds,
        )

        now_epoch = int(current_time_ms() / 1000)
        reset_epoch = now_epoch + (retry_after if not allowed else self.window_seconds)

        if not allowed:
            headers = {
                "X-RateLimit-Limit": str(max_requests),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_epoch),
                "Retry-After": str(retry_after),
            }
            return JSONResponse(
                status_code=429,
                headers=headers,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please wait before retrying.",
                        "details": {
                            "limit": max_requests,
                            "window_seconds": self.window_seconds,
                            "retry_after_seconds": retry_after,
                        },
                    }
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, max_requests - current_count))
        response.headers["X-RateLimit-Reset"] = str(reset_epoch)
        return response

    def _extract_client_info_from_token(self, request: Request) -> tuple[str, str]:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return ("anonymous", "basic")

        token = auth_header.split(" ", 1)[1].strip()
        try:
            payload = decode_access_token(
                token,
                secret_key=settings.JWT_SECRET_KEY,
                algorithm=settings.JWT_ALGORITHM,
            )
            client_id = str(payload.get("sub") or payload.get("name") or "anonymous")
            tier = str(payload.get("tier") or "basic").lower()
            return (client_id, tier)
        except (JWTError, Exception):
            return ("anonymous", "basic")
