"""Async Recognition Controller"""
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.services.recognition.service import RecognitionService
from app.schemas.responses.recognition import RecognitionLogResponse


class RecognitionController:
    """Async controller for recognition operations."""
    
    def __init__(self, service: RecognitionService):
        self.service = service
    
    async def save_recognition(self, person_name: str, camera_id: str,
                               confidence_score: Optional[float] = None) -> dict:
        """Save face recognition."""
        log_id = await self.service.save_recognition(person_name, camera_id, confidence_score)
        return {"success": True, "log_id": log_id, "message": "Recognition saved"}
    
    async def get_log(self, log_id: str) -> Optional[RecognitionLogResponse]:
        """Get recognition log by ID."""
        log = await self.service.get_log_by_id(log_id)
        return RecognitionLogResponse.from_mongo(log) if log else None
    
    async def get_logs(self, person_name: Optional[str] = None,
                       camera_id: Optional[str] = None,
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None,
                       skip: int = 0, limit: int = 10) -> Dict[str, Any]:
        """Get logs with filtering and pagination."""
        logs = await self.service.get_logs(person_name, camera_id, start_date, end_date, skip, limit)
        total = await self.service.get_total_count(person_name, camera_id)
        return {
            "data": [RecognitionLogResponse.from_mongo(log) for log in logs],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    async def update_log(self, log_id: str, person_name: Optional[str] = None,
                         camera_id: Optional[str] = None,
                         confidence_score: Optional[float] = None) -> dict:
        """Update recognition log."""
        success = await self.service.update_log(log_id, person_name, camera_id, confidence_score)
        return {"success": success, "message": "Log updated" if success else "Log not found"}
    
    async def delete_log(self, log_id: str) -> dict:
        """Delete recognition log."""
        success = await self.service.delete_log(log_id)
        return {"success": success, "message": "Log deleted" if success else "Log not found"}
