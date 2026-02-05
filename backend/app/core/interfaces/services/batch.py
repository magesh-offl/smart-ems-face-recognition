"""Batch Recognition Service Interface"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


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
    def get_all_batches(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get all batch summaries"""
        pass
