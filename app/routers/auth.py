from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_secret, verify_secret
from app.database import get_db
from app.models.models import Client
from app.schemas import ClientRegisterRequest, ClientResponse, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=ClientResponse)
def register_client(payload: ClientRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(Client).filter(Client.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client name already exists")

    client = Client(
        name=payload.name,
        tier=payload.tier,
        jwt_secret=hash_secret(payload.secret),
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.post("/token", response_model=TokenResponse)
def issue_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.name == form_data.username).first()
    if not client or not verify_secret(form_data.password, client.jwt_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(client_id=client.id, client_name=client.name)
    return TokenResponse(access_token=access_token)
