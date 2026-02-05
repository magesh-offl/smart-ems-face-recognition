"""Recognition Service Interface"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class IRecognitionService(ABC):
    """Interface for recognition-related services"""
    
    @abstractmethod
    def save_recognition(
        self, 
        person_name: str, 
        camera_id: str, 
        confidence_score: Optional[float] = None
    ) -> Optional[str]:
        """Save a recognition event"""
        pass
    
    @abstractmethod
    def get_log_by_id(self, log_id: str) -> Optional[Dict[str, Any]]:
        """Get recognition log by ID"""
        pass
    
    @abstractmethod
    def get_logs_with_filter(
        self,
        person_name: Optional[str] = None,
        camera_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get filtered recognition logs"""
        pass
