from typing import List
from fastapi import APIRouter, Depends, Response, status

from app.dependencies.auth import require_tier
from app.dependencies.services import get_audit_service
from app.models.client import Client
from app.schemas.blocked_ip import BlockedIPCreateRequest, BlockedIPResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/blocked-ips", tags=["Access Control"])


@router.get(
    "",
    response_model=List[BlockedIPResponse],
    status_code=status.HTTP_200_OK,
    summary="List blocked IP addresses (Admin only)",
)
def list_blocked_ips(
    audit_service: AuditService = Depends(get_audit_service),
    _: Client = Depends(require_tier("admin")),
):
    """Retrieve all active blocked IP entries (Admin access required)."""
    return audit_service.list_blocked_ips(active_only=True)


@router.post(
    "",
    response_model=BlockedIPResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Block an IP address (Admin only)",
)
def block_ip(
    payload: BlockedIPCreateRequest,
    audit_service: AuditService = Depends(get_audit_service),
    _: Client = Depends(require_tier("admin")),
):
    """Add or activate an IP address in the blocklist (Admin access required)."""
    return audit_service.block_ip(payload)


@router.delete(
    "/{ip_address}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unblock an IP address (Admin only)",
)
def unblock_ip(
    ip_address: str,
    audit_service: AuditService = Depends(get_audit_service),
    _: Client = Depends(require_tier("admin")),
):
    """Deactivate a blocked IP address (Admin access required)."""
    audit_service.unblock_ip(ip_address)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

