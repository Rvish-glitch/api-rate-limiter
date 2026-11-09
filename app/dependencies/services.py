from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.services.audit_service import AuditService
from app.services.auth_service import AuthService
from app.services.client_service import ClientService
from app.services.rate_limit_service import RateLimitService
from app.services.route_service import RouteService

# Singleton instance of RateLimitService across requests
_rate_limit_service_instance = RateLimitService()


def get_client_service(db: Session = Depends(get_db)) -> ClientService:
    return ClientService(db)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_rate_limit_service() -> RateLimitService:
    return _rate_limit_service_instance


def get_route_service(db: Session = Depends(get_db)) -> RouteService:
    return RouteService(db)


def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    return AuditService(db)

