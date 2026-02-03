"""MongoDB Schema for Batch Recognition Logs"""
from datetime import datetime
from typing import Optional, Dict, Any
import uuid


class BatchRecognitionLogSchema:
    """MongoDB schema for batch recognition logs"""
    collection_name = "batch_recognition_logs"
    
    @staticmethod
    def get_document(
        person_name: str,
        confidence_score: float,
        source_path: str,
        face_location: Dict[str, int],
        batch_id: str,
        total_faces_detected: int,
        processing_time_ms: Optional[float] = None
    ) -> Dict[str, Any]:
        """Get MongoDB document structure for a single detection"""
        return {
            "person_name": person_name,
            "detection_datetime": datetime.utcnow(),
            "confidence_score": confidence_score,
            "source_path": source_path,
            "face_location": face_location,
            "batch_id": batch_id,
            "total_faces_detected": total_faces_detected,
            "processing_time_ms": processing_time_ms,
        }
    
    @staticmethod
    def generate_batch_id() -> str:
        """Generate a unique batch ID"""
        return str(uuid.uuid4())
