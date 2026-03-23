from fastapi import APIRouter, Depends, FastAPI

from app.auth_router import get_current_client, router as auth_router
from app import database
from app.models.models import Base

app = FastAPI()


@app.on_event("startup")
def startup_event():
    database.initialize_database()
    Base.metadata.create_all(bind=database.engine)


app.include_router(auth_router)

protected_router = APIRouter(dependencies=[Depends(get_current_client)])


@protected_router.get("/")
def read_root():
    return {"hyy bro ,it is still in development"}


app.include_router(protected_router)
