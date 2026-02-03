"""API Request/Response Pydantic Models"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RecognitionLogCreate(BaseModel):
    """Schema for creating a recognition log"""
    person_name: str = Field(..., min_length=1, max_length=100)
    camera_id: str = Field(..., min_length=1, max_length=100)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class RecognitionLogResponse(BaseModel):
    """Schema for recognition log response"""
    id: Optional[str] = Field(None, alias="_id")
    person_name: str
    camera_id: str
    timestamp: datetime
    confidence_score: Optional[float]
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


class RecognitionLogUpdate(BaseModel):
    """Schema for updating a recognition log"""
    person_name: Optional[str] = None
    camera_id: Optional[str] = None
    confidence_score: Optional[float] = None


class RecognitionLogFilter(BaseModel):
    """Schema for filtering recognition logs"""
    person_name: Optional[str] = None
    camera_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)


class APIKeyCreate(BaseModel):
    """Schema for creating API key"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class APIKeyResponse(BaseModel):
    """Schema for API key response"""
    id: str = Field(alias="_id")
    name: str
    key: str
    created_at: datetime
    
    class Config:
        populate_by_name = True


class UserCreate(BaseModel):
    """Schema for user creation"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    """Schema for user response"""
    id: str = Field(alias="_id")
    username: str
    created_at: datetime
    
    class Config:
        populate_by_name = True


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# ============= Batch Recognition Models =============

class BatchRecognitionRequest(BaseModel):
    """Request schema for batch recognition from image path"""
    image_path: str = Field(..., min_length=1, description="Server-side path to the image file")


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
    detection_datetime: datetime
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
