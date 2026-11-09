from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class RouteCreateRequest(BaseModel):
    path: str = Field(..., description="Route pattern or path prefix, e.g. /v1/billing")
    destination_url: str = Field(..., description="Target upstream URL, e.g. http://billing-service:8080")
    is_active: bool = Field(default=True)


class RouteResponse(BaseModel):
    id: int
    path: str
    destination_url: str
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

