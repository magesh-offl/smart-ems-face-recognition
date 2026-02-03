"""Batch Recognition Controller with Dependency Injection"""
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.services.batch_recognition import BatchRecognitionService
from app.models import BatchRecognitionResult, BatchRecognitionResponse, FaceLocation
from app.utils.exceptions import ResourceNotFoundException
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class BatchRecognitionController:
    """
    Controller for batch recognition operations.
    Accepts service via constructor for dependency injection.
    """
    
    def __init__(self, service: BatchRecognitionService):
        """
        Initialize batch recognition controller with injected service.
        
        Args:
            service: BatchRecognitionService instance (injected)
        """
        self.service = service
    
    def process_image(self, image_path: str) -> BatchRecognitionResponse:
        """
        Process an image for face recognition.
        
        Args:
            image_path: Server-side path to the image
            
        Returns:
            BatchRecognitionResponse with results
        """
        try:
            result = self.service.process_image(image_path)
            
            # Convert results to response models
            recognition_results = []
            for r in result["results"]:
                face_loc = r["face_location"]
                recognition_results.append(
                    BatchRecognitionResult(
                        _id=r.get("_id"),
                        person_name=r["person_name"],
                        detection_datetime=datetime.utcnow(),
                        confidence_score=r["confidence_score"],
                        face_location=FaceLocation(
                            x_min=face_loc["x_min"],
                            y_min=face_loc["y_min"],
                            x_max=face_loc["x_max"],
                            y_max=face_loc["y_max"]
                        )
                    )
                )
            
            return BatchRecognitionResponse(
                success=True,
                batch_id=result["batch_id"],
                source_path=result["source_path"],
                total_faces_detected=result["total_faces_detected"],
                recognized_faces=result["recognized_faces"],
                processing_time_ms=result["processing_time_ms"],
                results=recognition_results
            )
        except FileNotFoundError as e:
            logger.error(f"Image not found: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise
    
    def get_batch_results(self, batch_id: str) -> Dict[str, Any]:
        """Get results for a specific batch"""
        result = self.service.get_batch_results(batch_id)
        
        if not result:
            raise ResourceNotFoundException(f"Batch {batch_id} not found")
        
        # Convert logs to response format
        recognition_results = [
            BatchRecognitionResult.from_mongo(log) 
            for log in result.get("logs", [])
        ]
        
        return {
            "batch_id": result["batch_id"],
            "source_path": result["source_path"],
            "total_faces_detected": result["total_faces_detected"],
            "recognized_count": result["recognized_count"],
            "processing_time_ms": result["processing_time_ms"],
            "results": recognition_results
        }
    
    def get_all_batches(self, skip: int = 0, limit: int = 10) -> Dict[str, Any]:
        """Get all batch summaries"""
        batches = self.service.get_all_batches(skip, limit)
        
        return {
            "skip": skip,
            "limit": limit,
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
    
    def delete_all_batches(self) -> Dict[str, Any]:
        """Delete all batch recognition logs"""
        result = self.service.delete_all_batches()
        logger.info(f"Deleted all batches: {result['deleted_count']} logs removed")
        return result

