"""Batch Recognition Document Model"""
from datetime import datetime
from typing import Optional, Dict, Any
import uuid
from .base import BaseDocument


class BatchRecognitionLogDocument(BaseDocument):
    """MongoDB document model for batch recognition logs.
    
    Stores face detection/recognition results from batch image processing.
    """
    
    collection_name = "batch_recognition_logs"
    
    @staticmethod
    def generate_batch_id() -> str:
        """Generate a unique batch ID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def create(
        person_name: str,
        confidence_score: float,
        source_path: str,
        face_location: Dict[str, int],
        batch_id: str,
        total_faces_detected: int,
        processing_time_ms: Optional[float] = None
    ) -> Dict[str, Any]:
        """Create a new batch recognition log document.
        
        Args:
            person_name: Name of recognized person (or "Unknown")
            confidence_score: Recognition confidence (0.0 - 1.0)
            source_path: Path to the source image
            face_location: Bounding box {x_min, y_min, x_max, y_max}
            batch_id: UUID for this batch operation
            total_faces_detected: Total faces found in image
            processing_time_ms: Processing time in milliseconds
            
        Returns:
            Document dictionary ready for MongoDB insertion
        """
        doc = {
            "person_name": person_name,
            "detection_datetime": datetime.utcnow(),
            "confidence_score": confidence_score,
            "source_path": source_path,
            "face_location": face_location,
            "batch_id": batch_id,
            "total_faces_detected": total_faces_detected,
            "processing_time_ms": processing_time_ms,
            **BaseDocument.get_base_fields()
        }
        return doc
