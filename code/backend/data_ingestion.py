import logging
import os
import time
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "BTC-USD", "ETH-USD"]
DEFAULT_END_DATE = datetime.now().strftime("%Y-%m-%d")
DEFAULT_START_DATE = (datetime.now() - timedelta(days=365 * 5)).strftime("%Y-%m-%d")
DATA_DIR = "data"
BATCH_SIZE = 5


def download_data(tickers: list, start_date: str, end_date: str) -> pd.DataFrame | None:
    """
    Attempts to download historical market data for a list of tickers with error handling.
    Returns a pandas DataFrame or None on failure.
    """
    try:
        logging.info(
            f"Downloading data for {tickers} from {start_date} to {end_date}..."
        )
        data = yf.download(
            tickers, start=start_date, end=end_date, group_by="ticker", progress=False
        )
        return data
    except Exception as e:
        logging.error(f"Failed to download data for tickers {tickers}. Error: {e}")
        return None


def fetch_historical_data(
    tickers: list, start_date: str, end_date: str, batch_size: int
) -> dict:
    """
    Fetches historical market data for a list of tickers, using batching for efficiency.
    """
    logging.info(f"Starting historical data fetch for {len(tickers)} tickers.")
    ticker_data = {}
    for i in range(0, len(tickers), batch_size):
        batch_tickers = tickers[i : i + batch_size]
        data = download_data(batch_tickers, start_date, end_date)
        if data is None:
            logging.warning(f"Skipping batch {batch_tickers} due to download failure.")
            continue
        for ticker in batch_tickers:
            df = None
            if isinstance(data.columns, pd.MultiIndex):
                if ticker in data.columns.levels[0]:
                    df = data[ticker].dropna()
            elif len(batch_tickers) == 1 and batch_tickers[0] == ticker:
                df = data.dropna()
            if df is not None and (not df.empty):
                ticker_data[ticker] = df
                logging.info(
                    f"Successfully processed data for {ticker}. Rows: {len(df)}"
                )
            else:
                logging.warning(f"No valid data found for {ticker}.")
        time.sleep(1)
    return ticker_data


def save_data_to_files(ticker_data: dict, data_dir: str) -> Any:
    """
    Saves the fetched data to CSV files in a specified directory.
    """
    os.makedirs(data_dir, exist_ok=True)
    logging.info(f"Saving data to files in '{data_dir}'...")
    for ticker, df in ticker_data.items():
        file_path = os.path.join(data_dir, f"{ticker.replace('-', '_')}_historical.csv")
        try:
            df.to_csv(file_path)
            logging.info(f"Saved {ticker} data to {file_path}")
        except Exception as e:
            logging.error(f"Error saving data for {ticker} to file: {e}")


def load_data_to_db(ticker_data: dict) -> Any:
    """
    Placeholder for database loading logic (PostgreSQL/MongoDB).
    """
    logging.info("\n--- Database Loading Placeholder ---")
    logging.info(
        "In a real implementation, this function would connect to a PostgreSQL or MongoDB instance."
    )
    logging.info(
        "It would iterate through 'ticker_data' and insert/upsert the time-series data."
    )
    for ticker, df in ticker_data.items():
        logging.info(
            f"  - Inserting {len(df)} records for {ticker} into the 'market_data' collection/table."
        )
    logging.info("----------------------------------\n")


def run_ingestion_service(
    tickers: list = DEFAULT_TICKERS,
    start_date: str = DEFAULT_START_DATE,
    end_date: str = DEFAULT_END_DATE,
    data_dir: str = DATA_DIR,
    batch_size: int = BATCH_SIZE,
) -> Any:
    """
    Main function to run the data ingestion service.
    :param tickers: List of ticker symbols to fetch.
    :param start_date: Start date for historical data (YYYY-MM-DD).
    :param end_date: End date for historical data (YYYY-MM-DD).
    :param data_dir: Directory to save the CSV files.
    :param batch_size: Number of tickers to download in a single batch.
    """
    logging.info("Starting Market Data Ingestion Service...")
    data = fetch_historical_data(tickers, start_date, end_date, batch_size)
    if not data:
        logging.error("Ingestion failed: No data was fetched.")
        return {}
    save_data_to_files(data, data_dir)
    load_data_to_db(data)
    logging.info("Market Data Ingestion Service finished.")
    return data


if __name__ == "__main__":
    run_ingestion_service()
