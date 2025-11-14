import pandas as pd
import numpy as np
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
import os
from datetime import datetime, timedelta

# --- Configuration and Data Loading ---

DATA_DIR = "data"
TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "BTC-USD", "ETH-USD"]

def load_prices(tickers: list, data_dir: str = DATA_DIR) -> pd.DataFrame:
    """Loads historical 'Close' price data for a list of tickers."""
    all_data = {}
    for ticker in tickers:
        file_name = f"{ticker.replace('-', '_')}_historical.csv"
        file_path = os.path.join(data_dir, file_name)
        
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, index_col=0, parse_dates=True)
            all_data[ticker] = df['Close']
        else:
            print(f"Warning: Data file not found for {ticker} at {file_path}")
            
    if not all_data:
        raise FileNotFoundError("No data files were loaded. Run data_ingestion.py first.")
        
    # Combine all series into a single DataFrame, forward-filling missing values
    prices = pd.DataFrame(all_data).ffill().dropna()
    return prices

# --- Core Portfolio Optimization Functions ---

def mean_variance_optimization(prices: pd.DataFrame, target_risk: float = 0.20) -> dict:
    """
    Performs Markowitz Mean-Variance Optimization to find the portfolio
    with the maximum Sharpe ratio and the minimum volatility.
    """
    print("\n--- Mean-Variance Optimization (Markowitz) ---")
    
    # 1. Calculate expected returns and sample covariance matrix
    mu = expected_returns.mean_historical_return(prices)
    S = risk_models.sample_cov(prices)
    
    # 2. Initialize the Efficient Frontier object
    ef = EfficientFrontier(mu, S)
    
    # 3. Max Sharpe Ratio Portfolio
    raw_weights_max_sharpe = ef.max_sharpe()
    cleaned_weights_max_sharpe = ef.clean_weights()
    
    print("\nMax Sharpe Ratio Portfolio Weights:")
    print(cleaned_weights_max_sharpe)
    
    performance_max_sharpe = ef.portfolio_performance(verbose=True)
    
    # 4. Min Volatility Portfolio
    ef_min_vol = EfficientFrontier(mu, S)
    raw_weights_min_vol = ef_min_vol.min_volatility()
    cleaned_weights_min_vol = ef_min_vol.clean_weights()
    
    print("\nMin Volatility Portfolio Weights:")
    print(cleaned_weights_min_vol)
    
    performance_min_vol = ef_min_vol.portfolio_performance(verbose=True)
    
    return {
        "max_sharpe_weights": cleaned_weights_max_sharpe,
        "max_sharpe_performance": performance_max_sharpe,
        "min_vol_weights": cleaned_weights_min_vol,
        "min_vol_performance": performance_min_vol,
    }

def discrete_allocation_suggestion(prices: pd.DataFrame, weights: dict, total_portfolio_value: float = 100000.0) -> dict:
    """
    Calculates the number of shares to purchase for a given set of weights.
    """
    print(f"\n--- Discrete Allocation Suggestion (Total Value: ${total_portfolio_value:,.2f}) ---")
    
    latest_prices = get_latest_prices(prices)
    
    da = DiscreteAllocation(weights, latest_prices, total_portfolio_value=total_portfolio_value)
    
    allocation, leftover = da.lp_portfolio()
    
    print("Discrete Allocation:")
    print(allocation)
    print(f"Funds remaining: ${leftover:,.2f}")
    
    return {
        "allocation": allocation,
        "leftover": leftover
    }

def run_portfolio_optimization():
    """Main function to run all portfolio optimization components."""
    try:
        prices = load_prices(TICKERS)
        
        # 1. Mean-Variance Optimization
        optimization_results = mean_variance_optimization(prices)
        
        # 2. Discrete Allocation for Max Sharpe Portfolio
        discrete_allocation_suggestion(prices, optimization_results["max_sharpe_weights"])
        
        # 3. Rebalancing Suggestion (Mock)
        print("\n--- Portfolio Rebalancing Suggestion ---")
        print("A rebalancing suggestion would compare the current portfolio weights (from a user's database) with the newly calculated optimal weights.")
        print("For example, if current AAPL weight is 10% and optimal is 15%, the suggestion would be to 'BUY' more AAPL.")
        print("Since we don't have a current portfolio, we'll use the Max Sharpe weights as the target for a mock rebalance.")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure the data ingestion script (data_ingestion.py) has been run successfully.")
    except Exception as e:
        print(f"An unexpected error occurred during portfolio optimization: {e}")

if __name__ == "__main__":
    run_portfolio_optimization()
