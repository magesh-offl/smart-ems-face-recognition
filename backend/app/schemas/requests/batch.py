"""Batch Recognition Request Schemas"""
from typing import Optional
from pydantic import BaseModel, Field


class BatchRecognitionRequest(BaseModel):
    """Request schema for batch recognition from image path"""
    image_path: str = Field(..., min_length=1, description="Server-side path to the image file")


class AddPersonsRequest(BaseModel):
    """Request schema for adding persons from folder"""
    source_path: Optional[str] = Field(None, description="Path to folder containing person subfolders")
    move_to_backup: bool = Field(True, description="Whether to move processed folders to backup")
