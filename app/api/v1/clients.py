from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies.auth import get_current_client, require_tier
from app.dependencies.services import get_client_service
from app.models.client import Client
from app.schemas.client import ClientProfileResponse, ClientResponse
from app.services.client_service import ClientService

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.get(
    "/me",
    response_model=ClientProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Fetch current client profile",
)
def get_me(current_client: Client = Depends(get_current_client)):
    """Return identity and tier for the authenticated client."""
    return current_client


@router.get(
    "",
    response_model=List[ClientResponse],
    status_code=status.HTTP_200_OK,
    summary="List registered clients (Admin only)",
)
def list_clients(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    client_service: ClientService = Depends(get_client_service),
    _: Client = Depends(require_tier("admin")),
):
    """List registered clients with pagination (Admin access required)."""
    return client_service.list_clients(skip=skip, limit=limit)


@router.get(
    "/{client_id}",
    response_model=ClientResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve client by ID (Admin only)",
)
def get_client(
    client_id: int,
    client_service: ClientService = Depends(get_client_service),
    _: Client = Depends(require_tier("admin")),
):
    """Retrieve details of a specific client by ID (Admin access required)."""
    client = client_service.get_by_id(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found",
        )
    return client

