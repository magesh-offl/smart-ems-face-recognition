"""Detection Service — wraps ML face detection models.

Provides face detection via YOLOv12 (primary) or SCRFD (fallback).
Models are loaded lazily on first use and cached for the process lifetime.
"""
import os
import logging
import numpy as np
from typing import Tuple, Optional

from app.config import get_settings, PROJECT_ROOT

logger = logging.getLogger(__name__)

# Lazy-loaded detector instance
_detector = None
_detector_type: str = ""


def get_detector_type() -> str:
    """Return the name of the currently loaded detector."""
    return _detector_type


def get_detector():
    """Get or create the face detector singleton.

    Uses YOLOv12 by default, falls back to SCRFD if unavailable.
    """
    global _detector, _detector_type
    if _detector is not None:
        return _detector

    settings = get_settings()
    model_name = settings.DETECTION_MODEL

    if model_name == "yolov12":
        try:
            from ml.detection.yolov12.detector import YOLOv12FaceDetector
            _detector = YOLOv12FaceDetector()
            _detector_type = "yolov12"
            logger.info("Loaded YOLOv12 face detector")
        except (ImportError, FileNotFoundError) as e:
            logger.warning(f"YOLOv12 unavailable ({e}), falling back to SCRFD")
            model_name = "scrfd"

    if model_name != "yolov12" or _detector is None:
        from ml.detection.scrfd.detector import SCRFD
        model_path = os.path.join(
            PROJECT_ROOT, "ml", "detection", "scrfd", "weights", "scrfd_2.5g_bnkps.onnx"
        )
        _detector = SCRFD(model_file=model_path)
        _detector_type = "scrfd"
        logger.info("Loaded SCRFD face detector")

    return _detector


def detect_faces(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Detect faces in an image.

    Args:
        image: BGR image as numpy array (OpenCV format).

    Returns:
        (bboxes, landmarks):
            bboxes: Nx5 array of [x1, y1, x2, y2, score]
            landmarks: Nx5x2 array of facial landmarks
    """
    detector = get_detector()
    return detector.detect(image=image)


def preprocess_image(image: np.ndarray) -> np.ndarray:
    """Preprocess image for better face detection.

    1. Upscale if image is too small
    2. Apply CLAHE contrast enhancement (if enabled)

    Args:
        image: BGR image (OpenCV format).

    Returns:
        Preprocessed image.
    """
    settings = get_settings()

    if not settings.ENABLE_PREPROCESSING:
        return image

    import cv2

    height, width = image.shape[:2]

    # Upscale small images
    if settings.ENABLE_UPSCALING and width < settings.MIN_IMAGE_WIDTH:
        scale_factor = settings.MIN_IMAGE_WIDTH / width
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        logger.info(f"Upscaled image from {width}x{height} to {new_width}x{new_height}")

    # CLAHE contrast enhancement (disabled by default)
    if settings.ENABLE_CLAHE:
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_enhanced = clahe.apply(l_channel)
        lab_enhanced = cv2.merge([l_enhanced, a_channel, b_channel])
        image = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
        logger.info("Applied CLAHE contrast enhancement")

    return image
