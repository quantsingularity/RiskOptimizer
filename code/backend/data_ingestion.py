import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

# Configuration
TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "BTC-USD", "ETH-USD"]
START_DATE = (datetime.now() - timedelta(days=365 * 5)).strftime('%Y-%m-%d')
END_DATE = datetime.now().strftime('%Y-%m-%d')
DATA_DIR = "data"

def fetch_historical_data(tickers: list, start_date: str, end_date: str) -> dict:
    """
    Fetches historical market data for a list of tickers.
    """
    print(f"Fetching historical data for {len(tickers)} tickers from {start_date} to {end_date}...")
    data = yf.download(tickers, start=start_date, end=end_date, group_by='ticker')
    
    # yfinance returns a multi-index DataFrame if multiple tickers are requested.
    # We will convert it to a dictionary of single-ticker DataFrames for easier handling.
    ticker_data = {}
    for ticker in tickers:
        if ticker in data.columns.levels[0]:
            # Extract the data for the specific ticker
            df = data[ticker].dropna()
            if not df.empty:
                ticker_data[ticker] = df
                print(f"Successfully fetched data for {ticker}. Rows: {len(df)}")
            else:
                print(f"Warning: No data found for {ticker}.")
        else:
            print(f"Error: Ticker {ticker} not found in downloaded data.")
            
    return ticker_data

def save_data_to_files(ticker_data: dict, data_dir: str):
    """
    Saves the fetched data to CSV files in a specified directory.
    In a production environment, this would be replaced by a database loader.
    """
    os.makedirs(data_dir, exist_ok=True)
    print(f"Saving data to files in '{data_dir}'...")
    
    for ticker, df in ticker_data.items():
        file_path = os.path.join(data_dir, f"{ticker.replace('-', '_')}_historical.csv")
        df.to_csv(file_path)
        print(f"Saved {ticker} data to {file_path}")

def load_data_to_db(ticker_data: dict):
    """
    Placeholder for database loading logic (PostgreSQL/MongoDB).
    """
    print("\n--- Database Loading Placeholder ---")
    print("In a real implementation, this function would connect to a PostgreSQL or MongoDB instance.")
    print("It would iterate through 'ticker_data' and insert/upsert the time-series data.")
    print("Example using a mock printout:")
    for ticker, df in ticker_data.items():
        print(f"  - Inserting {len(df)} records for {ticker} into the 'market_data' collection/table.")
    print("----------------------------------\n")

def run_ingestion_service():
    """
    Main function to run the data ingestion service.
    """
    print("Starting Market Data Ingestion Service...")
    
    # 1. Fetch data
    data = fetch_historical_data(TICKERS, START_DATE, END_DATE)
    
    if not data:
        print("Ingestion failed: No data was fetched.")
        return

    # 2. Save data to files (Mock DB)
    save_data_to_files(data, DATA_DIR)
    
    # 3. Load data to DB (Placeholder)
    load_data_to_db(data)
    
    print("Market Data Ingestion Service finished.")

if __name__ == "__main__":
    run_ingestion_service()
