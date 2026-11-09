from datetime import datetime, timedelta, timezone
from typing import Any, Mapping

from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_secret(secret: str) -> str:
    """Hash a raw secret using PBKDF2-SHA256."""
    return pwd_context.hash(secret)


def verify_secret(plain_secret: str, hashed_secret: str) -> bool:
    """Verify a plain secret against a stored PBKDF2-SHA256 hash."""
    return pwd_context.verify(plain_secret, hashed_secret)


def create_access_token(
    data: Mapping[str, Any],
    secret_key: str,
    algorithm: str = "HS256",
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token with an expiration timestamp."""
    to_encode = dict(data)
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=60)

    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def decode_access_token(token: str, secret_key: str, algorithm: str = "HS256") -> dict[str, Any]:
    """Decode and validate a JWT access token."""
    return jwt.decode(token, secret_key, algorithms=[algorithm])


__all__ = [
    "hash_secret",
    "verify_secret",
    "create_access_token",
    "decode_access_token",
    "JWTError",
]

