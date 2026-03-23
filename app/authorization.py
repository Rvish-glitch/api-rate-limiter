from fastapi import Depends, HTTPException, status

from app.auth_router import get_current_client
from app.models.models import Client


def require_tier(*allowed_tiers: str):
    allowed = {tier.lower() for tier in allowed_tiers}

    def dependency(current_client: Client = Depends(get_current_client)) -> Client:
        if current_client.tier.lower() not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires tier: {', '.join(sorted(allowed))}",
            )
        return current_client

    return dependency
