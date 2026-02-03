# Smart EMS Face Recognition System

A production-ready face recognition system with configurable detection and recognition models, FastAPI REST API, and MongoDB integration.

## ✨ Features

- **Face Detection**: YOLOv12 or SCRFD (configurable)
- **Face Recognition**: AdaFace or ArcFace (configurable)
- **REST API**: FastAPI with batch recognition endpoints
- **Database**: MongoDB for logging recognition results
- **Centralized Config**: Change models in one place (`ml/config.py`)
- **Clean Architecture**: API → Controller → Service → Repository

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/Smiley-Magesh/smart-ems-face-recognition.git
cd smart-ems-face-recognition
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download Model Weights

**⚠️ IMPORTANT**: Model weights are not included due to size. Download them to the paths below:

| Model | Size | Download | Save To |
|-------|------|----------|---------|
| **SCRFD** | 3MB | [Download](https://github.com/deepinsight/insightface/releases/download/v0.7/scrfd_2.5g_bnkps.onnx) | `ml/detection/scrfd/weights/scrfd_2.5g_bnkps.onnx` |
| **YOLOv12** | 5MB | [Download](https://github.com/akanametov/yolo-face/releases/download/v1.0.0/yolov12n-face.pt) | `ml/detection/yolov12/weights/yolov12n-face.pt` |
| **ArcFace** | 249MB | [Download](https://drive.google.com/file/d/1o1m-eT38Q3P86BMsT4QcNfDgQMVlEZvA/view) | `ml/recognition/arcface/weights/arcface_r100.pth` |
| **AdaFace** | 683MB | [Download](https://github.com/mk-minchul/AdaFace/releases/download/Pretrained/adaface_ir100_webface12m.ckpt) | `ml/recognition/adaface/weights/adaface_ir100_webface12m.ckpt` |

Or use wget/curl:
```bash
# SCRFD (included in repo)
# YOLOv12 (included in repo)

# ArcFace
wget -O ml/recognition/arcface/weights/arcface_r100.pth \
  "https://drive.google.com/uc?export=download&id=1o1m-eT38Q3P86BMsT4QcNfDgQMVlEZvA"

# AdaFace
wget -O ml/recognition/adaface/weights/adaface_ir100_webface12m.ckpt \
  "https://github.com/mk-minchul/AdaFace/releases/download/Pretrained/adaface_ir100_webface12m.ckpt"
```

### 5. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings (MongoDB URL, API key, etc.)
```

### 6. Run Application
```bash
python run.py
```

API available at: **http://localhost:8000/docs**

## ⚙️ Configuration

Change models in **one place** - `ml/config.py`:

```python
# Detection model: "scrfd" or "yolov12"
DETECTION_MODEL = "yolov12"

# Recognition model: "arcface" or "adaface"
RECOGNITION_MODEL = "adaface"
```

> **Note**: When changing `RECOGNITION_MODEL`, you must re-add persons using the API to regenerate embeddings.

## 📡 API Endpoints

### Batch Recognition
```bash
# Process an image and recognize faces
POST /api/v1/recognition/batch/process
Content-Type: application/json
X-API-Key: your-api-key

{
  "image_path": "/path/to/group_photo.jpg"
}
```

### Add Training Persons
```bash
# Add persons from folders (each folder = one person)
POST /api/v1/recognition/persons/add
Content-Type: application/json
X-API-Key: your-api-key

{
  "source_path": "/path/to/training_images"
}
```

Expected folder structure:
```
training_images/
├── Person1/
│   ├── photo1.jpg
│   ├── photo2.jpg
├── Person2/
│   ├── photo1.jpg
...
```

## 🏗️ Project Structure

```
├── app/                    # FastAPI Application
│   ├── api/v1/            # API routes
│   ├── controllers/       # Request orchestration
│   ├── services/          # Business logic
│   ├── repositories/      # Database operations
│   ├── schemas/           # Pydantic models
│   └── models/            # Database models
├── ml/                     # Machine Learning
│   ├── config.py          # Model configuration
│   ├── factory.py         # Model factory functions
│   ├── detection/         # Face detectors (SCRFD, YOLOv12)
│   ├── recognition/       # Face recognizers (ArcFace, AdaFace)
│   └── alignment/         # Face alignment utilities
├── datasets/              # Training data (not in repo)
│   ├── data/              # Aligned face images
│   ├── face_features/     # Pre-computed embeddings
│   └── backup/            # Original images
├── docs/                  # Documentation
├── http/                  # HTTP test files
└── scripts/               # Utility scripts
```

## 🔧 Requirements

- Python 3.8+
- MongoDB
- CUDA (optional, for GPU acceleration)

## 📄 License

MIT

## 🙏 Acknowledgements

- [InsightFace](https://github.com/deepinsight/insightface) - SCRFD & ArcFace
- [AdaFace](https://github.com/mk-minchul/AdaFace) - Quality-adaptive recognition
- [YOLOv12-Face](https://github.com/akanametov/yolo-face) - YOLO face detection
