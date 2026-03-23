from datetime import datetime, timedelta, timezone

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_secret(secret: str) -> str:
    return pwd_context.hash(secret)


def verify_secret(plain_secret: str, hashed_secret: str) -> bool:
    return pwd_context.verify(plain_secret, hashed_secret)


def create_access_token(client_id: int, client_name: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(client_id), "name": client_name, "exp": expire}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])


__all__ = [
    "oauth2_scheme",
    "hash_secret",
    "verify_secret",
    "create_access_token",
    "decode_access_token",
    "JWTError",
]
