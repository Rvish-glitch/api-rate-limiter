from pydantic import BaseModel, ConfigDict


class ClientRegisterRequest(BaseModel):
    name: str
    tier: str
    secret: str


class ClientResponse(BaseModel):
    id: int
    name: str
    tier: str

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
