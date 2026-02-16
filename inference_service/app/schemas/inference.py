"""Inference Request/Response Schemas

Pydantic models for all inference service endpoints.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional


# =============================================================================
# Health
# =============================================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    models_loaded: bool = False
    detector_type: str = ""
    recognizer_type: str = ""


# =============================================================================
# Detection
# =============================================================================

class DetectionRequest(BaseModel):
    """Face detection request — accepts base64 image."""
    image: str = Field(..., description="Base64-encoded image bytes")


class BoundingBox(BaseModel):
    """Face bounding box with confidence."""
    x_min: int
    y_min: int
    x_max: int
    y_max: int
    score: float


class Landmark(BaseModel):
    """5-point facial landmark (list of [x, y] pairs)."""
    points: List[List[float]] = Field(..., description="5 landmark points, each [x, y]")


class DetectedFace(BaseModel):
    """A single detected face with bbox and landmarks."""
    bbox: BoundingBox
    landmark: Landmark


class DetectionResponse(BaseModel):
    """Face detection response."""
    faces: List[DetectedFace] = []
    total_faces: int = 0


# =============================================================================
# Recognition (full pipeline: detect → align → embed → match)
# =============================================================================

class RecognitionRequest(BaseModel):
    """Full recognition request — accepts base64 image."""
    image: str = Field(..., description="Base64-encoded image bytes")
    confidence_threshold: Optional[float] = Field(
        None, description="Override default threshold"
    )


class RecognizedFace(BaseModel):
    """A recognized face result."""
    person_name: str
    confidence_score: float
    face_location: Dict[str, int]  # x_min, y_min, x_max, y_max


class RecognitionResponse(BaseModel):
    """Full recognition response."""
    results: List[RecognizedFace] = []
    total_faces_detected: int = 0
    processing_time_ms: float = 0.0


# =============================================================================
# Embedding
# =============================================================================

class EmbeddingRequest(BaseModel):
    """Embedding extraction request — accepts base64 aligned face image."""
    face_image: str = Field(..., description="Base64-encoded aligned face image")


class EmbeddingResponse(BaseModel):
    """Embedding extraction response."""
    embedding: List[float] = []


# =============================================================================
# Training (add persons)
# =============================================================================

class TrainRequest(BaseModel):
    """Training request — adds persons to feature store.

    images: dict mapping person_id to list of base64-encoded images.
    Example: {"ADM0001": ["base64...", "base64..."], "ADM0002": [...]}
    """
    images: Dict[str, List[str]] = Field(
        ..., description="person_id → list of base64-encoded images"
    )
    move_to_backup: bool = Field(
        True, description="Move processed images to backup folder"
    )


class TrainResponse(BaseModel):
    """Training response."""
    success: bool = False
    message: str = ""
    persons_added: List[str] = []
    faces_processed: int = 0


# =============================================================================
# Feature Store
# =============================================================================

class ReloadResponse(BaseModel):
    """Feature reload response."""
    status: str = "ok"
    persons_count: int = 0
    embeddings_count: int = 0


class KnownPersonsResponse(BaseModel):
    """Known persons response."""
    persons: List[str] = []
    count: int = 0
