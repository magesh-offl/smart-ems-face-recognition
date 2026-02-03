"""Abstract Service Interface"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class IService(ABC):
    """
    Abstract base class for all services.
    Services contain business logic and orchestrate repository operations.
    """
    pass


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


class IBatchRecognitionService(ABC):
    """Interface for batch recognition services"""
    
    @abstractmethod
    def process_image(self, image_path: str) -> Dict[str, Any]:
        """Process an image for face recognition"""
        pass
    
    @abstractmethod
    def get_batch_results(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get results for a specific batch"""
        pass
    
    @abstractmethod
    def get_all_batches(self, skip: int = 0, limit: int = 10):
        """Get all batch summaries"""
        pass
