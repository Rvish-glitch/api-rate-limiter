from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import JWTError, decode_access_token, oauth2_scheme
from app.database import get_db
from app.models.models import Client


def get_current_client(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Client:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        if token.lower().startswith("bearer "):
            token = token.split(" ", 1)[1].strip()
        payload = decode_access_token(token)
        client_id = payload.get("sub")
        if client_id is None:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    client = db.query(Client).filter(Client.id == int(client_id)).first()
    if client is None:
        raise credentials_exception
    return client


def require_tier(*allowed_tiers: str):
    allowed = {tier.lower() for tier in allowed_tiers}

    def dependency(current_client: Client = Depends(get_current_client)) -> Client:
        if current_client.tier.lower() not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires tier: {', '.join(sorted(allowed))}",
            )
        return current_client

    return dependency
