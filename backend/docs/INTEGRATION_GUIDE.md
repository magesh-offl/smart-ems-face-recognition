# Integration Guide: Connect recognize2.py to FastAPI Backend

This guide shows how to modify your `recognize2.py` to send face recognition data to the FastAPI backend.

## Quick Start

### 1. Update recognize2.py

Add the API client import at the top of your `recognize2.py`:

```python
import sys
sys.path.append('/path/to/backend')  # Adjust path as needed
from app.utils.client import RecognitionAPIClient
```

### 2. Initialize the Client

In the `main()` function, create the API client:

```python
def main():
    """Main function to process face detection and recognition."""
    
    # Initialize API client
    api_client = RecognitionAPIClient(
        base_url="http://localhost:8000",
        api_key="your-api-key"  # Set this in backend/.env
    )
    
    cap = cv2.VideoCapture(0)
    # ... rest of your code
```

### 3. Send Recognition Data

When a face is recognized, send the data to the API:

```python
score, name = recognition(face_image=face_alignment)

if name is not None:
    if score < 0.4:
        caption = "UNKNOWN"
    else:
        caption = f"{name}: {score:.2f}"
        
        # Send to backend API
        result = api_client.save_recognition(
            person_name=name,
            camera_id="camera_01",  # Change based on your camera
            confidence_score=score
        )
        
        if result.get("success"):
            print(f"Recognition saved: {result.get('log_id')}")
        else:
            print(f"Error saving: {result.get('error')}")
    
    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
    cv2.putText(...)
```

## Full Example Integration

Here's a complete example of how to modify `recognize2.py`:

```python
import threading
import time
import sys

import cv2
import numpy as np
import torch
import yaml
from torchvision import transforms

# Add backend to path
sys.path.append('/media/magesh/NewVolume2/Projects/Python/AppDemo/Comp_visn/backend')
from app.utils.client import RecognitionAPIClient

from face_alignment.alignment import norm_crop
from face_detection.scrfd.detector import SCRFD
from face_detection.yolov5_face.detector import Yolov5Face
from face_recognition.arcface.model import iresnet_inference
from face_recognition.arcface.utils import compare_encodings, read_features

# Device configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Face detector (choose one)
detector = SCRFD(model_file="face_detection/scrfd/weights/scrfd_2.5g_bnkps.onnx")

# Face recognizer
recognizer = iresnet_inference(
    model_name="r100", path="face_recognition/arcface/weights/arcface_r100.pth", device=device
)

# Load precomputed face features and names
images_names, images_embs = read_features(feature_path="./datasets/face_features/feature")

# Initialize API client
api_client = RecognitionAPIClient(
    base_url="http://localhost:8000",
    api_key="your-api-key-change-this"  # Must match API_KEY in backend/.env
)


def load_config(file_name):
    """Load a YAML configuration file."""
    with open(file_name, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


@torch.no_grad()
def get_feature(face_image):
    """Extract features from a face image."""
    face_preprocess = transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize((112, 112)),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.7, 0.7, 0.7]),
    ])

    face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
    face_image = face_preprocess(face_image).unsqueeze(0).to(device)
    emb_img_face = recognizer(face_image).cpu().numpy()
    images_emb = emb_img_face / np.linalg.norm(emb_img_face)

    return images_emb


def recognition(face_image):
    """Recognize a face image."""
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
                    bbox = np.squeeze(bbox)
                    if len(bbox) >= 4:
                        x_min, y_min, x_max, y_max = bbox[:4].astype(int)

                        face_alignment = norm_crop(img=frame, landmark=landmark)
                        score, name = recognition(face_image=face_alignment)

                        if name is not None:
                            if score < 0.4:
                                caption = "UNKNOWN"
                            else:
                                caption = f"{name}: {score:.2f}"
                                
                                # Send to backend API
                                result = api_client.save_recognition(
                                    person_name=name,
                                    camera_id="camera_01",
                                    confidence_score=float(score)
                                )
                                
                                if result.get("success"):
                                    print(f"✓ Saved: {name} (ID: {result.get('log_id')})")
                                else:
                                    print(f"✗ Error: {result.get('error')}")

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
```

## Environment Setup

### Backend Side (.env)

```env
# MongoDB Configuration
MONGO_DB_URL=mongodb://127.0.0.1:27017
MONGO_DB_NAME=face_recognition_db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_ENV=development

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# API Key Configuration
API_KEY=your-api-key-change-this

# Logging
LOG_LEVEL=INFO
```

### Client Side (recognize2.py)

Make sure the `API_KEY` in your code matches the backend's `API_KEY` in `.env`.

## Starting the Backend

```bash
cd /media/magesh/NewVolume2/Projects/Python/AppDemo/Comp_visn/backend
source benv/bin/activate
python run.py
```

The API will be available at `http://localhost:8000`

## Starting recognize2.py

```bash
cd /media/magesh/NewVolume2/Projects/Python/AppDemo/Comp_visn/face_recognition
source /path/to/venv/bin/activate  # Your face recognition environment
python recognize2.py
```

## API Client Methods

The `RecognitionAPIClient` provides these methods:

### Save Recognition
```python
api_client.save_recognition(person_name, camera_id, confidence_score=None)
```

### Get All Logs
```python
api_client.get_all_logs(skip=0, limit=10)
```

### Filter Logs
```python
api_client.filter_logs(
    person_name=None,
    camera_id=None,
    start_date=None,
    end_date=None,
    skip=0,
    limit=10
)
```

### Get Specific Log
```python
api_client.get_log(log_id)
```

### Update Log
```python
api_client.update_log(log_id, person_name=None, camera_id=None, confidence_score=None)
```

### Delete Log
```python
api_client.delete_log(log_id)
```

## Error Handling

The client methods return dictionaries. Check for errors:

```python
result = api_client.save_recognition("John", "camera_01", 0.95)

if result.get("success"):
    log_id = result.get("log_id")
    print(f"Saved with ID: {log_id}")
else:
    error = result.get("error")
    print(f"Failed to save: {error}")
```

## Troubleshooting

### Connection Error
- Ensure backend is running: `python run.py`
- Check if port 8000 is accessible
- Verify `base_url` in client initialization

### Authentication Error (API Key)
- Ensure `API_KEY` in code matches backend's `.env`
- Make sure `X-API-Key` header is being sent

### MongoDB Error
- Ensure MongoDB is running locally
- Check connection string in backend `.env`

### 1-Hour Cooldown Not Working
- This is automatic on the backend
- The same person at the same camera within 1 hour will increment counter
- Check MongoDB for `detection_count` field in logs
