from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.client import Client
from app.schemas.client import ClientRegisterRequest
from app.utils.security import hash_secret


class ClientService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, client_id: int) -> Optional[Client]:
        return self.db.query(Client).filter(Client.id == client_id).first()

    def get_by_name(self, name: str) -> Optional[Client]:
        return self.db.query(Client).filter(Client.name == name).first()

    def list_clients(self, skip: int = 0, limit: int = 100) -> List[Client]:
        return self.db.query(Client).offset(skip).limit(limit).all()

    def count_clients(self) -> int:
        return self.db.query(Client).count()

    def register_client(self, payload: ClientRegisterRequest) -> Client:
        existing = self.get_by_name(payload.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Client '{payload.name}' already exists",
            )

        client = Client(
            name=payload.name,
            tier=payload.tier,
            jwt_secret=hash_secret(payload.secret),
        )
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client

