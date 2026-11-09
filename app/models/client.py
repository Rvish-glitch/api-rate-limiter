from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    tier = Column(String, nullable=False, default="basic")
    jwt_secret = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    api_logs = relationship("APILog", back_populates="client", cascade="all, delete-orphan")

