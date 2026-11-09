import uuid
from threading import Lock
from typing import Dict, Tuple

from redis import Redis
from redis.exceptions import RedisError

from app.core.config import settings
from app.core.redis_client import get_redis_client
from app.models.client import Client
from app.utils.datetime_utils import calculate_window_start_ms, current_time_ms


class RateLimitService:
    def __init__(self, redis_client: Redis | None = None):
        self.redis = redis_client or get_redis_client()
        self.window_seconds = settings.RATE_LIMIT_WINDOW_SECONDS
        self._fallback_lock = Lock()
        self._fallback_events: Dict[str, list[int]] = {}
        self._redis_down_until: int = 0

    def check_and_increment(
        self,
        key_suffix: str,
        max_requests: int,
        window_seconds: int | None = None,
    ) -> Tuple[bool, int, int]:
        """
        Check and increment request count in a sliding window.
        Returns: (is_allowed, current_count, retry_after_seconds)
        """
        window = window_seconds or self.window_seconds
        now_ms = current_time_ms()
        if now_ms < self._redis_down_until:
            return self._fallback_sliding_window(key_suffix, max_requests, window)

        try:
            return self._redis_sliding_window(key_suffix, max_requests, window)
        except (RedisError, Exception):
            # Mark Redis as down for 5 seconds to prevent stalling on timeouts
            self._redis_down_until = now_ms + 5000
            return self._fallback_sliding_window(key_suffix, max_requests, window)

    def _redis_sliding_window(
        self,
        key_suffix: str,
        max_requests: int,
        window_seconds: int,
    ) -> Tuple[bool, int, int]:
        key = f"rate_limit:{key_suffix}"
        now_ms = current_time_ms()
        window_start_ms = calculate_window_start_ms(now_ms, window_seconds)

        pipeline = self.redis.pipeline(transaction=True)
        pipeline.zremrangebyscore(key, 0, window_start_ms)
        pipeline.zcard(key)
        pipeline.zrange(key, 0, 0, withscores=True)
        _, current_count, oldest_items = pipeline.execute()

        current_count = int(current_count)

        if current_count >= max_requests:
            retry_after = 1
            if oldest_items:
                oldest_score = oldest_items[0][1]
                retry_after = max(1, int((oldest_score + (window_seconds * 1000) - now_ms) / 1000))
            return False, current_count, retry_after

        member = f"{now_ms}-{uuid.uuid4()}"
        pipeline = self.redis.pipeline(transaction=True)
        pipeline.zadd(key, {member: now_ms})
        pipeline.expire(key, window_seconds + 1)
        pipeline.execute()
        return True, current_count + 1, 0

    def _fallback_sliding_window(
        self,
        key_suffix: str,
        max_requests: int,
        window_seconds: int,
    ) -> Tuple[bool, int, int]:
        now_ms = current_time_ms()
        window_start_ms = calculate_window_start_ms(now_ms, window_seconds)

        with self._fallback_lock:
            events = self._fallback_events.get(key_suffix, [])
            valid_events = [ts for ts in events if ts > window_start_ms]

            if len(valid_events) >= max_requests:
                self._fallback_events[key_suffix] = valid_events
                oldest = min(valid_events) if valid_events else window_start_ms
                retry_after = max(1, int((oldest + (window_seconds * 1000) - now_ms) / 1000))
                return False, len(valid_events), retry_after

            valid_events.append(now_ms)
            self._fallback_events[key_suffix] = valid_events
            return True, len(valid_events), 0

    def get_client_quota(self, client: Client, client_ip: str) -> dict:
        tier_limit = settings.rate_limits_by_tier.get(client.tier.lower(), settings.RATE_LIMIT_BASIC)
        key_suffix = f"request:{client_ip}:{client.name}"
        key = f"rate_limit:{key_suffix}"
        now_ms = current_time_ms()
        window_start_ms = calculate_window_start_ms(now_ms, self.window_seconds)

        if now_ms < self._redis_down_until:
            with self._fallback_lock:
                events = [ts for ts in self._fallback_events.get(key_suffix, []) if ts > window_start_ms]
                current_count = len(events)
        else:
            try:
                self.redis.zremrangebyscore(key, 0, window_start_ms)
                current_count = int(self.redis.zcard(key))
            except Exception:
                self._redis_down_until = now_ms + 5000
                with self._fallback_lock:
                    events = [ts for ts in self._fallback_events.get(key_suffix, []) if ts > window_start_ms]
                    current_count = len(events)

        remaining = max(0, tier_limit - current_count)
        reset_epoch = int((now_ms + (self.window_seconds * 1000)) / 1000)

        return {
            "client_name": client.name,
            "tier": client.tier,
            "limit": tier_limit,
            "remaining": remaining,
            "window_seconds": self.window_seconds,
            "reset_epoch_seconds": reset_epoch,
        }

