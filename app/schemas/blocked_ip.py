from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class BlockedIPCreateRequest(BaseModel):
    ip_address: str = Field(..., description="IP address or CIDR range to block")
    reason: Optional[str] = Field(None, description="Reason for blocking the IP")


class BlockedIPResponse(BaseModel):
    id: int
    ip_address: str
    blocked_at: datetime
    reason: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

