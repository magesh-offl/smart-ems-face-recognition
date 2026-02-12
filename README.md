# Smart EMS Face Recognition System

A production-ready, full-stack face recognition system designed for educational institutions. It features configurable detection and recognition models (YOLOv12, AdaFace), a robust FastAPI backend, and a modern React frontend with MongoDB integration.

![Dashboard Preview](frontend/public/vite.svg)  
*(Replace with actual screenshot if available)*

## ✨ Key Features

- **Advanced AI**: Uses state-of-the-art models for face detection (YOLOv12/SCRFD) and recognition (AdaFace/ArcFace).
- **Full Stack Solution**: complete separation of concerns with a RESTful API backend and a responsive React frontend.
- **Configurable**: Easily switch between models via `backend/ml/config.py`.
- **Database Integrated**: Checkpoints and recognition history logged to MongoDB.
- **User-Friendly UI**: Modern dashboard for managing students, training models, and viewing recognition history.

---

## 🚀 Getting Started

For detailed installation instructions, including manual ML model downloads and environment configuration, please see the **[Setup Guide](setup.md)**.

### Quick Summary

1.  **Clone the Repo**: `git clone https://github.com/Smiley-Magesh/smart-ems-face-recognition.git`
2.  **Backend Setup**:
    *   Create venv & install requirements.
    *   **Download ML Models** (Critical step! See setup.md).
    *   Configure `.env`.
    *   Run with `uvicorn`.
3.  **Frontend Setup**:
    *   `npm install`
    *   `npm run dev`

---

## 📖 Usage Workflow

### 1. 🎓 Admission & Training
1.  Navigate to the **Admission** page.
2.  Add a new student (ID, Name, Course).
3.  **Train Face**:
    *   Use the webcam to capture samples OR upload images.
    *   The system aligns and extracts features automatically.
    *   Click "Save" to register the student in the database.

### 2. 🔍 Recognition
1.  Go to the **Recognition** page.
2.  **Upload & Recognize**:
    *   Upload a group photo or single image.
    *   The system detects all faces and attempts to match them against the database.
    *   **Results**: Matched faces are identified with confidence scores. Unknown faces are marked.
3.  **History**: View past recognition logs in the "History" tab or the dedicated "Recognition History" page.

### 3. 👥 Manage Persons
1.  Use the **Persons** page to view all registered individuals.
2.  Manage their associated images and re-train if necessary.

---

## �️ Technology Stack

- **Backend**: Python 3.10+, FastAPI, PyTorch, Ultralytics (YOLO), InsightFace (SCRFD/ArcFace).
- **Frontend**: React 18, Vite, TypeScript, TailwindCSS/CSS Modules.
- **Database**: MongoDB.
- **Tools**: Docker (optional), Git.

## 📄 License
MIT

## 🙏 Acknowledgements

- [InsightFace](https://github.com/deepinsight/insightface) - SCRFD & ArcFace
- [AdaFace](https://github.com/mk-minchul/AdaFace) - Quality-adaptive recognition
- [YOLOv12-Face](https://github.com/akanametov/yolo-face) - YOLO face detection
