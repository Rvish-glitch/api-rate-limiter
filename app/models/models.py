# Re-export models for backward compatibility
from app.models.api_log import APILog
from app.models.base import Base
from app.models.client import Client
from app.models.blocked_ip import BlockedIP
from app.models.route import Route

__all__ = ["Base", "Client", "APILog", "BlockedIP", "Route"]
