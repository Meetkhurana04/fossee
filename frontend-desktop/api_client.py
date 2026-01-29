# frontend-desktop/api_client.py
"""
API Client for Desktop Application

Handles all HTTP communication with the Django backend.
Uses requests library for synchronous API calls.
"""

import requests
from typing import Optional, Dict, Any


class APIClient:
    """
    Client for communicating with the Django REST API.
    
    Provides methods for:
    - File upload
    - Dataset retrieval
    - History management
    - PDF download
    - Authentication
    """
    
    def __init__(self, base_url: str = "http://localhost:8000/api"):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL for the Django API
        """
        self.base_url = base_url
        self.token: Optional[str] = None
        self.session = requests.Session()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token if available"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Token {self.token}"
        return headers
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and raise exceptions for errors.
        
        Args:
            response: Response object from requests
            
        Returns:
            JSON response data
            
        Raises:
            Exception: If response status is not OK
        """
        if response.status_code >= 400:
            error_msg = response.json().get('error', 'Unknown error')
            raise Exception(f"API Error: {error_msg}")
        return response.json()
    
    def upload_csv(self, file_path: str) -> Dict[str, Any]:
        """
        Upload a CSV file to the backend.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Response with dataset information
        """
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.split('/')[-1], f, 'text/csv')}
            headers = {}
            if self.token:
                headers["Authorization"] = f"Token {self.token}"
            
            response = self.session.post(
                f"{self.base_url}/upload/",
                files=files,
                headers=headers
            )
        
        return self._handle_response(response)
    
    def get_dataset(self, dataset_id: int) -> Dict[str, Any]:
        """
        Get a specific dataset by ID.
        
        Args:
            dataset_id: ID of the dataset
            
        Returns:
            Dataset details including raw data and summary
        """
        response = self.session.get(
            f"{self.base_url}/dataset/{dataset_id}/",
            headers=self._get_headers()
        )
        return self._handle_response(response)
    
    def get_latest_dataset(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recently uploaded dataset.
        
        Returns:
            Latest dataset or None if no datasets exist
        """
        try:
            response = self.session.get(
                f"{self.base_url}/dataset/latest/",
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception:
            return None
    
    def get_history(self) -> list:
        """
        Get upload history (last 5 datasets).
        
        Returns:
            List of dataset summaries
        """
        response = self.session.get(
            f"{self.base_url}/history/",
            headers=self._get_headers()
        )
        return self._handle_response(response)
    
    def get_summary(self, dataset_id: int) -> Dict[str, Any]:
        """
        Get summary statistics for a dataset.
        
        Args:
            dataset_id: ID of the dataset
            
        Returns:
            Summary statistics
        """
        response = self.session.get(
            f"{self.base_url}/summary/{dataset_id}/",
            headers=self._get_headers()
        )
        return self._handle_response(response)
    
    def download_pdf(self, dataset_id: int, save_path: str) -> bool:
        """
        Download PDF report for a dataset.
        
        Args:
            dataset_id: ID of the dataset
            save_path: Path to save the PDF file
            
        Returns:
            True if successful
        """
        headers = {}
        if self.token:
            headers["Authorization"] = f"Token {self.token}"
        
        response = self.session.get(
            f"{self.base_url}/pdf/{dataset_id}/",
            headers=headers,
            stream=True
        )
        
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        return False
    
    def delete_dataset(self, dataset_id: int) -> bool:
        """
        Delete a dataset.
        
        Args:
            dataset_id: ID of the dataset
            
        Returns:
            True if successful
        """
        response = self.session.delete(
            f"{self.base_url}/dataset/{dataset_id}/delete/",
            headers=self._get_headers()
        )
        return response.status_code == 204
    
    # ============== Authentication ==============
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Login and get authentication token.
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            User info and token
        """
        response = self.session.post(
            f"{self.base_url}/auth/login/",
            json={"username": username, "password": password}
        )
        
        result = self._handle_response(response)
        self.token = result.get('token')
        return result
    
    def register(self, username: str, password: str, email: str = "") -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            username: Desired username
            password: Desired password
            email: Optional email address
            
        Returns:
            User info and token
        """
        response = self.session.post(
            f"{self.base_url}/auth/register/",
            json={"username": username, "password": password, "email": email}
        )
        
        result = self._handle_response(response)
        self.token = result.get('token')
        return result
    
    def logout(self) -> None:
        """Logout and clear token"""
        if self.token:
            try:
                self.session.post(
                    f"{self.base_url}/auth/logout/",
                    headers=self._get_headers()
                )
            except Exception:
                pass
        self.token = None