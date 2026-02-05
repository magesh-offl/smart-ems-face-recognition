"""Recognition Request Schemas"""
from pydantic import BaseModel, Field
from typing import Optional


class RecognitionLogCreate(BaseModel):
    """Schema for creating a recognition log (live camera)"""
    person_name: str = Field(..., min_length=1, max_length=100)
    camera_id: str = Field(..., min_length=1, max_length=100)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class RecognitionLogUpdate(BaseModel):
    """Schema for updating a recognition log"""
    person_name: Optional[str] = Field(None, min_length=1, max_length=100)
    camera_id: Optional[str] = Field(None, min_length=1, max_length=100)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
