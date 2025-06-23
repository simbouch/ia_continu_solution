"""
End-to-end integration tests for complete ML workflow
"""

import time

import pytest
import requests

from tests.conftest import API_BASE_URL, PREFECT_URL, UPTIME_KUMA_URL


class TestEndToEndWorkflow:
    """Test complete ML workflow integration"""

    def test_complete_ml_workflow_authentication_to_prediction(
        self, test_user_credentials
    ):
        """Test complete workflow from authentication to prediction"""
        # Step 1: Authenticate
        login_response = requests.post(
            f"{API_BASE_URL}/auth/login", json=test_user_credentials, timeout=10
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 2: Check system health
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        assert health_response.status_code == 200
        assert health_response.json()["status"] == "ok"

        # Step 3: Generate training data
        generate_response = requests.post(
            f"{API_BASE_URL}/generate",
            json={"samples": 100},
            headers=headers,
            timeout=30,
        )
        assert generate_response.status_code == 200
        generation_data = generate_response.json()
        assert "generation_id" in generation_data
        assert generation_data["samples_created"] == 100

        # Step 4: Make predictions
        prediction_response = requests.post(
            f"{API_BASE_URL}/predict",
            json={"features": [0.5, 0.5]},
            headers=headers,
            timeout=10,
        )
        assert prediction_response.status_code == 200
        prediction_data = prediction_response.json()
        assert "prediction" in prediction_data
        assert "confidence" in prediction_data
        assert 0.0 <= prediction_data["confidence"] <= 1.0

        # Step 5: Check model info
        model_info_response = requests.get(
            f"{API_BASE_URL}/model/info", headers=headers, timeout=10
        )
        assert model_info_response.status_code == 200
        model_data = model_info_response.json()
        assert model_data["model_loaded"] is True
        assert "model_version" in model_data
        assert "model_type" in model_data

    def test_service_availability_integration(self):
        """Test that all required services are available"""
        services_to_test = [
            (API_BASE_URL, "/health"),
            (UPTIME_KUMA_URL, "/"),
            (PREFECT_URL, "/api/health"),
        ]

        for base_url, endpoint in services_to_test:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
                # Accept various success codes depending on service
                assert response.status_code in [200, 201, 302]
            except requests.exceptions.RequestException:
                pytest.fail(f"Service {base_url} is not accessible")

    def test_data_persistence_across_requests(self, auth_headers):
        """Test that data persists across multiple requests"""
        import time
        time.sleep(1.0)  # Prevent database race conditions

        # Generate data
        generate_response = requests.post(
            f"{API_BASE_URL}/generate",
            json={"samples": 150},  # Valid range is 100-10000
            headers=auth_headers,
            timeout=30,
        )
        assert generate_response.status_code == 200
        generation_id = generate_response.json()["generation_id"]

        # Make multiple predictions to ensure model is working
        predictions = []
        for i in range(3):
            prediction_response = requests.post(
                f"{API_BASE_URL}/predict",
                json={"features": [0.1 * i, 0.2 * i]},
                headers=auth_headers,
                timeout=10,
            )
            assert prediction_response.status_code == 200
            predictions.append(prediction_response.json())

        # Verify all predictions were successful
        assert len(predictions) == 3
        for pred in predictions:
            assert "prediction" in pred
            assert "confidence" in pred
            assert "model_version" in pred

    def test_error_handling_and_recovery(self, auth_headers):
        """Test system error handling and recovery"""
        # Test with invalid prediction data
        invalid_response = requests.post(
            f"{API_BASE_URL}/predict",
            json={"features": "invalid"},
            headers=auth_headers,
            timeout=10,
        )
        assert invalid_response.status_code == 422

        # Test that system recovers and normal requests still work
        valid_response = requests.post(
            f"{API_BASE_URL}/predict",
            json={"features": [0.5, 0.5]},
            headers=auth_headers,
            timeout=10,
        )
        assert valid_response.status_code == 200

    def test_concurrent_requests_handling(self, auth_headers):
        """Test system handling of concurrent requests"""
        import concurrent.futures

        def make_prediction(features):
            return requests.post(
                f"{API_BASE_URL}/predict",
                json={"features": features},
                headers=auth_headers,
                timeout=10,
            )

        # Make concurrent predictions
        test_features = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6], [0.7, 0.8]]

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(make_prediction, features) for features in test_features
            ]
            responses = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert "prediction" in data
            assert "confidence" in data

    def test_authentication_token_lifecycle(self, test_user_credentials):
        """Test complete authentication token lifecycle"""
        # Login
        login_response = requests.post(
            f"{API_BASE_URL}/auth/login", json=test_user_credentials, timeout=10
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Use token for authenticated request
        me_response = requests.get(
            f"{API_BASE_URL}/auth/me", headers=headers, timeout=10
        )
        assert me_response.status_code == 200

        # Verify token works for protected endpoints
        prediction_response = requests.post(
            f"{API_BASE_URL}/predict",
            json={"features": [0.5, 0.5]},
            headers=headers,
            timeout=10,
        )
        assert prediction_response.status_code == 200

    def test_ml_pipeline_performance_under_load(self, auth_headers):
        """Test ML pipeline performance under moderate load"""

        # Measure response times for multiple requests
        response_times = []

        for i in range(10):
            start_time = time.time()
            response = requests.post(
                f"{API_BASE_URL}/predict",
                json={"features": [0.1 * i, 0.2 * i]},
                headers=auth_headers,
                timeout=10,
            )
            end_time = time.time()

            assert response.status_code == 200
            response_times.append(end_time - start_time)

        # Check performance metrics
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)

        assert avg_response_time < 1.0  # Average under 1 second
        assert max_response_time < 2.0  # Max under 2 seconds

    def test_data_generation_and_model_consistency(self, auth_headers):
        """Test that data generation doesn't break model consistency"""
        # Get initial model info
        initial_model_response = requests.get(
            f"{API_BASE_URL}/model/info", headers=auth_headers, timeout=10
        )
        assert initial_model_response.status_code == 200
        initial_model = initial_model_response.json()

        # Make initial prediction
        initial_prediction_response = requests.post(
            f"{API_BASE_URL}/predict",
            json={"features": [0.5, 0.5]},
            headers=auth_headers,
            timeout=10,
        )
        assert initial_prediction_response.status_code == 200
        initial_prediction = initial_prediction_response.json()

        # Generate new data
        generate_response = requests.post(
            f"{API_BASE_URL}/generate",
            json={"samples": 100},
            headers=auth_headers,
            timeout=30,
        )
        assert generate_response.status_code == 200

        # Make prediction with same features
        post_generation_prediction_response = requests.post(
            f"{API_BASE_URL}/predict",
            json={"features": [0.5, 0.5]},
            headers=auth_headers,
            timeout=10,
        )
        assert post_generation_prediction_response.status_code == 200
        post_generation_prediction = post_generation_prediction_response.json()

        # Predictions should be consistent (same model)
        assert (
            initial_prediction["prediction"] == post_generation_prediction["prediction"]
        )
        assert (
            abs(
                initial_prediction["confidence"]
                - post_generation_prediction["confidence"]
            )
            < 0.1
        )

    def test_system_health_monitoring_integration(self):
        """Test integration with monitoring systems"""
        # Test API health
        api_health = requests.get(f"{API_BASE_URL}/health", timeout=10)
        assert api_health.status_code == 200

        # Test Uptime Kuma accessibility
        try:
            uptime_response = requests.get(UPTIME_KUMA_URL, timeout=10)
            assert uptime_response.status_code in [200, 302]  # May redirect to login
        except requests.exceptions.RequestException:
            pytest.skip("Uptime Kuma not accessible")

        # Test Prefect health
        try:
            prefect_response = requests.get(f"{PREFECT_URL}/api/health", timeout=10)
            assert prefect_response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.skip("Prefect not accessible")
