"""
Test suite for ML prediction endpoints
"""

import random
import time

import requests

from tests.conftest import API_BASE_URL


class TestPredictionEndpoints:
    """Test ML prediction functionality"""

    def test_predict_endpoint_requires_authentication(self, sample_prediction_data):
        """Test that predict endpoint requires authentication"""
        response = requests.post(
            f"{API_BASE_URL}/predict", json=sample_prediction_data, timeout=10
        )

        assert response.status_code == 403  # API returns 403 for missing auth

    def test_predict_endpoint_with_valid_token_and_data(
        self, auth_headers, sample_prediction_data
    ):
        """Test prediction with valid authentication and data"""
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=sample_prediction_data,
            headers=auth_headers,
            timeout=10,
        )

        assert response.status_code == 200
        data = response.json()

        # Check required prediction response fields
        assert "prediction" in data
        assert "confidence" in data
        assert "model_version" in data
        assert "timestamp" in data

    def test_predict_endpoint_returns_valid_prediction_data(
        self, auth_headers, sample_prediction_data
    ):
        """Test that prediction returns valid data types and ranges"""
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=sample_prediction_data,
            headers=auth_headers,
            timeout=10,
        )

        assert response.status_code == 200
        data = response.json()

        # Validate prediction data
        assert isinstance(data["prediction"], int)
        assert data["prediction"] in [0, 1]  # Binary classification
        assert isinstance(data["confidence"], int | float)
        assert 0.0 <= data["confidence"] <= 1.0
        assert isinstance(data["model_version"], str)
        assert data["model_version"].startswith("v")

    def test_predict_endpoint_with_invalid_features_format(self, auth_headers):
        """Test prediction with invalid features format"""
        invalid_data = {"features": "invalid"}

        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=invalid_data,
            headers=auth_headers,
            timeout=10,
        )

        assert response.status_code == 422  # Validation error

    def test_predict_endpoint_with_missing_features(self, auth_headers):
        """Test prediction with missing features field"""
        invalid_data = {"not_features": [0.5, 0.5]}

        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=invalid_data,
            headers=auth_headers,
            timeout=10,
        )

        assert response.status_code == 422  # Validation error

    def test_predict_endpoint_with_wrong_number_of_features(self, auth_headers):
        """Test prediction with wrong number of features"""
        invalid_data = {"features": [0.5]}  # Should be 2 features

        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=invalid_data,
            headers=auth_headers,
            timeout=10,
        )

        assert response.status_code == 422  # Validation error

    def test_predict_endpoint_with_extreme_feature_values(self, auth_headers):
        """Test prediction with extreme feature values"""
        extreme_data = {"features": [1000.0, -1000.0]}

        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=extreme_data,
            headers=auth_headers,
            timeout=10,
        )

        # Should still work but may have lower confidence
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "confidence" in data

    def test_predict_endpoint_response_time_under_threshold(
        self, auth_headers, sample_prediction_data
    ):
        """Test that prediction responds within acceptable time"""


        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=sample_prediction_data,
            headers=auth_headers,
            timeout=10,
        )
        response_time = time.time() - start_time

        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second

    def test_predict_endpoint_multiple_predictions_consistency(self, auth_headers):
        """Test that multiple predictions with same input are consistent"""
        test_data = {"features": [0.5, 0.5]}

        # Make multiple predictions
        predictions = []
        for _ in range(3):
            response = requests.post(
                f"{API_BASE_URL}/predict",
                json=test_data,
                headers=auth_headers,
                timeout=10,
            )
            assert response.status_code == 200
            predictions.append(response.json())

        # Check consistency
        first_prediction = predictions[0]["prediction"]
        first_confidence = predictions[0]["confidence"]

        for pred in predictions[1:]:
            assert pred["prediction"] == first_prediction
            assert abs(pred["confidence"] - first_confidence) < 0.001  # Small tolerance

    def test_generate_endpoint_requires_authentication(self, sample_generation_data):
        """Test that generate endpoint requires authentication"""
        response = requests.post(
            f"{API_BASE_URL}/generate", json=sample_generation_data, timeout=10
        )

        assert response.status_code == 403  # Generate endpoint requires auth

    def test_generate_endpoint_with_valid_token_and_data(
        self, auth_headers, sample_generation_data
    ):
        """Test data generation with valid authentication and data"""
        response = requests.post(
            f"{API_BASE_URL}/generate",
            json=sample_generation_data,
            headers=auth_headers,
            timeout=30,  # Generation might take longer
        )

        assert response.status_code == 200
        data = response.json()

        # Check required generation response fields (actual API format)
        assert "generation_id" in data
        assert "samples_created" in data
        assert "timestamp" in data

    def test_generate_endpoint_creates_correct_number_of_samples(self, auth_headers):
        """Test that data generation creates the requested number of samples"""


        time.sleep(1.0)  # Longer delay to prevent race conditions
        generation_id = random.randint(10000, 99999)  # Use random generation_id

        test_data = {"samples": 150, "generation_id": generation_id}  # Valid range is 100-10000

        response = requests.post(
            f"{API_BASE_URL}/generate", json=test_data, headers=auth_headers, timeout=30
        )

        if response.status_code != 200:
            print(f"Error response: {response.text}")

        assert response.status_code == 200
        data = response.json()
        assert data["samples_created"] == 150

    def test_generate_endpoint_with_invalid_sample_count(self, auth_headers):
        """Test data generation with invalid sample count"""
        invalid_data = {"samples": -10}

        response = requests.post(
            f"{API_BASE_URL}/generate",
            json=invalid_data,
            headers=auth_headers,
            timeout=10,
        )

        assert response.status_code == 422  # Validation error

    def test_generate_endpoint_with_excessive_sample_count(self, auth_headers):
        """Test data generation with excessive sample count"""
        excessive_data = {"samples": 100000}  # Very large number

        response = requests.post(
            f"{API_BASE_URL}/generate",
            json=excessive_data,
            headers=auth_headers,
            timeout=10,
        )

        # Should either reject or limit the request
        assert response.status_code in [422, 400]
