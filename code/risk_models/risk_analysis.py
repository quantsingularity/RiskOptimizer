import os

import numpy as np
import pandas as pd
from arch import arch_model
from scipy.stats import norm

# --- Configuration and Data Loading ---

DATA_DIR = "data"
TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "BTC-USD", "ETH-USD"]


def load_data(tickers: list, data_dir: str = DATA_DIR) -> pd.DataFrame:
    """Loads historical 'Close' price data for a list of tickers."""
    all_data = {}
    for ticker in tickers:
        # Replace '-' with '_' for file name consistency
        file_name = f"{ticker.replace('-', '_')}_historical.csv"
        file_path = os.path.join(data_dir, file_name)

        if os.path.exists(file_path):
            df = pd.read_csv(file_path, index_col=0, parse_dates=True)
            # Use 'Close' price for risk analysis
            all_data[ticker] = df["Close"]
        else:
            print(f"Warning: Data file not found for {ticker} at {file_path}")

    if not all_data:
        raise FileNotFoundError(
            "No data files were loaded. Run data_ingestion.py first."
        )

    # Combine all series into a single DataFrame, forward-filling missing values
    data = pd.DataFrame(all_data).ffill().dropna()
    # Calculate daily log returns
    returns = np.log(data / data.shift(1)).dropna()
    return returns


# --- Core Risk Analysis Functions ---


def calculate_correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    """Computes the correlation matrix of asset returns."""
    print("\n--- Correlation Matrix ---")
    corr_matrix = returns.corr()
    print(corr_matrix)
    return corr_matrix


def historical_var(
    returns: pd.DataFrame, confidence_level: float = 0.99, horizon: int = 1
) -> pd.Series:
    """
    Calculates Value-at-Risk (VaR) using the historical simulation method.

    :param returns: DataFrame of asset returns.
    :param confidence_level: The confidence level (e.g., 0.99 for 99% VaR).
    :param horizon: The time horizon in days (e.g., 1 for 1-day VaR).
    :return: Series of VaR values for each asset.
    """
    print(f"\n--- Historical VaR ({confidence_level*100:.0f}%, {horizon}-day) ---")
    # Calculate the percentile corresponding to the VaR
    alpha = 1 - confidence_level
    var_values = returns.quantile(alpha) * np.sqrt(horizon)
    print(var_values)
    return var_values


def monte_carlo_var(
    returns: pd.DataFrame,
    confidence_level: float = 0.99,
    horizon: int = 1,
    n_simulations: int = 10000,
) -> pd.Series:
    """
    Calculates Value-at-Risk (VaR) using Monte Carlo simulation (assuming Normal distribution).

    :param returns: DataFrame of asset returns.
    :param confidence_level: The confidence level (e.g., 0.99 for 99% VaR).
    :param horizon: The time horizon in days (e.g., 1 for 1-day VaR).
    :param n_simulations: Number of Monte Carlo paths to simulate.
    :return: Series of VaR values for each asset.
    """
    print(f"\n--- Monte Carlo VaR ({confidence_level*100:.0f}%, {horizon}-day) ---")

    mu = returns.mean()
    sigma = returns.std()
    alpha = 1 - confidence_level

    var_values = {}
    for ticker in returns.columns:
        # Simulate returns for the horizon
        simulated_returns = np.random.normal(
            mu[ticker] * horizon, sigma[ticker] * np.sqrt(horizon), n_simulations
        )
        # Calculate VaR as the alpha-percentile of the simulated returns
        var = np.percentile(simulated_returns, alpha * 100)
        var_values[ticker] = var

    var_series = pd.Series(var_values)
    print(var_series)
    return var_series


def garch_volatility_forecast(returns: pd.DataFrame, horizon: int = 5) -> pd.Series:
    """
    Forecasts volatility for each asset using a GARCH(1,1) model.

    :param returns: DataFrame of asset returns.
    :param horizon: The number of days to forecast volatility.
    :return: Series of annualized volatility forecasts.
    """
    print(f"\n--- GARCH(1,1) Volatility Forecast ({horizon}-day) ---")
    forecasts = {}
    for ticker in returns.columns:
        # Use the mean-adjusted returns (subtract the mean)
        am = arch_model(returns[ticker] * 100, vol="Garch", p=1, q=1, rescale=False)
        res = am.fit(disp="off")

        # Forecast the conditional variance
        forecast = res.forecast(horizon=horizon)
        # The forecast is for variance, take the square root for volatility
        # We use the last step of the forecast for the horizon volatility
        volatility_forecast = np.sqrt(forecast.variance.iloc[-1].sum()) / 100

        # Annualize the volatility (assuming 252 trading days)
        annualized_vol = volatility_forecast * np.sqrt(252)
        forecasts[ticker] = annualized_vol

    forecast_series = pd.Series(forecasts)
    print(forecast_series)
    return forecast_series


def stress_test(returns: pd.DataFrame, scenario_multiplier: float = 3.0) -> pd.Series:
    """
    Performs a simple stress test by simulating an extreme market shock.

    :param returns: DataFrame of asset returns.
    :param scenario_multiplier: Multiplier for the standard deviation to define the shock.
    :return: Series of simulated loss for each asset.
    """
    print(f"\n--- Stress Test (Extreme Shock: {scenario_multiplier}x Std Dev) ---")

    # Calculate the shock as a multiple of the standard deviation
    shock = returns.std() * scenario_multiplier

    # The simulated loss is the negative of the shock
    simulated_loss = -shock
    print(simulated_loss)
    return simulated_loss


def run_risk_analysis():
    """Main function to run all risk analysis components."""
    try:
        returns = load_data(TICKERS)

        # 1. Correlation Matrix
        calculate_correlation_matrix(returns)

        # 2. Historical VaR (99%, 1-day)
        historical_var(returns, confidence_level=0.99, horizon=1)

        # 3. Monte Carlo VaR (95%, 5-day)
        monte_carlo_var(returns, confidence_level=0.95, horizon=5)

        # 4. GARCH Volatility Forecast (5-day)
        garch_volatility_forecast(returns, horizon=5)

        # 5. Stress Test
        stress_test(returns, scenario_multiplier=4.0)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print(
            "Please ensure the data ingestion script (data_ingestion.py) has been run successfully."
        )
    except Exception as e:
        print(f"An unexpected error occurred during risk analysis: {e}")


if __name__ == "__main__":
    run_risk_analysis()
