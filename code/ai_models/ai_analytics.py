import pandas as pd
import numpy as np
from prophet import Prophet
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os
import warnings

# Suppress Prophet's verbose output
warnings.filterwarnings('ignore')

# --- Configuration and Data Loading ---

DATA_DIR = "data"
TICKER_TO_FORECAST = "AAPL"

def load_price_data(ticker: str, data_dir: str = DATA_DIR) -> pd.DataFrame:
    """Loads historical 'Close' price data for a single ticker for Prophet."""
    file_name = f"{ticker.replace('-', '_')}_historical.csv"
    file_path = os.path.join(data_dir, file_name)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found for {ticker} at {file_path}. Run data_ingestion.py first.")
        
    df = pd.read_csv(file_path, index_col=0, parse_dates=True)
    
    # Prophet requires columns named 'ds' (datestamp) and 'y' (value)
    df_prophet = df['Close'].reset_index()
    df_prophet.columns = ['ds', 'y']
    
    print(f"Loaded {len(df_prophet)} rows for {ticker} for forecasting.")
    return df_prophet

# --- Time-Series Forecasting (Prophet) ---

def prophet_forecast(df: pd.DataFrame, periods: int = 30):
    """
    Trains a Prophet model and forecasts future price movements.
    """
    print(f"\n--- Prophet Time-Series Forecasting for {TICKER_TO_FORECAST} ({periods} days) ---")
    
    # Initialize and train the model
    m = Prophet(daily_seasonality=True)
    m.fit(df)
    
    # Create a future dataframe for prediction
    future = m.make_future_dataframe(periods=periods)
    
    # Make the prediction
    forecast = m.predict(future)
    
    print("Forecast columns: ds, yhat (forecast), yhat_lower, yhat_upper")
    print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())
    
    return forecast

# --- Sentiment Analysis (VADER) ---

def analyze_sentiment(text_list: list) -> pd.DataFrame:
    """
    Performs sentiment analysis on a list of text snippets using NLTK's VADER.
    In a real application, this would be fed by a web scraper.
    """
    print("\n--- Sentiment Analysis (VADER) ---")
    
    sia = SentimentIntensityAnalyzer()
    results = []
    
    for text in text_list:
        vs = sia.polarity_scores(text)
        results.append({
            'text': text,
            'compound': vs['compound'],
            'sentiment': 'Positive' if vs['compound'] >= 0.05 else ('Negative' if vs['compound'] <= -0.05 else 'Neutral')
        })
        
    df_sentiment = pd.DataFrame(results)
    print(df_sentiment[['text', 'compound', 'sentiment']])
    return df_sentiment

# --- Main Execution ---

def run_ai_analytics():
    """Main function to run all AI analytics components."""
    try:
        # 1. Time-Series Forecasting
        df_prices = load_price_data(TICKER_TO_FORECAST)
        prophet_forecast(df_prices, periods=7)
        
        # 2. Sentiment Analysis (Mock Scraped Data)
        mock_news_headlines = [
            "Apple stock hits all-time high on strong iPhone sales report.",
            "Federal Reserve signals interest rate hike, causing market jitters.",
            "Tesla announces massive recall due to software glitch.",
            "Bitcoin surges past $100,000 milestone in a historic rally.",
            "Analyst gives a neutral rating on Amazon's Q4 earnings."
        ]
        analyze_sentiment(mock_news_headlines)
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure the data ingestion script (data_ingestion.py) has been run successfully.")
    except Exception as e:
        print(f"An unexpected error occurred during AI analytics: {e}")

if __name__ == "__main__":
    run_ai_analytics()
