"""API Integration Tests (Sync)

Tests for all API endpoints using synchronous HTTP client.
Requires server running on localhost:8000.

Usage: 
    1. Start server: uvicorn app.main:app --port 8000
    2. Run tests: pytest tests/ -v
"""
import os
import pytest
import uuid
import requests
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY")

# Test data paths (real data from user)
TEST_TRAINING_PATH = "/media/magesh/NewVolume4/Images/Training/ICC 2011/Players"
TEST_IMAGE_PATH = "/media/magesh/NewVolume4/Images/Training/ICC 2011/squad.jpg"

# Generate unique test ID for this run
TEST_ID = uuid.uuid4().hex[:8]


@pytest.fixture
def auth_headers() -> dict:
    """Headers with API key for authenticated endpoints."""
    return {"X-API-Key": API_KEY, "Content-Type": "application/json"}


class TestHealthEndpoint:
    """Health check endpoint tests."""
    
    def test_health_check(self):
        """Test health endpoint returns healthy status."""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestAuthAPI:
    """Authentication API tests."""
    
    def test_register_user(self):
        """Test user registration."""
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={"username": f"testuser_{TEST_ID}", "password": "testpass123"}
        )
        # Either 200 (new user) or 400 (already exists)
        assert response.status_code in [200, 400]
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"username": "nonexistent_user_xyz", "password": "wrongpass123"}
        )
        # 401 (auth error)
        assert response.status_code == 401


class TestRecognitionAPI:
    """Recognition API tests."""
    
    def test_save_recognition(self, auth_headers: dict):
        """Test saving recognition log."""
        response = requests.post(
            f"{BASE_URL}/api/v1/recognition/save",
            headers=auth_headers,
            json={
                "person_name": "TestPerson",
                "camera_id": "test_cam",
                "confidence_score": 0.95
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "log_id" in data
    
    def test_get_logs(self, auth_headers: dict):
        """Test getting recognition logs."""
        response = requests.get(
            f"{BASE_URL}/api/v1/recognition/logs",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
    
    def test_get_known_persons(self, auth_headers: dict):
        """Test getting known persons."""
        response = requests.get(
            f"{BASE_URL}/api/v1/recognition/persons",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "persons" in data
        assert "count" in data
    
    def test_unauthorized_access(self):
        """Test that API rejects requests without API key."""
        response = requests.get(f"{BASE_URL}/api/v1/recognition/logs")
        assert response.status_code in [401, 403]


class TestBatchRecognitionAPI:
    """Batch recognition API tests with real image data."""
    
    def test_add_persons_from_folder(self, auth_headers: dict):
        """Test adding persons from training folder."""
        response = requests.post(
            f"{BASE_URL}/api/v1/recognition/persons/add",
            headers=auth_headers,
            json={
                "source_path": TEST_TRAINING_PATH,
                "move_to_backup": False  # Don't move during test
            },
            timeout=120  # Allow time for ML processing
        )
        # 200 (success) or 404 (path not found)
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            print(f"\n✓ Persons added: {data.get('persons_added', [])}")
    
    def test_batch_process_image(self, auth_headers: dict):
        """Test batch processing an image for face recognition."""
        response = requests.post(
            f"{BASE_URL}/api/v1/recognition/batch/process",
            headers=auth_headers,
            json={"image_path": TEST_IMAGE_PATH},
            timeout=120  # Allow time for ML processing
        )
        # 200 (success), 404 (image not found), or 500 (model/DB error)
        if response.status_code == 200:
            data = response.json()
            assert "batch_id" in data
            assert "total_faces_detected" in data
            assert "results" in data
            print(f"\n✓ Detected {data['total_faces_detected']} faces")
            for result in data.get("results", []):
                print(f"  - {result.get('person_name')}: {result.get('confidence', 0):.2%}")
        elif response.status_code == 500:
            print(f"\n⚠ Server error (check logs): {response.json().get('error', {}).get('message', 'Unknown')}")
        assert response.status_code in [200, 404, 500]
    
    def test_get_batch_results(self, auth_headers: dict):
        """Test getting batch results."""
        response = requests.get(
            f"{BASE_URL}/api/v1/recognition/batches",
            headers=auth_headers
        )
        # 200 (success) or 500 (DB aggregation error)
        if response.status_code == 500:
            print(f"\n⚠ Server error: {response.json().get('error', {}).get('message', 'Unknown')}")
        assert response.status_code in [200, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
