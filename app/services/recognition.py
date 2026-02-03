"""Recognition Service with Dependency Injection"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.interfaces.service import IRecognitionService
from app.repositories.recognition import RecognitionRepository
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class RecognitionService(IRecognitionService):
    """
    Service for recognition operations.
    Implements IRecognitionService interface.
    Accepts repository via constructor for dependency injection.
    """
    
    def __init__(self, repository: RecognitionRepository):
        """
        Initialize recognition service with injected repository.
        
        Args:
            repository: RecognitionRepository instance (injected)
        """
        self.recognition_repo = repository
    
    def save_recognition(self, person_name: str, camera_id: str,
                        confidence_score: Optional[float] = None) -> str:
        """
        Save face recognition with 1-hour cooldown.
        Returns log ID.
        """
        log_id = self.recognition_repo.create_or_update_log(
            person_name, camera_id, confidence_score
        )
        return log_id
    
    def get_recognition_log(self, log_id: str) -> Optional[Dict[str, Any]]:
        """Get recognition log by ID"""
        return self.recognition_repo.get_log_by_id(log_id)
    
    def get_all_logs(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get all recognition logs"""
        return self.recognition_repo.get_all_logs(skip, limit)
    
    def filter_logs(self, person_name: Optional[str] = None,
                   camera_id: Optional[str] = None,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get filtered recognition logs"""
        return self.recognition_repo.get_logs_with_filter(
            person_name, camera_id, start_date, end_date, skip, limit
        )
    
    def update_log(self, log_id: str, person_name: Optional[str] = None,
                  camera_id: Optional[str] = None,
                  confidence_score: Optional[float] = None) -> bool:
        """Update recognition log"""
        return self.recognition_repo.update_log(
            log_id, person_name, camera_id, confidence_score
        )
    
    def delete_log(self, log_id: str) -> bool:
        """Delete recognition log"""
        return self.recognition_repo.delete_log(log_id)
    
    def get_total_count(self, person_name: Optional[str] = None,
                       camera_id: Optional[str] = None) -> int:
        """Get total count of logs"""
        return self.recognition_repo.get_total_count(person_name, camera_id)
