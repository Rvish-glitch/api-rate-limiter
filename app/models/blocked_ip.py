from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.models.base import Base


class BlockedIP(Base):
    __tablename__ = "blocked_ips"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, unique=True, nullable=False, index=True)
    blocked_at = Column(DateTime(timezone=True), server_default=func.now())
    reason = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

