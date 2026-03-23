from typing import Literal

from pydantic import BaseModel, ConfigDict

Tier = Literal["basic", "premium", "admin"]


class ClientRegisterRequest(BaseModel):
    name: str
    tier: Tier
    secret: str


class ClientResponse(BaseModel):
    id: int
    name: str
    tier: Tier

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
