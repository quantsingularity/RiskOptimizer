from flask import Flask, jsonify, request
from web3 import Web3
import joblib
import pandas as pd
from pyportfolioopt import EfficientFrontier, risk_models, expected_returns

app = Flask(__name__)
w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))
model = joblib.load('../ai_models/optimization_model.pkl')

@app.route('/api/optimize', methods=['POST'])
def optimize_portfolio():
    data = request.json
    df = pd.DataFrame(data['historical_data'])
    
    # Calculate expected returns and covariance matrix
    mu = expected_returns.mean_historical_return(df)
    S = risk_models.sample_cov(df)
    
    # Optimize portfolio
    ef = EfficientFrontier(mu, S)
    ef.max_sharpe()
    weights = ef.clean_weights()
    
    return jsonify({
        'optimized_allocation': weights,
        'performance_metrics': ef.portfolio_performance()
    })

@app.route('/api/portfolio/<address>')
def get_portfolio(address):
    contract = w3.eth.contract(
        address='0x...',
        abi=PortfolioTracker_ABI
    )
    assets, allocations = contract.functions.getPortfolio(address).call()
    return jsonify({
        'assets': assets,
        'allocations': [a/10000 for a in allocations]  # Convert basis points to percentages
    })