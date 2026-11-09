from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.api_log import APILog
from app.models.blocked_ip import BlockedIP
from app.schemas.blocked_ip import BlockedIPCreateRequest


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def list_blocked_ips(self, active_only: bool = True) -> List[BlockedIP]:
        query = self.db.query(BlockedIP)
        if active_only:
            query = query.filter(BlockedIP.is_active == True)
        return query.all()

    def is_ip_blocked(self, ip_address: str) -> bool:
        record = (
            self.db.query(BlockedIP)
            .filter(BlockedIP.ip_address == ip_address, BlockedIP.is_active == True)
            .first()
        )
        return record is not None

    def block_ip(self, payload: BlockedIPCreateRequest) -> BlockedIP:
        existing = (
            self.db.query(BlockedIP)
            .filter(BlockedIP.ip_address == payload.ip_address)
            .first()
        )
        if existing:
            if existing.is_active:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"IP address '{payload.ip_address}' is already blocked",
                )
            existing.is_active = True
            existing.reason = payload.reason
            self.db.commit()
            self.db.refresh(existing)
            return existing

        blocked = BlockedIP(
            ip_address=payload.ip_address,
            reason=payload.reason,
            is_active=True,
        )
        self.db.add(blocked)
        self.db.commit()
        self.db.refresh(blocked)
        return blocked

    def unblock_ip(self, ip_address: str) -> bool:
        record = (
            self.db.query(BlockedIP)
            .filter(BlockedIP.ip_address == ip_address, BlockedIP.is_active == True)
            .first()
        )
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blocked IP address '{ip_address}' not found",
            )
        record.is_active = False
        self.db.commit()
        return True

    def count_blocked_ips(self) -> int:
        return self.db.query(BlockedIP).filter(BlockedIP.is_active == True).count()

    def log_request(
        self,
        client_id: Optional[int],
        route: str,
        ip_address: str,
        status_code: int,
    ) -> APILog:
        log_entry = APILog(
            client_id=client_id,
            route=route,
            ip_address=ip_address,
            status_code=status_code,
        )
        self.db.add(log_entry)
        self.db.commit()
        self.db.refresh(log_entry)
        return log_entry

