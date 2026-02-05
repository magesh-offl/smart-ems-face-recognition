"""Client module for API integration"""
import requests
from typing import Optional
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class RecognitionAPIClient:
    """Client for communicating with Face Recognition API"""
    
    def __init__(self, base_url: str, api_key: str = None):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL of the API server
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            self.headers["X-API-Key"] = api_key
    
    def save_recognition(self, person_name: str, camera_id: str,
                        confidence_score: Optional[float] = None) -> dict:
        """
        Save face recognition data.
        
        Args:
            person_name: Name of recognized person
            camera_id: Camera ID that detected the face
            confidence_score: Confidence score (0.0-1.0)
        
        Returns:
            Response dictionary with log_id
        """
        url = f"{self.base_url}/api/v1/recognition/save"
        data = {
            "person_name": person_name,
            "camera_id": camera_id,
            "confidence_score": confidence_score
        }
        
        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=5)
            response.raise_for_status()
            logger.info(f"Recognition saved: {person_name} from {camera_id}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to save recognition: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_all_logs(self, skip: int = 0, limit: int = 10) -> dict:
        """Get all recognition logs."""
        url = f"{self.base_url}/api/v1/recognition/logs"
        params = {"skip": skip, "limit": limit}
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch logs: {str(e)}")
            return {"error": str(e)}
    
    def filter_logs(self, person_name: Optional[str] = None,
                   camera_id: Optional[str] = None,
                   start_date: Optional[str] = None,
                   end_date: Optional[str] = None,
                   skip: int = 0, limit: int = 10) -> dict:
        """Filter recognition logs."""
        url = f"{self.base_url}/api/v1/recognition/filter"
        params = {
            "skip": skip,
            "limit": limit
        }
        
        if person_name:
            params["person_name"] = person_name
        if camera_id:
            params["camera_id"] = camera_id
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to filter logs: {str(e)}")
            return {"error": str(e)}
    
    def get_log(self, log_id: str) -> dict:
        """Get specific recognition log."""
        url = f"{self.base_url}/api/v1/recognition/logs/{log_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch log: {str(e)}")
            return {"error": str(e)}
    
    def update_log(self, log_id: str, person_name: Optional[str] = None,
                  camera_id: Optional[str] = None,
                  confidence_score: Optional[float] = None) -> dict:
        """Update recognition log."""
        url = f"{self.base_url}/api/v1/recognition/logs/{log_id}"
        data = {}
        
        if person_name is not None:
            data["person_name"] = person_name
        if camera_id is not None:
            data["camera_id"] = camera_id
        if confidence_score is not None:
            data["confidence_score"] = confidence_score
        
        try:
            response = requests.put(url, json=data, headers=self.headers, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update log: {str(e)}")
            return {"error": str(e)}
    
    def delete_log(self, log_id: str) -> dict:
        """Delete recognition log."""
        url = f"{self.base_url}/api/v1/recognition/logs/{log_id}"
        
        try:
            response = requests.delete(url, headers=self.headers, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to delete log: {str(e)}")
            return {"error": str(e)}
