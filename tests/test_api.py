import pytest
import requests
import os

# Get base URL from environment or default
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

class TestAPI:

    def test_health_endpoint(self):
        """Test /health returns 200 with status healthy and model_version key."""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("status") == "healthy", f"Expected status='healthy', got {data.get('status')}"
        assert "model_version" in data, "model_version key missing from /health response"

    def test_predict_returns_label_and_confidence(self):
        """Test /predict returns 200 with label, confidence 0-1, and model_version."""
        payload = {"text": "This is a great product!"}
        response = requests.post(f"{BASE_URL}/predict", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("label") in ["POSITIVE", "NEGATIVE"], f"Invalid label: {data.get('label')}"
        confidence = data.get("confidence")
        assert isinstance(confidence, (int, float)), f"confidence not numeric: {confidence}"
        assert 0 <= confidence <= 1, f"confidence out of range [0,1]: {confidence}"
        assert "model_version" in data, "model_version key missing from /predict response"

    def test_predict_negative_text(self):
        """Test /predict with negative sentiment text returns 200."""
        payload = {"text": "This is terrible and awful"}
        response = requests.post(f"{BASE_URL}/predict", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "label" in data, "label missing from response"
        assert "confidence" in data, "confidence missing from response"

    def test_health_returns_model_version_unstable(self):
        """Test /health returns model_version == 'unstable-v1' exactly."""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("model_version") == "unstable-v1", \
            f"Expected model_version='unstable-v1', got {data.get('model_version')}"
