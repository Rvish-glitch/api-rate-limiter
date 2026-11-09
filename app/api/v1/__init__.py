from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.blocked_ips import router as blocked_ips_router
from app.api.v1.clients import router as clients_router
from app.api.v1.rate_limits import router as rate_limits_router
from app.api.v1.routes import router as routes_router
from app.api.v1.system import router as system_router

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(auth_router)
v1_router.include_router(clients_router)
v1_router.include_router(rate_limits_router)
v1_router.include_router(routes_router)
v1_router.include_router(blocked_ips_router)
v1_router.include_router(system_router)

__all__ = ["v1_router"]

