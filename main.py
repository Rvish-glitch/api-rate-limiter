from fastapi import FastAPI

from app import database
from app.models.models import Base
from app.routers.auth import router as auth_router
from app.routers.protected import router as protected_router

app = FastAPI()


@app.on_event("startup")
def startup_event():
    database.initialize_database()
    Base.metadata.create_all(bind=database.engine)


app.include_router(auth_router)
app.include_router(protected_router)
