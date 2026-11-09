from fastapi import APIRouter, Depends, status

from app.core.database import check_db_health
from app.core.redis_client import check_redis_health
from app.dependencies.auth import require_tier
from app.dependencies.services import get_audit_service, get_client_service, get_route_service
from app.models.client import Client
from app.schemas.common import HealthResponse, MetricsResponse
from app.services.audit_service import AuditService
from app.services.client_service import ClientService
from app.services.route_service import RouteService

router = APIRouter(prefix="/system", tags=["System"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Gateway health check",
)
def health_check():
    """Verify that database and Redis connections are responsive."""
    db_ok = check_db_health()
    redis_ok = check_redis_health()
    overall = "ok" if (db_ok and redis_ok) else "degraded"
    return HealthResponse(
        status=overall,
        database=db_ok,
        redis=redis_ok,
    )


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Gateway operational metrics (Admin only)",
)
def metrics(
    client_service: ClientService = Depends(get_client_service),
    route_service: RouteService = Depends(get_route_service),
    audit_service: AuditService = Depends(get_audit_service),
    _: Client = Depends(require_tier("admin")),
):
    """Inspect core gateway metrics and inventory counters (Admin access required)."""
    return MetricsResponse(
        status="ok",
        active_routes_count=route_service.count_routes(),
        blocked_ips_count=audit_service.count_blocked_ips(),
        total_clients_count=client_service.count_clients(),
    )

