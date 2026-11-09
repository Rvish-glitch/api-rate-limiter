from typing import Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.dependencies.database import get_db
from app.models.client import Client
from app.services.client_service import ClientService
from app.utils.security import JWTError, decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/tokens")


def get_current_client(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Client:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        if token.lower().startswith("bearer "):
            token = token.split(" ", 1)[1].strip()
        payload = decode_access_token(
            token,
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        client_id: str | None = payload.get("sub")
        if client_id is None:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    client_service = ClientService(db)
    client = client_service.get_by_id(int(client_id))
    if client is None:
        raise credentials_exception
    return client


def require_tier(*allowed_tiers: str) -> Callable[[Client], Client]:
    normalized_allowed = {tier.lower() for tier in allowed_tiers}

    def dependency(current_client: Client = Depends(get_current_client)) -> Client:
        if current_client.tier.lower() not in normalized_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: requires one of the following tiers: {', '.join(sorted(normalized_allowed))}",
            )
        return current_client

    return dependency
