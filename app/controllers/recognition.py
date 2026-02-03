"""Recognition Controller with Dependency Injection"""
from typing import List, Optional
from datetime import datetime

from app.services.recognition import RecognitionService
from app.models import RecognitionLogResponse, RecognitionLogUpdate
from app.utils.exceptions import ResourceNotFoundException
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class RecognitionController:
    """
    Controller for recognition operations.
    Accepts service via constructor for dependency injection.
    """
    
    def __init__(self, service: RecognitionService):
        """
        Initialize recognition controller with injected service.
        
        Args:
            service: RecognitionService instance (injected)
        """
        self.recognition_service = service
    
    def save_recognition(self, person_name: str, camera_id: str,
                        confidence_score: Optional[float] = None) -> dict:
        """Handle saving face recognition"""
        try:
            log_id = self.recognition_service.save_recognition(
                person_name, camera_id, confidence_score
            )
            return {
                "success": True,
                "log_id": log_id,
                "message": "Recognition saved successfully"
            }
        except Exception as e:
            logger.error(f"Error saving recognition: {str(e)}")
            raise
    
    def get_recognition_log(self, log_id: str) -> RecognitionLogResponse:
        """Get recognition log"""
        log = self.recognition_service.get_recognition_log(log_id)
        
        if not log:
            raise ResourceNotFoundException(f"Recognition log {log_id} not found")
        
        return RecognitionLogResponse.from_mongo(log)
    
    def get_all_logs(self, skip: int = 0, limit: int = 10) -> dict:
        """Get all recognition logs"""
        logs = self.recognition_service.get_all_logs(skip, limit)
        total_count = self.recognition_service.get_total_count()
        
        return {
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "logs": [RecognitionLogResponse.from_mongo(log) for log in logs]
        }
    
    def filter_logs(self, person_name: Optional[str] = None,
                   camera_id: Optional[str] = None,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   skip: int = 0, limit: int = 10) -> dict:
        """Get filtered recognition logs"""
        logs = self.recognition_service.filter_logs(
            person_name, camera_id, start_date, end_date, skip, limit
        )
        total_count = self.recognition_service.get_total_count(
            person_name, camera_id
        )
        
        return {
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "logs": [RecognitionLogResponse.from_mongo(log) for log in logs]
        }
    
    def update_log(self, log_id: str, update_data: RecognitionLogUpdate) -> dict:
        """Update recognition log"""
        success = self.recognition_service.update_log(
            log_id,
            update_data.person_name,
            update_data.camera_id,
            update_data.confidence_score
        )
        
        if not success:
            raise ResourceNotFoundException(f"Recognition log {log_id} not found")
        
        updated_log = self.recognition_service.get_recognition_log(log_id)
        return {
            "success": True,
            "log": RecognitionLogResponse.from_mongo(updated_log)
        }
    
    def delete_log(self, log_id: str) -> dict:
        """Delete recognition log"""
        success = self.recognition_service.delete_log(log_id)
        
        if not success:
            raise ResourceNotFoundException(f"Recognition log {log_id} not found")
        
        return {
            "success": True,
            "message": f"Log {log_id} deleted successfully"
        }
