"""Recognition Response Schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RecognitionLogResponse(BaseModel):
    """Response schema for a recognition log"""
    id: Optional[str] = Field(None, alias="_id")
    person_name: str
    camera_id: str
    timestamp: datetime
    confidence_score: Optional[float] = None
    detection_count: int = Field(default=1)
    last_detection_time: datetime
    
    class Config:
        populate_by_name = True
    
    @staticmethod
    def from_mongo(doc):
        """Convert MongoDB document to RecognitionLogResponse"""
        if not doc:
            return None
        return RecognitionLogResponse(
            _id=str(doc.get('_id')),
            person_name=doc.get('person_name'),
            camera_id=doc.get('camera_id'),
            timestamp=doc.get('timestamp'),
            confidence_score=doc.get('confidence_score'),
            detection_count=doc.get('detection_count', 1),
            last_detection_time=doc.get('last_detection_time')
        )
