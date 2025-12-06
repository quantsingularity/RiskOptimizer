import unittest

import requests

from core.logging import get_logger

logger = get_logger(__name__)

# Assuming the backend is running on localhost:8000
BASE_URL = "http://localhost:8000/api/v1"


class TestRiskAPI(unittest.TestCase):

    def setUp(self):
        # Ensure the backend is running before tests
        try:
            requests.get(f"{BASE_URL}/health")
        except requests.exceptions.ConnectionError:
            self.fail(
                "Backend not running. Please start the backend server before running integration tests."
            )

        self.test_user_email = "risk_test@example.com"
        self.test_user_username = "risk_test_user"
        self.test_user_password = "SecureRisk123!"
        self.access_token = None
        self.refresh_token = None
        self.user_id = None

        # Register and login a user for testing
        self._register_and_login_user()

    def tearDown(self):
        # Logout and cleanup user after tests
        self._logout_user()
        self._cleanup_test_user()

    def _register_and_login_user(self):
        # Register
        register_data = {
            "email": self.test_user_email,
            "username": self.test_user_username,
            "password": self.test_user_password,
        }
        register_response = requests.post(
            f"{BASE_URL}/auth/register", json=register_data
        )
        if register_response.status_code == 409:  # User already exists
            logger.info(
                f"User {self.test_user_email} already exists, proceeding to login."
            )
        elif register_response.status_code != 201:
            self.fail(
                f"Failed to register user: {register_response.status_code} - {register_response.text}"
            )

        # Login
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password,
        }
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        self.assertEqual(
            login_response.status_code,
            200,
            f"Failed to login user: {login_response.status_code} - {login_response.text}",
        )
        data = login_response.json()
        self.access_token = data["tokens"]["access_token"]
        self.refresh_token = data["tokens"]["refresh_token"]
        self.user_id = data["user"]["id"]

    def _logout_user(self):
        if self.access_token and self.refresh_token:
            logout_data = {
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
            }
            requests.post(f"{BASE_URL}/auth/logout", json=logout_data)

    def _cleanup_test_user(self):
        # In a real application, you'd have an an admin endpoint to delete users.
        # For this test, we'll assume the user can be deleted via a direct call if needed
        # or rely on database cleanup between test runs.
        pass

    def get_auth_headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    def test_1_calculate_var(self):
        returns = [0.01, 0.02, -0.03, 0.04, -0.05]
        confidence = 0.95
        data = {"returns": returns, "confidence": confidence}
        response = requests.post(
            f"{BASE_URL}/risk/var", json=data, headers=self.get_auth_headers()
        )
        self.assertEqual(
            response.status_code,
            200,
            f"Expected 200, got {response.status_code}: {response.text}",
        )
        result = response.json()
        self.assertIn("value_at_risk", result)
        self.assertIsInstance(float(result["value_at_risk"]), float)

    def test_2_calculate_cvar(self):
        returns = [0.01, 0.02, -0.03, 0.04, -0.05]
        confidence = 0.95
        data = {"returns": returns, "confidence": confidence}
        response = requests.post(
            f"{BASE_URL}/risk/cvar", json=data, headers=self.get_auth_headers()
        )
        self.assertEqual(
            response.status_code,
            200,
            f"Expected 200, got {response.status_code}: {response.text}",
        )
        result = response.json()
        self.assertIn("conditional_value_at_risk", result)
        self.assertIsInstance(float(result["conditional_value_at_risk"]), float)

    def test_3_calculate_sharpe_ratio(self):
        returns = [0.01, 0.02, 0.03, 0.04, 0.05]
        risk_free_rate = 0.01
        data = {"returns": returns, "risk_free_rate": risk_free_rate}
        response = requests.post(
            f"{BASE_URL}/risk/sharpe-ratio", json=data, headers=self.get_auth_headers()
        )
        self.assertEqual(
            response.status_code,
            200,
            f"Expected 200, got {response.status_code}: {response.text}",
        )
        result = response.json()
        self.assertIn("sharpe_ratio", result)
        self.assertIsInstance(float(result["sharpe_ratio"]), float)

    def test_4_calculate_max_drawdown(self):
        returns = [0.01, -0.02, 0.03, -0.04, 0.05]
        data = {"returns": returns}
        response = requests.post(
            f"{BASE_URL}/risk/max-drawdown", json=data, headers=self.get_auth_headers()
        )
        self.assertEqual(
            response.status_code,
            200,
            f"Expected 200, got {response.status_code}: {response.text}",
        )
        result = response.json()
        self.assertIn("max_drawdown", result)
        self.assertIsInstance(float(result["max_drawdown"]), float)

    def test_5_calculate_portfolio_risk_metrics(self):
        returns = [0.01, 0.02, -0.03, 0.04, -0.05]
        confidence = 0.95
        risk_free_rate = 0.01
        data = {
            "returns": returns,
            "confidence": confidence,
            "risk_free_rate": risk_free_rate,
        }
        response = requests.post(
            f"{BASE_URL}/risk/portfolio-metrics",
            json=data,
            headers=self.get_auth_headers(),
        )
        self.assertEqual(
            response.status_code,
            200,
            f"Expected 200, got {response.status_code}: {response.text}",
        )
        result = response.json()
        self.assertIn("expected_return", result)
        self.assertIn("volatility", result)
        self.assertIn("value_at_risk", result)
        self.assertIn("conditional_var", result)
        self.assertIn("sharpe_ratio", result)
        self.assertIn("max_drawdown", result)
        self.assertIsInstance(float(result["expected_return"]), float)

    def test_6_calculate_efficient_frontier(self):
        returns = {
            "asset1": [0.01, 0.02, 0.03, 0.04, 0.05],
            "asset2": [0.005, 0.015, 0.025, 0.035, 0.045],
        }
        data = {
            "returns": returns,
            "min_weight": 0.1,
            "max_weight": 0.9,
            "risk_free_rate": 0.01,
            "points": 10,
        }
        response = requests.post(
            f"{BASE_URL}/risk/efficient-frontier",
            json=data,
            headers=self.get_auth_headers(),
        )
        self.assertEqual(
            response.status_code,
            200,
            f"Expected 200, got {response.status_code}: {response.text}",
        )
        result = response.json()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn("expected_return", result[0])
        self.assertIn("volatility", result[0])
        self.assertIn("sharpe_ratio", result[0])
        self.assertIn("weights", result[0])


if __name__ == "__main__":
    unittest.main()
