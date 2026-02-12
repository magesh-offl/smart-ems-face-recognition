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
        student_id: str,
        confidence_score: float,
        source_path: str,
        face_location: Dict[str, int],
        batch_id: str,
        total_faces_detected: int,
        processing_time_ms: Optional[float] = None,
        admission_id: str = "",
        first_name: str = "",
        last_name: str = "",
        course_id: str = "",
        course_name: str = "",
        section: str = ""
    ) -> Dict[str, Any]:
        """Create a new batch recognition log document.
        
        Args:
            student_id: Student ID (may be same as admission_id initially)
            confidence_score: Recognition confidence (0.0 - 1.0)
            source_path: Path to the source image
            face_location: Bounding box {x_min, y_min, x_max, y_max}
            batch_id: UUID for this batch operation
            total_faces_detected: Total faces found in image
            processing_time_ms: Processing time in milliseconds
            admission_id: Stable admission identifier (npz key)
            first_name: Student's first name
            last_name: Student's last name
            course_id: Course ID (e.g., CRS0001)
            course_name: Course name
            section: Section (e.g., A, B)
            
        Returns:
            Document dictionary ready for MongoDB insertion
        """
        doc = {
            "admission_id": admission_id,
            "student_id": student_id,
            "first_name": first_name,
            "last_name": last_name,
            "course_id": course_id,
            "course_name": course_name,
            "section": section,
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

