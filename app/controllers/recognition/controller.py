"""Recognition Controller"""
from typing import Optional
from datetime import datetime

from app.services.recognition import RecognitionService
from app.schemas import RecognitionLogResponse, RecognitionLogUpdate
from app.utils.exceptions import ResourceNotFoundException


class RecognitionController:
    """Controller for recognition operations."""
    
    def __init__(self, service: RecognitionService):
        self.service = service
    
    def save_recognition(self, person_name: str, camera_id: str,
                        confidence_score: Optional[float] = None) -> dict:
        """Save face recognition."""
        log_id = self.service.save_recognition(person_name, camera_id, confidence_score)
        return {"success": True, "log_id": log_id, "message": "Recognition saved"}
    
    def get_recognition_log(self, log_id: str) -> RecognitionLogResponse:
        """Get recognition log by ID."""
        log = self.service.get_recognition_log(log_id)
        if not log:
            raise ResourceNotFoundException(f"Log {log_id} not found")
        return RecognitionLogResponse.from_mongo(log)
    
    def get_all_logs(self, skip: int = 0, limit: int = 10) -> dict:
        """Get all recognition logs with pagination."""
        logs = self.service.get_all_logs(skip, limit)
        total = self.service.get_total_count()
        return {
            "total": total, "skip": skip, "limit": limit,
            "logs": [RecognitionLogResponse.from_mongo(log) for log in logs]
        }
    
    def filter_logs(self, person_name: Optional[str] = None,
                   camera_id: Optional[str] = None,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   skip: int = 0, limit: int = 10) -> dict:
        """Get filtered recognition logs."""
        logs = self.service.filter_logs(person_name, camera_id, start_date, end_date, skip, limit)
        total = self.service.get_total_count(person_name, camera_id)
        return {
            "total": total, "skip": skip, "limit": limit,
            "logs": [RecognitionLogResponse.from_mongo(log) for log in logs]
        }
    
    def update_log(self, log_id: str, data: RecognitionLogUpdate) -> dict:
        """Update recognition log."""
        success = self.service.update_log(log_id, data.person_name, data.camera_id, data.confidence_score)
        if not success:
            raise ResourceNotFoundException(f"Log {log_id} not found")
        updated = self.service.get_recognition_log(log_id)
        return {"success": True, "log": RecognitionLogResponse.from_mongo(updated)}
    
    def delete_log(self, log_id: str) -> dict:
        """Delete recognition log."""
        if not self.service.delete_log(log_id):
            raise ResourceNotFoundException(f"Log {log_id} not found")
        return {"success": True, "message": f"Log {log_id} deleted"}
