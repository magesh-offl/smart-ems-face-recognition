"""ML Model Factory - Provides detector and recognizer instances"""
import os
import numpy as np
import torch
from typing import Optional, Tuple
from torchvision import transforms

from .config import DETECTION_MODEL, RECOGNITION_MODEL, PROJECT_ROOT, FEATURE_PATH

# Lazy-loaded instances
_detector = None
_recognizer = None
_device = None
_images_names = None
_images_embs = None


def get_device() -> torch.device:
    """Get torch device (GPU if available)."""
    global _device
    if _device is None:
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return _device


def get_detector():
    """Get face detector based on config."""
    global _detector
    if _detector is None:
        if DETECTION_MODEL == "yolov12":
            try:
                from ml.detection.yolov12.detector import YOLOv12FaceDetector
                _detector = YOLOv12FaceDetector()
            except (ImportError, FileNotFoundError):
                from ml.detection.scrfd.detector import SCRFD
                model_path = os.path.join(PROJECT_ROOT, "ml/detection/scrfd/weights/scrfd_2.5g_bnkps.onnx")
                _detector = SCRFD(model_file=model_path)
        else:
            from ml.detection.scrfd.detector import SCRFD
            model_path = os.path.join(PROJECT_ROOT, "ml/detection/scrfd/weights/scrfd_2.5g_bnkps.onnx")
            _detector = SCRFD(model_file=model_path)
    return _detector


def get_recognizer():
    """Get face recognizer based on config."""
    global _recognizer
    if _recognizer is None:
        if RECOGNITION_MODEL == "adaface":
            try:
                from ml.recognition.adaface.model import AdaFaceRecognizer
                _recognizer = AdaFaceRecognizer(device=get_device())
            except (ImportError, FileNotFoundError):
                from ml.recognition.arcface.model import iresnet_inference
                model_path = os.path.join(PROJECT_ROOT, "ml/recognition/arcface/weights/arcface_r100.pth")
                _recognizer = iresnet_inference(model_name="r100", path=model_path, device=get_device())
        else:
            from ml.recognition.arcface.model import iresnet_inference
            model_path = os.path.join(PROJECT_ROOT, "ml/recognition/arcface/weights/arcface_r100.pth")
            _recognizer = iresnet_inference(model_name="r100", path=model_path, device=get_device())
    return _recognizer


def get_face_embedding(face_image: np.ndarray) -> np.ndarray:
    """Extract face embedding from aligned face image."""
    recognizer = get_recognizer()
    device = get_device()
    
    preprocess = transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize((112, 112)),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
    ])
    
    face_tensor = preprocess(face_image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        embedding = recognizer(face_tensor)
        if isinstance(embedding, tuple):
            embedding = embedding[0]
        embedding = embedding.cpu().numpy()
    
    return (embedding / np.linalg.norm(embedding, axis=1, keepdims=True))[0]


def get_features() -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    """Load pre-computed face features."""
    global _images_names, _images_embs
    if _images_names is None or _images_embs is None:
        try:
            data = np.load(FEATURE_PATH + ".npz", allow_pickle=True)
            _images_names = data["images_name"]
            _images_embs = data["images_emb"]
        except Exception:
            return None, None
    return _images_names, _images_embs


def reload_features():
    """Force reload of face features."""
    global _images_names, _images_embs
    _images_names = None
    _images_embs = None
    return get_features()


def compare_embeddings(query_emb: np.ndarray, gallery_embs: np.ndarray) -> Tuple[float, int]:
    """Compare query embedding against gallery."""
    sims = np.dot(gallery_embs, query_emb.T)
    best_idx = np.argmax(sims)
    return float(sims[best_idx]), int(best_idx)
