"""Batch Recognition Response Schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FaceLocation(BaseModel):
    """Bounding box coordinates for detected face"""
    x_min: int
    y_min: int
    x_max: int
    y_max: int


class BatchRecognitionResult(BaseModel):
    """Single detection result from batch recognition"""
    id: Optional[str] = Field(None, alias="_id")
    person_name: str
    detection_datetime: Optional[datetime] = None
    confidence_score: float
    face_location: FaceLocation
    
    class Config:
        populate_by_name = True
    
    @staticmethod
    def from_mongo(doc):
        """Convert MongoDB document to BatchRecognitionResult"""
        if not doc:
            return None
        face_loc = doc.get('face_location', {})
        return BatchRecognitionResult(
            _id=str(doc.get('_id')),
            person_name=doc.get('person_name'),
            detection_datetime=doc.get('detection_datetime'),
            confidence_score=doc.get('confidence_score'),
            face_location=FaceLocation(
                x_min=face_loc.get('x_min', 0),
                y_min=face_loc.get('y_min', 0),
                x_max=face_loc.get('x_max', 0),
                y_max=face_loc.get('y_max', 0)
            )
        )


class BatchRecognitionResponse(BaseModel):
    """Response schema for batch recognition"""
    success: bool
    batch_id: str
    source_path: str
    total_faces_detected: int
    recognized_faces: int
    processing_time_ms: float
    results: List[BatchRecognitionResult]


class AddPersonsResponse(BaseModel):
    """Response schema for adding persons"""
    success: bool
    message: str
    persons_added: int
    total_images_processed: int
