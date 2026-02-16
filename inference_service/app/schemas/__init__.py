"""Inference Schemas Package"""
from .inference import (
    DetectionRequest, DetectionResponse,
    RecognitionRequest, RecognitionResponse, RecognizedFace,
    EmbeddingRequest, EmbeddingResponse,
    TrainRequest, TrainResponse,
    ReloadResponse,
    KnownPersonsResponse,
    HealthResponse,
)

__all__ = [
    "DetectionRequest", "DetectionResponse",
    "RecognitionRequest", "RecognitionResponse", "RecognizedFace",
    "EmbeddingRequest", "EmbeddingResponse",
    "TrainRequest", "TrainResponse",
    "ReloadResponse",
    "KnownPersonsResponse",
    "HealthResponse",
]
