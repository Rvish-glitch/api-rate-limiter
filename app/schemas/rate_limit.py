from typing import Dict
from pydantic import BaseModel, Field


class RateLimitStatusResponse(BaseModel):
    client_name: str
    tier: str
    limit: int = Field(..., description="Maximum allowed requests in the window")
    remaining: int = Field(..., description="Remaining requests in the current window")
    window_seconds: int = Field(..., description="Sliding window size in seconds")
    reset_epoch_seconds: int = Field(..., description="Epoch timestamp when current window resets")


class RateLimitPoliciesResponse(BaseModel):
    window_seconds: int
    tier_limits: Dict[str, int]

