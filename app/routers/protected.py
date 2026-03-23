from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_client, require_tier

router = APIRouter(dependencies=[Depends(get_current_client)], tags=["Protected"])


@router.get("/")
def read_root():
    return {"hyy bro ,it is still in development"}


@router.get("/me")
def read_me(current_client=Depends(get_current_client)):
    return {"id": current_client.id, "name": current_client.name, "tier": current_client.tier}


@router.get("/admin/health")
def admin_health(current_client=Depends(require_tier("admin"))):
    return {"status": "ok", "message": f"Welcome admin {current_client.name}"}
