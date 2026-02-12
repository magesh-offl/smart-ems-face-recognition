"""Password Reset Repository - CRUD for password_resets collection"""
from typing import List, Optional, Dict, Any

from app.repositories.base import BaseRepository
from app.models import PasswordResetDocument


class PasswordResetRepository(BaseRepository):
    """Async repository for password reset request management."""
    
    def __init__(self):
        super().__init__(PasswordResetDocument.collection_name)
    
    async def create_reset_request(self, reset_data: Dict[str, Any]) -> str:
        """Create a new password reset request."""
        return await self.create(reset_data)
    
    async def get_pending_requests(
        self, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get all pending password reset requests (for admin dashboard)."""
        return await self.find_many(
            {"status": PasswordResetDocument.STATUS_PENDING},
            skip=skip,
            limit=limit
        )
    
    async def get_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all reset requests for a user."""
        return await self.find_many({"user_id": user_id}, limit=100)
    
    async def get_pending_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get pending reset request for a user (if any)."""
        return await self.find_one({
            "user_id": user_id,
            "status": PasswordResetDocument.STATUS_PENDING
        })
    
    async def mark_completed(self, request_id: str) -> bool:
        """Mark a reset request as completed."""
        return await self.update(request_id, {
            "status": PasswordResetDocument.STATUS_COMPLETED
        })
    
    async def mark_expired(self, request_id: str) -> bool:
        """Mark a reset request as expired."""
        return await self.update(request_id, {
            "status": PasswordResetDocument.STATUS_EXPIRED
        })
    
    async def count_pending(self) -> int:
        """Count pending reset requests."""
        return await self.count({"status": PasswordResetDocument.STATUS_PENDING})
