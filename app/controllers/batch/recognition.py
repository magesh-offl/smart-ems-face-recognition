"""Async Batch Recognition Controller"""
from typing import Optional, Dict, Any, List

from app.services.batch.recognition import BatchRecognitionService


class BatchRecognitionController:
    """Async controller for batch face recognition."""
    
    def __init__(self, service: BatchRecognitionService):
        self.service = service
    
    async def process_image(self, image_path: str) -> Dict[str, Any]:
        """Process an image for face recognition."""
        result = await self.service.process_image(image_path)
        result["success"] = True
        return result
    
    async def get_batch_results(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get results for a specific batch."""
        return await self.service.get_batch_results(batch_id)
    
    async def get_all_batches(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get all batch summaries."""
        return await self.service.get_all_batches(skip, limit)
    
    async def delete_all(self) -> Dict[str, Any]:
        """Delete all batch recognition logs."""
        return await self.service.delete_all_batches()
