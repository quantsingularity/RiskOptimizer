import unittest

import requests

from core.logging import get_logger

logger = get_logger(__name__)

# Assuming the backend is running on localhost:8000
BASE_URL = "http://localhost:8000/api/v1"


class TestAuthAPI(unittest.TestCase):

    def setUp(self):
        # Ensure the backend is running before tests
        try:
            requests.get(f"{BASE_URL}/health")
        except requests.exceptions.ConnectionError:
            self.fail(
                "Backend not running. Please start the backend server before running integration tests."
            )

        self.test_user_email = "integration_test@example.com"
        self.test_user_username = "integration_test_user"
        self.test_user_password = "SecurePassword123!"

        # Clean up any existing test user before each test
        self._cleanup_test_user()

    def tearDown(self):
        # Clean up test user after each test
        self._cleanup_test_user()

    def _cleanup_test_user(self):
        # This is a simplified cleanup. In a real scenario, you might have an admin endpoint
        # or direct database access for cleanup.
        try:
            # Attempt to log in to get a token for deletion if user exists
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password,
            }
            login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            if login_response.status_code == 200:
                access_token = login_response.json()["access_token"]
                headers = {"Authorization": f"Bearer {access_token}"}
                # Assuming a delete user endpoint exists (might require admin privileges)
                # This is a placeholder and needs to be implemented in the actual API
                # delete_response = requests.delete(f"{BASE_URL}/users/{user_id}", headers=headers)
                # if delete_response.status_code == 204:
                #     print(f"Cleaned up user {self.test_user_email}")
                pass  # For now, we'll just register and let subsequent tests handle conflicts
        except Exception as e:
            logger.info(f"Error during test user cleanup: {e}")

    def test_1_register_user(self):
        # Test user registration
        register_data = {
            "email": self.test_user_email,
            "username": self.test_user_username,
            "password": self.test_user_password,
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        self.assertEqual(
            response.status_code,
            201,
            f"Expected 201, got {response.status_code}: {response.text}",
        )
        data = response.json()
        self.assertIn("user", data)
        self.assertIn("tokens", data)
        self.assertEqual(data["user"]["email"], self.test_user_email)
        self.assertIn("access_token", data["tokens"])
        self.assertIn("refresh_token", data["tokens"])

    def test_2_login_user(self):
        # Ensure user is registered first (depends on test_1_register_user)
        self.test_1_register_user()  # Register the user if not already

        # Test user login
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password,
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        self.assertEqual(
            response.status_code,
            200,
            f"Expected 200, got {response.status_code}: {response.text}",
        )
        data = response.json()
        self.assertIn("user", data)
        self.assertIn("tokens", data)
        self.assertEqual(data["user"]["email"], self.test_user_email)
        self.assertIn("access_token", data["tokens"])
        self.assertIn("refresh_token", data["tokens"])

    def test_3_register_existing_user(self):
        # Register user first
        self.test_1_register_user()

        # Attempt to register again with the same email
        register_data = {
            "email": self.test_user_email,
            "username": "another_username",
            "password": "AnotherPassword123!",
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        self.assertEqual(
            response.status_code,
            409,
            f"Expected 409, got {response.status_code}: {response.text}",
        )
        self.assertIn("User with email", response.json()["detail"])

    def test_4_login_invalid_credentials(self):
        # Test login with wrong password
        login_data = {"email": self.test_user_email, "password": "wrongpassword"}
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        self.assertEqual(
            response.status_code,
            401,
            f"Expected 401, got {response.status_code}: {response.text}",
        )
        self.assertIn("Invalid email or password", response.json()["detail"])

    def test_5_refresh_token(self):
        # Login to get tokens
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password,
        }
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        self.assertEqual(login_response.status_code, 200)
        refresh_token = login_response.json()["tokens"]["refresh_token"]

        # Use refresh token to get new access token
        refresh_data = {"refresh_token": refresh_token}
        response = requests.post(f"{BASE_URL}/auth/refresh", json=refresh_data)
        self.assertEqual(
            response.status_code,
            200,
            f"Expected 200, got {response.status_code}: {response.text}",
        )
        data = response.json()
        self.assertIn("access_token", data)
        self.assertIn("token_type", data)
        self.assertIn("expires_in", data)

    def test_6_logout_user(self):
        # Login to get tokens
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password,
        }
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        self.assertEqual(login_response.status_code, 200)
        tokens = login_response.json()["tokens"]

        # Logout
        logout_data = {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
        }
        response = requests.post(f"{BASE_URL}/auth/logout", json=logout_data)
        self.assertEqual(
            response.status_code,
            200,
            f"Expected 200, got {response.status_code}: {response.text}",
        )
        self.assertIn("message", response.json())
        self.assertEqual(response.json()["message"], "Successfully logged out.")

        # Try to use blacklisted access token
        headers = {"Authorization": f"Bearer {tokens["access_token"]}"}
        protected_response = requests.get(
            f"{BASE_URL}/users/me", headers=headers
        )  # Assuming a protected endpoint
        self.assertEqual(
            protected_response.status_code,
            401,
            f"Expected 401 after logout, got {protected_response.status_code}: {protected_response.text}",
        )


if __name__ == "__main__":
    unittest.main()
