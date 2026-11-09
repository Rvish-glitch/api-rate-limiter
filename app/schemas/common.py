from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class HealthResponse(BaseModel):
    status: str = "ok"
    database: bool
    redis: bool


class MetricsResponse(BaseModel):
    status: str = "ok"
    active_routes_count: int
    blocked_ips_count: int
    total_clients_count: int

