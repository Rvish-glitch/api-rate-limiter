from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

Tier = Literal["basic", "premium", "admin"]


class ClientRegisterRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="Unique client identifier")
    tier: Tier = Field(default="basic", description="Access tier: basic, premium, or admin")
    secret: str = Field(..., min_length=6, description="Client access secret / password")


class ClientResponse(BaseModel):
    id: int
    name: str
    tier: Tier
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ClientProfileResponse(BaseModel):
    id: int
    name: str
    tier: Tier
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

