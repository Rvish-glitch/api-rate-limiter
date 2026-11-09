from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.route import Route
from app.schemas.route import RouteCreateRequest


class RouteService:
    def __init__(self, db: Session):
        self.db = db

    def list_routes(self, active_only: bool = True) -> List[Route]:
        query = self.db.query(Route)
        if active_only:
            query = query.filter(Route.is_active == True)
        return query.all()

    def get_by_id(self, route_id: int) -> Optional[Route]:
        return self.db.query(Route).filter(Route.id == route_id).first()

    def get_by_path(self, path: str) -> Optional[Route]:
        return self.db.query(Route).filter(Route.path == path).first()

    def count_routes(self) -> int:
        return self.db.query(Route).filter(Route.is_active == True).count()

    def create_route(self, payload: RouteCreateRequest) -> Route:
        existing = self.get_by_path(payload.path)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Route path '{payload.path}' is already registered",
            )

        route = Route(
            path=payload.path,
            destination_url=payload.destination_url,
            is_active=payload.is_active,
        )
        self.db.add(route)
        self.db.commit()
        self.db.refresh(route)
        return route

    def delete_route(self, route_id: int) -> bool:
        route = self.get_by_id(route_id)
        if not route:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Route ID {route_id} not found",
            )
        self.db.delete(route)
        self.db.commit()
        return True

