"""
WSGI entry point for the RiskOptimizer API.
Used for production deployment with WSGI servers like Gunicorn.
"""

from riskoptimizer.app import app

if __name__ == "__main__":
    app.run()
