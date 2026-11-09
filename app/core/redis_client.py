from redis import Redis
from redis.exceptions import RedisError

from app.core.config import settings

redis_client: Redis = Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=0.5,
    socket_timeout=0.5,
)


def get_redis_client() -> Redis:
    """Return the global Redis client instance."""
    return redis_client


def check_redis_health() -> bool:
    """Return True if Redis is reachable and responds to PING."""
    try:
        return bool(redis_client.ping())
    except (RedisError, Exception):
        return False
