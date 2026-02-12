"""Authentication and RBAC Tests

Tests for authentication flows, role-based access control, and admin APIs.
Requires server running on localhost:8000.

Usage: 
    1. Start server: uvicorn app.main:app --port 8000
    2. Run tests: pytest tests/test_auth_rbac.py -v
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
API_VERSION = "v1"
AUTH_URL = f"{BASE_URL}/api/{API_VERSION}/auth"
ADMIN_URL = f"{BASE_URL}/api/{API_VERSION}/admin"

# Test data
TEST_ID = uuid.uuid4().hex[:8]
SUPER_ADMIN_USERNAME = "superadmin"
SUPER_ADMIN_PASSWORD = "admin@123"


class TestAuthenticationFlows:
    """Test authentication flows: login, register, forgot-password."""
    
    @pytest.fixture
    def admin_token(self) -> str:
        """Get admin access token for authenticated requests."""
        response = requests.post(
            f"{AUTH_URL}/login",
            json={"username": SUPER_ADMIN_USERNAME, "password": SUPER_ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Admin login failed: {response.json()}"
        return response.json()["access_token"]
    
    @pytest.fixture
    def admin_auth_headers(self, admin_token) -> dict:
        """Headers with Bearer token for admin requests."""
        return {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
    
    def test_login_returns_user_info(self):
        """Test that login returns user info with role."""
        response = requests.post(
            f"{AUTH_URL}/login",
            json={"username": SUPER_ADMIN_USERNAME, "password": SUPER_ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check token fields
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        
        # Check user info
        assert "user" in data, "Login response must include user info"
        user = data["user"]
        assert user["username"] == SUPER_ADMIN_USERNAME
        assert "role" in user
        assert user["role"] == "super_admin"
        assert "email" in user
        assert "user_id" in user
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials returns 401."""
        response = requests.post(
            f"{AUTH_URL}/login",
            json={"username": "nonexistent_user", "password": "wrongpass"}
        )
        assert response.status_code == 401
    
    def test_register_new_user(self):
        """Test user registration with email."""
        test_username = f"testuser_{TEST_ID}"
        response = requests.post(
            f"{AUTH_URL}/register",
            json={
                "username": test_username,
                "password": "testpass123",
                "email": f"{test_username}@test.com"
            }
        )
        # Either 200 (new user) or 400/409 (already exists)
        assert response.status_code in [200, 400, 409]
        if response.status_code == 200:
            data = response.json()
            assert "user_id" in data
            assert data["username"] == test_username
    
    def test_register_duplicate_username_fails(self):
        """Test that duplicate username registration fails."""
        # First registration
        test_username = f"duplicate_{TEST_ID}"
        requests.post(
            f"{AUTH_URL}/register",
            json={
                "username": test_username,
                "password": "pass123",
                "email": f"{test_username}@test.com"
            }
        )
        
        # Second registration with same username should fail
        response = requests.post(
            f"{AUTH_URL}/register",
            json={
                "username": test_username,
                "password": "pass456",
                "email": f"{test_username}2@test.com"
            }
        )
        assert response.status_code in [400, 409]
    
    def test_forgot_password_creates_request(self):
        """Test forgot password creates a reset request."""
        response = requests.post(
            f"{AUTH_URL}/forgot-password",
            json={"username": SUPER_ADMIN_USERNAME}
        )
        # 200 for valid user, 404 for not found
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "message" in data
    
    def test_forgot_password_nonexistent_user(self):
        """Test forgot password for nonexistent user returns 404."""
        response = requests.post(
            f"{AUTH_URL}/forgot-password",
            json={"username": "definitely_not_a_user_xyz123"}
        )
        assert response.status_code == 404


