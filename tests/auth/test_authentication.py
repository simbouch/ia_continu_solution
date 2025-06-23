"""
Test suite for authentication and authorization
"""

import requests

from tests.conftest import API_BASE_URL


class TestAuthentication:
    """Test authentication functionality"""

    def test_login_endpoint_with_valid_credentials(self, test_user_credentials):
        """Test login with valid user credentials"""
        response = requests.post(
            f"{API_BASE_URL}/auth/login", json=test_user_credentials, timeout=10
        )

        assert response.status_code == 200
        data = response.json()

        # Check required login response fields
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 50  # JWT tokens are long

    def test_login_endpoint_with_admin_credentials(self, admin_user_credentials):
        """Test login with admin credentials"""
        response = requests.post(
            f"{API_BASE_URL}/auth/login", json=admin_user_credentials, timeout=10
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data

    def test_login_endpoint_with_invalid_username(self):
        """Test login with invalid username"""
        invalid_credentials = {
            "username": "nonexistent_user",
            "password": "any_password",
        }

        response = requests.post(
            f"{API_BASE_URL}/auth/login", json=invalid_credentials, timeout=10
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_login_endpoint_with_invalid_password(self):
        """Test login with invalid password"""
        invalid_credentials = {"username": "testuser", "password": "wrong_password"}

        response = requests.post(
            f"{API_BASE_URL}/auth/login", json=invalid_credentials, timeout=10
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_login_endpoint_with_missing_username(self):
        """Test login with missing username field"""
        invalid_data = {"password": "test123"}

        response = requests.post(
            f"{API_BASE_URL}/auth/login", json=invalid_data, timeout=10
        )

        assert response.status_code == 422  # Validation error

    def test_login_endpoint_with_missing_password(self):
        """Test login with missing password field"""
        invalid_data = {"username": "testuser"}

        response = requests.post(
            f"{API_BASE_URL}/auth/login", json=invalid_data, timeout=10
        )

        assert response.status_code == 422  # Validation error

    def test_login_endpoint_with_empty_credentials(self):
        """Test login with empty credentials"""
        empty_credentials = {"username": "", "password": ""}

        response = requests.post(
            f"{API_BASE_URL}/auth/login", json=empty_credentials, timeout=10
        )

        assert response.status_code in [
            401,
            422,
        ]  # Either auth error or validation error

    def test_logout_endpoint_with_valid_token(self, auth_headers):
        """Test logout with valid authentication token"""
        response = requests.post(
            f"{API_BASE_URL}/auth/logout", headers=auth_headers, timeout=10
        )

        assert response.status_code == 404  # Logout endpoint not implemented

    def test_logout_endpoint_without_token(self):
        """Test logout without authentication token"""
        response = requests.post(f"{API_BASE_URL}/auth/logout", timeout=10)

        assert response.status_code == 404  # Logout endpoint not implemented

    def test_logout_endpoint_with_invalid_token(self):
        """Test logout with invalid authentication token"""
        invalid_headers = {"Authorization": "Bearer invalid_token"}

        response = requests.post(
            f"{API_BASE_URL}/auth/logout", headers=invalid_headers, timeout=10
        )

        assert response.status_code == 404  # Logout endpoint not implemented

    def test_me_endpoint_with_valid_token(self, auth_headers):
        """Test current user info endpoint with valid token"""
        response = requests.get(
            f"{API_BASE_URL}/auth/me", headers=auth_headers, timeout=10
        )

        assert response.status_code == 200
        data = response.json()

        # Check required user info fields
        assert "username" in data
        assert "role" in data
        assert data["username"] == "testuser"
        assert data["role"] == "user"

    def test_me_endpoint_without_token(self):
        """Test current user info endpoint without token"""
        response = requests.get(f"{API_BASE_URL}/auth/me", timeout=10)

        assert response.status_code == 403  # API returns 403 for missing auth

    def test_users_endpoint_with_admin_token(self, admin_auth_headers):
        """Test users list endpoint with admin token"""
        response = requests.get(
            f"{API_BASE_URL}/auth/users", headers=admin_auth_headers, timeout=10
        )

        assert response.status_code == 200
        data = response.json()

        # The endpoint currently returns an empty list (not implemented)
        assert isinstance(data, list)
        assert len(data) == 0  # Currently returns empty list

    def test_users_endpoint_with_regular_user_token(self, auth_headers):
        """Test users list endpoint with regular user token (should be forbidden)"""
        response = requests.get(
            f"{API_BASE_URL}/auth/users", headers=auth_headers, timeout=10
        )

        assert response.status_code == 403  # Forbidden for non-admin users

    def test_users_endpoint_without_token(self):
        """Test users list endpoint without authentication"""
        response = requests.get(f"{API_BASE_URL}/auth/users", timeout=10)

        assert response.status_code == 403  # API returns 403 for missing auth

    def test_token_expiration_handling(self):
        """Test that expired tokens are properly rejected"""
        # This would require a token with very short expiration
        # For now, we test with a malformed token
        expired_headers = {"Authorization": "Bearer expired.token.here"}

        response = requests.get(
            f"{API_BASE_URL}/auth/me", headers=expired_headers, timeout=10
        )

        assert response.status_code == 401  # API returns 401 for malformed tokens

    def test_token_format_validation(self):
        """Test that malformed tokens are rejected"""
        malformed_headers = {"Authorization": "InvalidFormat"}

        response = requests.get(
            f"{API_BASE_URL}/auth/me", headers=malformed_headers, timeout=10
        )

        assert response.status_code == 403  # API returns 403 for invalid format

    def test_bearer_token_prefix_required(self, auth_token):
        """Test that Bearer prefix is required for tokens"""
        # Token without Bearer prefix
        invalid_headers = {"Authorization": auth_token}

        response = requests.get(
            f"{API_BASE_URL}/auth/me", headers=invalid_headers, timeout=10
        )

        assert response.status_code == 403  # API returns 403 for missing Bearer prefix
