from fastapi import APIRouter, Depends, Request, status

from app.core.config import settings
from app.dependencies.auth import get_current_client, require_tier
from app.dependencies.services import get_rate_limit_service
from app.models.client import Client
from app.schemas.rate_limit import RateLimitPoliciesResponse, RateLimitStatusResponse
from app.services.rate_limit_service import RateLimitService
from app.utils.network import get_client_ip

router = APIRouter(prefix="/rate-limits", tags=["Rate Limiting"])


@router.get(
    "/status",
    response_model=RateLimitStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current client rate limit status",
)
def get_rate_limit_status(
    request: Request,
    current_client: Client = Depends(get_current_client),
    rate_limit_service: RateLimitService = Depends(get_rate_limit_service),
):
    """Inspect current quota consumption, remaining tokens, and reset timestamp."""
    client_ip = get_client_ip(request)
    return rate_limit_service.get_client_quota(current_client, client_ip)


@router.get(
    "/policies",
    response_model=RateLimitPoliciesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get active rate limit policies (Admin only)",
)
def get_rate_limit_policies(
    _: Client = Depends(require_tier("admin")),
):
    """Inspect active rate limit configuration per tier (Admin access required)."""
    return RateLimitPoliciesResponse(
        window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
        tier_limits=settings.rate_limits_by_tier,
    )

