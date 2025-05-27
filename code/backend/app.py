"""
RiskOptimizer API - Main Application Entry Point

This module provides the main FastAPI application for the RiskOptimizer backend.
It handles portfolio optimization, risk analysis, and blockchain integration.
"""
import os
import sys
import logging
from typing import Dict, List, Any, Optional, Tuple, Union, cast
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from web3 import Web3
import pandas as pd
from pypfopt import EfficientFrontier, risk_models, expected_returns
import joblib

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import configuration and ABI definitions
from config import (
    API_HOST, API_PORT, DEBUG_MODE, 
    BLOCKCHAIN_PROVIDER, PORTFOLIO_TRACKER_ADDRESS,
    MODEL_PATH
)
from blockchain_abi import PORTFOLIO_TRACKER_ABI
from services.quant_analysis import RiskMetrics
from db.database import Database

# Configure logging
def setup_logging() -> logging.Logger:
    """Configure application logging with rotating file handler and console output."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger = logging.getLogger("riskoptimizer")
    logger.setLevel(logging.DEBUG if DEBUG_MODE else logging.INFO)
    
    # Create handlers
    file_handler = RotatingFileHandler(
        log_dir / "riskoptimizer.log", 
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    console_handler = logging.StreamHandler()
    
    # Set levels
    file_handler.setLevel(logging.DEBUG)
    console_handler.setLevel(logging.INFO)
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Initialize logger
logger = setup_logging()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize database connection
db = Database()

# Initialize Web3 connection
try:
    w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_PROVIDER))
    if w3.is_connected():
        logger.info(f"Connected to blockchain provider at {BLOCKCHAIN_PROVIDER}")
    else:
        logger.warning(f"Failed to connect to blockchain provider at {BLOCKCHAIN_PROVIDER}")
except Exception as e:
    logger.error(f"Error initializing Web3 connection: {e}")
    w3 = None

# Load AI model if available
model = None
try:
    if MODEL_PATH and os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        logger.info(f"Model loaded successfully from {MODEL_PATH}")
    else:
        logger.warning(f"Model path not found: {MODEL_PATH}")
except Exception as e:
    logger.error(f"Error loading model: {e}")


@app.route('/')
def index() -> Response:
    """Root endpoint that confirms API is running."""
    logger.debug("Root endpoint accessed")
    return jsonify({
        "status": "success",
        "message": "RiskOptimizer API is running"
    })


@app.route('/ping')
def health_check() -> Response:
    """Health check endpoint for monitoring and load balancers."""
    logger.debug("Health check endpoint accessed")
    return jsonify({
        "status": "healthy",
        "service": "RiskOptimizer API"
    })


@app.route('/api/optimize', methods=['POST'])
def optimize_portfolio() -> Response:
    """
    Optimize portfolio allocation based on historical data.
    
    Expects JSON payload with historical_data field containing price history.
    Returns optimized weights and performance metrics.
    """
    logger.info("Portfolio optimization requested")
    try:
        data = request.json
        if not data or 'historical_data' not in data:
            logger.warning("Invalid request data for portfolio optimization")
            return jsonify({
                'status': 'error',
                'message': 'Missing historical_data in request'
            }), 400
            
        df = pd.DataFrame(data['historical_data'])
        logger.debug(f"Processing historical data with shape {df.shape}")
        
        # Calculate expected returns and covariance matrix
        mu = expected_returns.mean_historical_return(df)
        S = risk_models.sample_cov(df)
        
        # Optimize portfolio
        ef = EfficientFrontier(mu, S)
        ef.max_sharpe()
        weights = ef.clean_weights()
        
        # Get performance metrics
        performance = ef.portfolio_performance()
        
        logger.info("Portfolio optimization completed successfully")
        return jsonify({
            'status': 'success',
            'optimized_allocation': weights,
            'performance_metrics': {
                'expected_return': float(performance[0]),
                'volatility': float(performance[1]),
                'sharpe_ratio': float(performance[2])
            }
        })
    except Exception as e:
        logger.error(f"Error in portfolio optimization: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


@app.route('/api/portfolio/<address>')
def get_portfolio(address: str) -> Response:
    """
    Get portfolio allocation from blockchain for a specific address.
    
    Args:
        address: Ethereum wallet address
        
    Returns:
        Portfolio assets and allocations
    """
    logger.info(f"Portfolio requested for address: {address}")
    try:
        # Validate Ethereum address
        if not w3 or not w3.is_connected():
            logger.error("Web3 connection not available")
            return jsonify({
                'status': 'error',
                'message': 'Blockchain connection not available'
            }), 503
            
        if not w3.is_address(address):
            logger.warning(f"Invalid Ethereum address: {address}")
            return jsonify({
                'status': 'error',
                'message': 'Invalid Ethereum address'
            }), 400
            
        # Get portfolio from blockchain
        contract = w3.eth.contract(
            address=PORTFOLIO_TRACKER_ADDRESS,
            abi=PORTFOLIO_TRACKER_ABI
        )
        
        assets, allocations = contract.functions.getPortfolio(address).call()
        logger.debug(f"Retrieved portfolio with {len(assets)} assets from blockchain")
        
        return jsonify({
            'status': 'success',
            'portfolio': {
                'assets': assets,
                'allocations': [a/10000 for a in allocations]  # Convert basis points to percentages
            }
        })
    except Exception as e:
        logger.error(f"Error retrieving portfolio from blockchain: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/portfolio/db/<address>')
def get_portfolio_from_db(address: str) -> Response:
    """
    Get portfolio from database instead of blockchain.
    
    Args:
        address: User wallet address
        
    Returns:
        Portfolio assets and allocations from database
    """
    logger.info(f"Portfolio requested from database for address: {address}")
    try:
        portfolio_data = db.get_portfolio(address)
        
        if not portfolio_data:
            logger.warning(f"Portfolio not found for address: {address}")
            return jsonify({
                'status': 'error',
                'message': 'Portfolio not found'
            }), 404
            
        # Format the response
        assets: List[str] = []
        allocations: List[float] = []
        
        for item in portfolio_data:
            assets.append(item['asset_symbol'])
            allocations.append(item['percentage'])
            
        logger.debug(f"Retrieved portfolio with {len(assets)} assets from database")
        return jsonify({
            'status': 'success',
            'portfolio': {
                'user_address': address,
                'assets': assets,
                'allocations': allocations
            }
        })
    except Exception as e:
        logger.error(f"Error retrieving portfolio from database: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/portfolio/save', methods=['POST'])
def save_portfolio() -> Response:
    """
    Save portfolio to database.
    
    Expects JSON payload with user_address and allocations.
    """
    logger.info("Save portfolio request received")
    try:
        data = request.json
        if not data:
            logger.warning("No data provided in save portfolio request")
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
            
        user_address = data.get('user_address')
        allocations = data.get('allocations', {})
        
        if not user_address or not allocations:
            logger.warning("Missing required fields in save portfolio request")
            return jsonify({
                'status': 'error',
                'message': 'User address and allocations are required'
            }), 400
            
        logger.debug(f"Saving portfolio for {user_address} with {len(allocations)} assets")
        success = db.save_portfolio(user_address, allocations)
        
        if success:
            logger.info(f"Portfolio saved successfully for {user_address}")
            return jsonify({
                'status': 'success',
                'message': 'Portfolio saved successfully'
            })
        else:
            logger.error(f"Failed to save portfolio for {user_address}")
            return jsonify({
                'status': 'error',
                'message': 'Failed to save portfolio'
            }), 500
    except Exception as e:
        logger.error(f"Error saving portfolio: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/risk/var', methods=['POST'])
def calculate_var() -> Response:
    """
    Calculate Value at Risk (VaR) for a given set of returns.
    
    Expects JSON payload with returns array and optional confidence level.
    """
    logger.info("VaR calculation requested")
    try:
        data = request.json
        if not data:
            logger.warning("No data provided in VaR calculation request")
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
            
        returns = data.get('returns', [])
        confidence = data.get('confidence', 0.95)
        
        if not returns:
            logger.warning("Returns data missing in VaR calculation request")
            return jsonify({
                'status': 'error',
                'message': 'Returns data is required'
            }), 400
            
        logger.debug(f"Calculating VaR with {len(returns)} data points and {confidence} confidence")
        var = RiskMetrics.calculate_var(returns, confidence)
        
        logger.info("VaR calculation completed successfully")
        return jsonify({
            'status': 'success',
            'value_at_risk': float(var)
        })
    except Exception as e:
        logger.error(f"Error calculating VaR: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


def main() -> None:
    """
    Main entry point for the application.
    Sets up logging, initializes connections, and starts the Flask server.
    """
    try:
        logger.info("Starting RiskOptimizer API")
        logger.info(f"Server configuration: host={API_HOST}, port={API_PORT}, debug={DEBUG_MODE}")
        
        # Test database connection
        if db.connect():
            logger.info("Database connection successful")
            db.disconnect()
        else:
            logger.warning("Database connection failed")
        
        # Start Flask app
        app.run(host=API_HOST, port=API_PORT, debug=DEBUG_MODE)
    except Exception as e:
        logger.critical(f"Failed to start application: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
