#!/usr/bin/env python3
"""
Face Recognition Script
Run from project root: python scripts/recognize2.py
"""
import sys
import os
import warnings

# Suppress FutureWarnings from dependencies
warnings.filterwarnings("ignore", category=FutureWarning)

# Add project root to path so we can import face_detection, etc.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import cv2
import numpy as np
import torch
import yaml
from torchvision import transforms

from ml.alignment.alignment import norm_crop
from ml.detection.scrfd.detector import SCRFD
from ml.detection.yolov5_face.detector import Yolov5Face
from ml.recognition.arcface.model import iresnet_inference
from ml.recognition.arcface.utils import compare_encodings, read_features

# Device configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Face detector (choose one)
detector = SCRFD(model_file=os.path.join(PROJECT_ROOT, "ml/detection/scrfd/weights/scrfd_2.5g_bnkps.onnx"))
# detector = Yolov5Face(model_file=os.path.join(PROJECT_ROOT, "ml/detection/yolov5_face/weights/yolov5n-face.pt"))

# Face recognizer
recognizer = iresnet_inference(
    model_name="r100", 
    path=os.path.join(PROJECT_ROOT, "ml/recognition/arcface/weights/arcface_r100.pth"), 
    device=device
)

# Load precomputed face features and names
images_names, images_embs = read_features(
    feature_path=os.path.join(PROJECT_ROOT, "datasets/face_features/feature")
)


def load_config(file_name):
    """
    Load a YAML configuration file.

    Args:
        file_name (str): The path to the YAML configuration file.

    Returns:
        dict: The loaded configuration as a dictionary.
    """
    with open(file_name, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


@torch.no_grad()
def get_feature(face_image):
    """
    Extract features from a face image.

    Args:
        face_image: The input face image.

    Returns:
        numpy.ndarray: The extracted features.
    """
    face_preprocess = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Resize((112, 112)),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.7, 0.7, 0.7]),
        ]
    )

    # Convert to RGB
    face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)

    # Preprocess image (BGR)
    face_image = face_preprocess(face_image).unsqueeze(0).to(device)

    # Inference to get feature
    emb_img_face = recognizer(face_image).cpu().numpy()

    # Convert to array
    images_emb = emb_img_face / np.linalg.norm(emb_img_face)

    return images_emb


def recognition(face_image):
    """
    Recognize a face image.

    Args:
        face_image: The input face image.

    Returns:
        tuple: A tuple containing the recognition score and name.
    """
    # Get feature from face
    query_emb = get_feature(face_image)

    score, id_min = compare_encodings(query_emb, images_embs)
    name = images_names[id_min]
    score = score[0]

    return score, name


def main():
    """Main function to process face detection and recognition."""
    cap = cv2.VideoCapture(0)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame.")
                break

            # Detect faces
            detection_results = detector.detect(image=frame)

            if detection_results is not None:
                bboxes, landmarks = detection_results

                for bbox, landmark in zip(bboxes, landmarks):
                    bbox = np.squeeze(bbox)  # Ensure bbox is a flat array
                    if len(bbox) >= 4:
                        x_min, y_min, x_max, y_max = bbox[:4].astype(int)

                        face_alignment = norm_crop(img=frame, landmark=landmark)

                        score, name = recognition(face_image=face_alignment)
                        if name is not None:
                            if score < 0.4:  # 0.25
                                caption = "UNKNOWN"
                            else:
                                caption = f"{name}: {score:.2f}"

                            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                            cv2.putText(
                                frame,
                                caption,
                                (x_min, y_min - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,
                                (0, 255, 0),
                                2,
                            )

            cv2.imshow("Face Recognition", frame)

            # Check for user exit input
            ch = cv2.waitKey(1)
            if ch == 27 or ch == ord("q") or ch == ord("Q"):
                print("Exiting...")
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
