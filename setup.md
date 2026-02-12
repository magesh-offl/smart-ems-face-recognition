# Project Setup Guide

This guide details how to set up the Smart EMS Face Recognition System, including the Backend (FastAPI), Frontend (React/Vite), Database (MongoDB), and Machine Learning models.

## 📋 Prerequisites

Ensure you have the following installed:
- **Python 3.10+**
- **Node.js 18+** (and `npm`)
- **MongoDB** (running locally or accessible remotely)
- **Git**

---

## 🏗️ 1. Backend Setup

### 1.1. Clone and Navigate
```bash
git clone https://github.com/Smiley-Magesh/smart-ems-face-recognition.git
cd smart-ems-face-recognition/backend
```

### 1.2. Virtual Environment
Create and activate a Python virtual environment:

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 1.3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 1.4. Environment Configuration
Copy the example environment file and configure it:
```bash
cp .env.example .env
```
Edit `.env` to ensure `MONGO_DB_URL` points to your running MongoDB instance.

### 1.5. 🧠 Manual ML Model Download (Required)
The ML models are too large for Git. You must download them manually and place them in the correct `backend/ml/...` directories.

| Model | Description | Download Link | Destination Path (rel to `backend/`) |
|-------|-------------|---------------|-------------------------------------|
| **YOLOv12** | Face Detection (Default) | [yolov12n-face.pt](https://github.com/akanametov/yolo-face/releases/download/v1.0.0/yolov12n-face.pt) | `ml/detection/yolov12/weights/yolov12n-face.pt` |
| **SCRFD** | Face Detection (Fallback) | [scrfd_2.5g_bnkps.onnx](https://github.com/deepinsight/insightface/releases/download/v0.7/scrfd_2.5g_bnkps.onnx) | `ml/detection/scrfd/weights/scrfd_2.5g_bnkps.onnx` |
| **AdaFace** | Face Recognition (Default) | [adaface_ir100_webface12m.ckpt](https://github.com/mk-minchul/AdaFace/releases/download/Pretrained/adaface_ir100_webface12m.ckpt) | `ml/recognition/adaface/weights/adaface_ir100_webface12m.ckpt` |
| **ArcFace** | Face Recognition (Fallback) | [arcface_r100.pth](https://drive.google.com/file/d/1o1m-eT38Q3P86BMsT4QcNfDgQMVlEZvA/view) | `ml/recognition/arcface/weights/arcface_r100.pth` |

**Directory Creation:**
Ensure the `weights` directories exist:
```bash
mkdir -p ml/detection/yolov12/weights
mkdir -p ml/detection/scrfd/weights
mkdir -p ml/recognition/adaface/weights
mkdir -p ml/recognition/arcface/weights
```

---

## 🎨 2. Frontend Setup

### 2.1. Navigate to Frontend
Open a new terminal and navigate to the frontend directory:
```bash
cd smart-ems-face-recognition/frontend
```

### 2.2. Install Dependencies
```bash
npm install
```

### 2.3. Environment Configuration
Create a `.env` file in the `frontend` root if it doesn't exist (usually not required if using defaults, but good for custom API URLs):
```bash
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env
```

---

## 🚀 3. Running the Application

### 3.1. Start Backend Server
In your backend terminal (with venv activated):
```bash
# Run with live reload
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Backend will be available at: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

### 3.2. Start Frontend Development Server
In your frontend terminal:
```bash
npm run dev
```
Frontend will be available at: `http://localhost:5173` (or the port shown in terminal).

---

## 🧪 4. Verification Workflow

1.  **Access Frontend**: Go to `http://localhost:5173`.
2.  **Login**: Use the Super Admin credentials (default in `backend/app/core/config.py` or your `.env`):
    *   Email: `superadmin@ems.com`
    *   Password: (Check logs on first run for generated password if not set in `.env`)
3.  **Dashboard**: You should see the main dashboard with statistics.
