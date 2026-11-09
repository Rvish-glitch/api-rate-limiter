from typing import List
from fastapi import APIRouter, Depends, Response, status

from app.dependencies.auth import require_tier
from app.dependencies.services import get_route_service
from app.models.client import Client
from app.schemas.route import RouteCreateRequest, RouteResponse
from app.services.route_service import RouteService

router = APIRouter(prefix="/routes", tags=["Gateway Routes"])


@router.get(
    "",
    response_model=List[RouteResponse],
    status_code=status.HTTP_200_OK,
    summary="List active upstream routes (Admin only)",
)
def list_routes(
    route_service: RouteService = Depends(get_route_service),
    _: Client = Depends(require_tier("admin")),
):
    """Retrieve all active proxy upstream routes (Admin access required)."""
    return route_service.list_routes(active_only=True)


@router.post(
    "",
    response_model=RouteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new upstream route (Admin only)",
)
def create_route(
    payload: RouteCreateRequest,
    route_service: RouteService = Depends(get_route_service),
    _: Client = Depends(require_tier("admin")),
):
    """Register a new upstream destination for gateway proxying (Admin access required)."""
    return route_service.create_route(payload)


@router.delete(
    "/{route_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an upstream route (Admin only)",
)
def delete_route(
    route_id: int,
    route_service: RouteService = Depends(get_route_service),
    _: Client = Depends(require_tier("admin")),
):
    """Remove an upstream route from the gateway registry (Admin access required)."""
    route_service.delete_route(route_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

