# Legacy compatibility layer - prefer importing from app.core.database or app.dependencies.database
from app.core.database import SessionLocal, _build_engine, engine, initialize_database
from app.dependencies.database import get_db

__all__ = ["engine", "SessionLocal", "initialize_database", "get_db", "_build_engine"]
