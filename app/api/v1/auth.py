from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies.services import get_auth_service, get_client_service
from app.schemas.auth import TokenResponse
from app.schemas.client import ClientRegisterRequest, ClientResponse
from app.services.auth_service import AuthService
from app.services.client_service import ClientService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new client",
)
def register(
    payload: ClientRegisterRequest,
    client_service: ClientService = Depends(get_client_service),
):
    """Register a new client identity with a specified access tier."""
    return client_service.register_client(payload)


@router.post(
    "/tokens",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Issue an OAuth2 access token",
)
def issue_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Authenticate client credentials and issue a signed Bearer token."""
    access_token = auth_service.issue_token(form_data.username, form_data.password)
    return TokenResponse(access_token=access_token)

