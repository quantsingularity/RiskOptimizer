# code/backend/tests/conftest.py
import pytest
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the Flask app instance
# We need to ensure imports within app.py work correctly
# Adjust the import based on your actual app structure if needed
try:
    from app import app as flask_app
except ImportError as e:
    print(f"Error importing Flask app: {e}")
    print("Please ensure app.py is structured correctly and dependencies are installed.")
    # Provide a dummy app if import fails to allow pytest collection
    from flask import Flask
    flask_app = Flask(__name__)
    @flask_app.route('/')
    def dummy_index():
        return "Dummy App"

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Set testing configuration
    flask_app.config.update({
        "TESTING": True,
        # Add other test-specific configurations if needed
        # e.g., "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    # TODO: Add setup code here if needed (e.g., creating test database tables)

    yield flask_app

    # TODO: Add teardown code here if needed (e.g., dropping test database tables)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

