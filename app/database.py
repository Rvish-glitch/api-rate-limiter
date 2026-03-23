import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

def _build_engine(database_url: str):
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, pool_pre_ping=True, connect_args=connect_args)

engine = _build_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def initialize_database():
    global engine, DATABASE_URL
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except OperationalError:
        if DATABASE_URL.startswith("postgresql"):
            fallback_url = "sqlite:///./app.db"
            engine = _build_engine(fallback_url)
            SessionLocal.configure(bind=engine)
            DATABASE_URL = fallback_url


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
