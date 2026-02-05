"""YOLOv12 Face Detector

This module provides a wrapper for YOLOv12 face detection model.
Uses the ultralytics framework for inference.
"""
import os
import numpy as np
from typing import Tuple, Optional

# Lazy import to avoid loading ultralytics at startup
_model = None

# Default model path
MODEL_PATH = os.path.join(os.path.dirname(__file__), "weights", "yolov12n-face.pt")


def _get_model():
    """Lazy load YOLOv12 model"""
    global _model
    if _model is None:
        try:
            from ultralytics import YOLO
            if os.path.exists(MODEL_PATH):
                _model = YOLO(MODEL_PATH)
            else:
                # Download the model if not exists
                print(f"Model not found at {MODEL_PATH}. Please download yolov12n-face.pt")
                raise FileNotFoundError(f"YOLOv12 face model not found: {MODEL_PATH}")
        except ImportError:
            raise ImportError("ultralytics not installed. Run: pip install ultralytics")
    return _model


class YOLOv12FaceDetector:
    """YOLOv12-based face detector compatible with SCRFD interface"""
    
    def __init__(self, model_path: Optional[str] = None, conf_threshold: float = 0.5):
        """
        Initialize YOLOv12 face detector.
        
        Args:
            model_path: Path to YOLOv12 face model weights
            conf_threshold: Confidence threshold for detections
        """
        self.model_path = model_path or MODEL_PATH
        self.conf_threshold = conf_threshold
        self._model = None
    
    def _load_model(self):
        """Lazy load the model"""
        if self._model is None:
            from ultralytics import YOLO
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model not found: {self.model_path}")
            self._model = YOLO(self.model_path)
        return self._model
    
    def detect(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect faces in an image.
        
        Args:
            image: BGR image as numpy array
            
        Returns:
            Tuple of (bboxes, landmarks)
            - bboxes: Nx5 array of [x1, y1, x2, y2, score]
            - landmarks: Nx5x2 array of facial landmarks (if available)
        """
        model = self._load_model()
        
        # Run inference
        results = model.predict(
            source=image,
            conf=self.conf_threshold,
            verbose=False
        )
        
        bboxes = []
        landmarks = []
        
        if results and len(results) > 0:
            result = results[0]
            
            if result.boxes is not None:
                for box in result.boxes:
                    # Get bounding box
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = box.conf[0].cpu().numpy()
                    bboxes.append([x1, y1, x2, y2, conf])
                    
                    # YOLOv12-face may include keypoints
                    if hasattr(result, 'keypoints') and result.keypoints is not None:
                        kpts = result.keypoints.xy[0].cpu().numpy()
                        if len(kpts) >= 5:
                            landmarks.append(kpts[:5])
                        else:
                            # Generate approximate landmarks from bbox
                            landmarks.append(self._approximate_landmarks(x1, y1, x2, y2))
                    else:
                        # Generate approximate landmarks from bbox
                        landmarks.append(self._approximate_landmarks(x1, y1, x2, y2))
        
        bboxes = np.array(bboxes) if bboxes else np.array([]).reshape(0, 5)
        landmarks = np.array(landmarks) if landmarks else np.array([]).reshape(0, 5, 2)
        
        return bboxes, landmarks
    
    def _approximate_landmarks(self, x1: float, y1: float, x2: float, y2: float) -> np.ndarray:
        """
        Generate approximate 5-point landmarks from bounding box.
        Points: left_eye, right_eye, nose, left_mouth, right_mouth
        """
        w = x2 - x1
        h = y2 - y1
        
        # Approximate landmark positions (normalized to face box)
        landmarks = np.array([
            [x1 + 0.3 * w, y1 + 0.35 * h],  # left eye
            [x1 + 0.7 * w, y1 + 0.35 * h],  # right eye
            [x1 + 0.5 * w, y1 + 0.55 * h],  # nose
            [x1 + 0.35 * w, y1 + 0.75 * h], # left mouth
            [x1 + 0.65 * w, y1 + 0.75 * h], # right mouth
        ])
        
        return landmarks
