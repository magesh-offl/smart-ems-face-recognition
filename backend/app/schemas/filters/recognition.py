"""Recognition Filter Schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RecognitionLogFilter(BaseModel):
    """Schema for filtering recognition logs"""
    person_name: Optional[str] = None
    camera_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)


class BatchRecognitionFilter(BaseModel):
    """Schema for filtering batch recognition logs"""
    person_name: Optional[str] = None
    batch_id: Optional[str] = None
    source_path: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)
