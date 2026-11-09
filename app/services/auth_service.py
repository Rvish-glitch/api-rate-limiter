from datetime import timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.client import Client
from app.services.client_service import ClientService
from app.utils.security import create_access_token, verify_secret


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.client_service = ClientService(db)

    def authenticate_client(self, username: str, secret: str) -> Optional[Client]:
        client = self.client_service.get_by_name(username)
        if not client or not verify_secret(secret, client.jwt_secret):
            return None
        return client

    def issue_token(self, username: str, secret: str) -> str:
        client = self.authenticate_client(username, secret)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid client credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_data = {
            "sub": str(client.id),
            "name": client.name,
            "tier": client.tier,
        }
        expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_access_token(
            data=token_data,
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            expires_delta=expires,
        )

