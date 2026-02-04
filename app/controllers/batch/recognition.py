"""Batch Recognition Controller"""
from datetime import datetime

from app.services.batch import BatchRecognitionService
from app.schemas import BatchRecognitionResult, BatchRecognitionResponse, FaceLocation
from app.utils.exceptions import ResourceNotFoundException


class BatchRecognitionController:
    """Controller for batch recognition operations."""
    
    def __init__(self, service: BatchRecognitionService):
        self.service = service
    
    def process_image(self, image_path: str) -> BatchRecognitionResponse:
        """Process an image for face recognition."""
        result = self.service.process_image(image_path)
        
        recognition_results = [
            BatchRecognitionResult(
                _id=r.get("_id"),
                person_name=r["person_name"],
                detection_datetime=datetime.utcnow(),
                confidence_score=r["confidence_score"],
                face_location=FaceLocation(
                    x_min=r["face_location"]["x_min"],
                    y_min=r["face_location"]["y_min"],
                    x_max=r["face_location"]["x_max"],
                    y_max=r["face_location"]["y_max"]
                )
            )
            for r in result["results"]
        ]
        
        return BatchRecognitionResponse(
            success=True,
            batch_id=result["batch_id"],
            source_path=result["source_path"],
            total_faces_detected=result["total_faces_detected"],
            recognized_faces=result["recognized_faces"],
            processing_time_ms=result["processing_time_ms"],
            results=recognition_results
        )
    
    def get_batch_results(self, batch_id: str) -> dict:
        """Get results for a specific batch."""
        result = self.service.get_batch_results(batch_id)
        if not result:
            raise ResourceNotFoundException(f"Batch {batch_id} not found")
        
        return {
            "batch_id": result["batch_id"],
            "source_path": result["source_path"],
            "total_faces_detected": result["total_faces_detected"],
            "recognized_count": result["recognized_count"],
            "processing_time_ms": result["processing_time_ms"],
            "results": [BatchRecognitionResult.from_mongo(log) for log in result.get("logs", [])]
        }
    
    def get_all_batches(self, skip: int = 0, limit: int = 10) -> dict:
        """Get all batch summaries."""
        batches = self.service.get_all_batches(skip, limit)
        return {
            "skip": skip, "limit": limit,
            "batches": [
                {
                    "batch_id": b["_id"],
                    "source_path": b["source_path"],
                    "detection_datetime": b["detection_datetime"],
                    "total_faces_detected": b["total_faces_detected"],
                    "recognized_count": b["recognized_count"],
                    "processing_time_ms": b["processing_time_ms"]
                }
                for b in batches
            ]
        }
    
    def delete_all_batches(self) -> dict:
        """Delete all batch recognition logs."""
        return self.service.delete_all_batches()
