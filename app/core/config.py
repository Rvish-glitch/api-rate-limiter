import os

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-env")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
RATE_LIMITS_BY_TIER = {
	"basic": int(os.getenv("RATE_LIMIT_BASIC", "60")),
	"premium": int(os.getenv("RATE_LIMIT_PREMIUM", "300")),
	"admin": int(os.getenv("RATE_LIMIT_ADMIN", "1000")),
}
