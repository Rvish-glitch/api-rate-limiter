from fastapi import APIRouter, Depends, FastAPI

from app.auth_router import get_current_client, router as auth_router
from app import database
from app.authorization import require_tier
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


@protected_router.get("/me")
def read_me(current_client=Depends(get_current_client)):
    return {"id": current_client.id, "name": current_client.name, "tier": current_client.tier}


@protected_router.get("/admin/health")
def admin_health(current_client=Depends(require_tier("admin"))):
    return {"status": "ok", "message": f"Welcome admin {current_client.name}"}


app.include_router(protected_router)
