import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
from web3 import Web3
import pandas as pd

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

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Web3 connection
w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_PROVIDER))

# Initialize database connection
db = Database()

# Import PyPortfolioOpt for portfolio optimization
from pypfopt import EfficientFrontier, risk_models, expected_returns

# Load AI model if available
try:
    import joblib
    model = joblib.load(MODEL_PATH)
    print(f"Model loaded successfully from {MODEL_PATH}")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

@app.route('/')
def index():
    return jsonify({
        "status": "success",
        "message": "RiskOptimizer API is running"
    })

@app.route('/api/optimize', methods=['POST'])
def optimize_portfolio():
    try:
        data = request.json
        df = pd.DataFrame(data['historical_data'])
        
        # Calculate expected returns and covariance matrix
        mu = expected_returns.mean_historical_return(df)
        S = risk_models.sample_cov(df)
        
        # Optimize portfolio
        ef = EfficientFrontier(mu, S)
        ef.max_sharpe()
        weights = ef.clean_weights()
        
        # Get performance metrics
        performance = ef.portfolio_performance()
        
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
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/portfolio/<address>')
def get_portfolio(address):
    try:
        # Validate Ethereum address
        if not w3.isAddress(address):
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
        
        return jsonify({
            'status': 'success',
            'portfolio': {
                'assets': assets,
                'allocations': [a/10000 for a in allocations]  # Convert basis points to percentages
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/portfolio/db/<address>')
def get_portfolio_from_db(address):
    """Get portfolio from database instead of blockchain"""
    try:
        portfolio_data = db.get_portfolio(address)
        
        if not portfolio_data:
            return jsonify({
                'status': 'error',
                'message': 'Portfolio not found'
            }), 404
            
        # Format the response
        assets = []
        allocations = []
        
        for item in portfolio_data:
            assets.append(item['asset_symbol'])
            allocations.append(item['percentage'])
            
        return jsonify({
            'status': 'success',
            'portfolio': {
                'user_address': address,
                'assets': assets,
                'allocations': allocations
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/portfolio/save', methods=['POST'])
def save_portfolio():
    """Save portfolio to database"""
    try:
        data = request.json
        user_address = data.get('user_address')
        allocations = data.get('allocations', {})
        
        if not user_address or not allocations:
            return jsonify({
                'status': 'error',
                'message': 'User address and allocations are required'
            }), 400
            
        success = db.save_portfolio(user_address, allocations)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Portfolio saved successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to save portfolio'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/risk/var', methods=['POST'])
def calculate_var():
    try:
        data = request.json
        returns = data.get('returns', [])
        confidence = data.get('confidence', 0.95)
        
        if not returns:
            return jsonify({
                'status': 'error',
                'message': 'Returns data is required'
            }), 400
            
        var = RiskMetrics.calculate_var(returns, confidence)
        
        return jsonify({
            'status': 'success',
            'value_at_risk': float(var)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host=API_HOST, port=API_PORT, debug=DEBUG_MODE)
