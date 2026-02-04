"""Recognition Log Document Model"""
from datetime import datetime
from typing import Optional, Dict, Any
from .base import BaseDocument


class RecognitionLogDocument(BaseDocument):
    """MongoDB document model for recognition logs.
    
    Stores individual face recognition events from live camera feeds.
    """
    
    collection_name = "recognition_logs"
    
    @staticmethod
    def create(
        person_name: str,
        camera_id: str,
        confidence_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """Create a new recognition log document.
        
        Args:
            person_name: Name of the recognized person
            camera_id: ID of the camera that captured the face
            confidence_score: Recognition confidence (0.0 - 1.0)
            
        Returns:
            Document dictionary ready for MongoDB insertion
        """
        now = datetime.utcnow()
        doc = {
            "person_name": person_name,
            "camera_id": camera_id,
            "timestamp": now,
            "confidence_score": confidence_score,
            "detection_count": 1,
            "last_detection_time": now,
            **BaseDocument.get_base_fields()
        }
        return doc
    
    @staticmethod
    def increment_detection(doc_id: str) -> Dict[str, Any]:
        """Get update data for incrementing detection count.
        
        Args:
            doc_id: Document ID to update
            
        Returns:
            Update dictionary for MongoDB $set and $inc operations
        """
        return {
            "$inc": {"detection_count": 1},
            "$set": {
                "last_detection_time": datetime.utcnow(),
                **BaseDocument.update_timestamp()
            }
        }