class TestRBACProtection:
    """Test role-based access control on protected endpoints."""
    
    @pytest.fixture
    def admin_token(self) -> str:
        """Get admin access token."""
        response = requests.post(
            f"{AUTH_URL}/login",
            json={"username": SUPER_ADMIN_USERNAME, "password": SUPER_ADMIN_PASSWORD}
        )
        return response.json()["access_token"]
    
    @pytest.fixture
    def admin_auth_headers(self, admin_token) -> dict:
        """Headers with admin Bearer token."""
        return {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
    
    def test_admin_endpoint_without_token_fails(self):
        """Test admin endpoints reject requests without token."""
        response = requests.get(f"{ADMIN_URL}/students")
        assert response.status_code in [401, 403]
    
    def test_admin_endpoint_with_invalid_token_fails(self):
        """Test admin endpoints reject invalid tokens."""
        response = requests.get(
            f"{ADMIN_URL}/students",
            headers={"Authorization": "Bearer invalid_token_xyz"}
        )
        assert response.status_code == 401
    
    def test_admin_can_access_students(self, admin_auth_headers):
        """Test admin can access student list endpoint."""
        response = requests.get(
            f"{ADMIN_URL}/students",
            headers=admin_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "students" in data
        assert "count" in data
    
    def test_admin_can_access_password_resets(self, admin_auth_headers):
        """Test admin can access password reset requests."""
        response = requests.get(
            f"{ADMIN_URL}/password-resets",
            headers=admin_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "requests" in data


class TestAdminStudentManagement:
    """Test admin student management APIs."""
    
    @pytest.fixture
    def admin_auth_headers(self) -> dict:
        """Get admin auth headers."""
        response = requests.post(
            f"{AUTH_URL}/login",
            json={"username": SUPER_ADMIN_USERNAME, "password": SUPER_ADMIN_PASSWORD}
        )
        token = response.json()["access_token"]
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def test_get_courses(self, admin_auth_headers):
        """Test getting course list."""
        response = requests.get(
            f"{ADMIN_URL}/courses",
            headers=admin_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "courses" in data
    
    def test_create_course(self, admin_auth_headers):
        """Test creating a new course."""
        # Use multipart form data
        response = requests.post(
            f"{ADMIN_URL}/courses",
            headers={"Authorization": admin_auth_headers["Authorization"]},
            data={
                "name": f"Test Course {TEST_ID}",
                "section": "A",
                "description": "Test course for pytest"
            }
        )
        # 200 (created) or 400/409 (already exists)
        assert response.status_code in [200, 400, 409]
        if response.status_code == 200:
            data = response.json()
            assert "course_id" in data
    
    def test_list_students(self, admin_auth_headers):
        """Test listing all students."""
        response = requests.get(
            f"{ADMIN_URL}/students",
            headers=admin_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "students" in data
        assert isinstance(data["students"], list)
    
    def test_get_nonexistent_student_returns_404(self, admin_auth_headers):
        """Test getting nonexistent student returns 404."""
        response = requests.get(
            f"{ADMIN_URL}/students/STU99999999",
            headers=admin_auth_headers
        )
        assert response.status_code == 404


class TestPasswordResetManagement:
    """Test password reset admin flow."""
    
    @pytest.fixture
    def admin_auth_headers(self) -> dict:
        """Get admin auth headers."""
        response = requests.post(
            f"{AUTH_URL}/login",
            json={"username": SUPER_ADMIN_USERNAME, "password": SUPER_ADMIN_PASSWORD}
        )
        token = response.json()["access_token"]
        return {
            "Authorization": f"Bearer {token}",
        }
    
    def test_list_password_resets(self, admin_auth_headers):
        """Test listing password reset requests."""
        response = requests.get(
            f"{ADMIN_URL}/password-resets",
            headers=admin_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "requests" in data
        assert "pending_count" in data
    
    def test_complete_nonexistent_reset_returns_404(self, admin_auth_headers):
        """Test completing nonexistent reset returns 404."""
        response = requests.post(
            f"{ADMIN_URL}/password-resets/nonexistent123/complete",
            headers=admin_auth_headers
        )
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
