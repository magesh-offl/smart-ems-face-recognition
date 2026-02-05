"""Async Recognition Service"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.repositories.recognition import RecognitionRepository
from app.core.interfaces.services import IRecognitionService


class RecognitionService(IRecognitionService):
    """Async service for recognition operations."""
    
    def __init__(self, repository: RecognitionRepository):
        self.repo = repository
    
    async def save_recognition(self, person_name: str, camera_id: str,
                               confidence_score: Optional[float] = None) -> str:
        """Save face recognition with 1-hour cooldown."""
        return await self.repo.create_or_update_log(person_name, camera_id, confidence_score)
    
    async def get_log_by_id(self, log_id: str) -> Optional[Dict[str, Any]]:
        """Get recognition log by ID."""
        return await self.repo.get_log_by_id(log_id)
    
    async def get_logs_with_filter(self, person_name: Optional[str] = None,
                                   camera_id: Optional[str] = None,
                                   skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get filtered recognition logs (interface method)."""
        return await self.repo.get_logs_with_filter(person_name, camera_id, None, None, skip, limit)
    
    async def get_logs(self, person_name: Optional[str] = None,
                       camera_id: Optional[str] = None,
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None,
                       skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get logs with full filtering including dates."""
        return await self.repo.get_logs_with_filter(person_name, camera_id, start_date, end_date, skip, limit)
    
    async def update_log(self, log_id: str, person_name: Optional[str] = None,
                         camera_id: Optional[str] = None,
                         confidence_score: Optional[float] = None) -> bool:
        """Update recognition log."""
        return await self.repo.update_log(log_id, person_name, camera_id, confidence_score)
    
    async def delete_log(self, log_id: str) -> bool:
        """Delete recognition log."""
        return await self.repo.delete_log(log_id)
    
    async def get_total_count(self, person_name: Optional[str] = None,
                              camera_id: Optional[str] = None) -> int:
        """Get total count."""
        return await self.repo.get_total_count(person_name, camera_id)
