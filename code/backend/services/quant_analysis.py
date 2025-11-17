from decimal import Decimal, getcontext

import numpy as np
from scipy.stats import norm

# Set precision for Decimal calculations
getcontext().prec = 28


class RiskMetrics:
    @staticmethod
    def calculate_var(returns, confidence=0.95):
        """
        Calculate Value at Risk (VaR) using the parametric method.
        This method assumes returns are normally distributed.

        Args:
            returns (list or np.ndarray): A list or array of portfolio returns.
            confidence (float): The confidence level for VaR calculation (e.g., 0.95 for 95%).

        Returns:
            Decimal: The calculated Value at Risk.
        """
        if not isinstance(returns, (list, np.ndarray)) or len(returns) == 0:
            raise ValueError("Returns must be a non-empty list or numpy array.")

        # Convert returns to Decimal for higher precision
        decimal_returns = [Decimal(str(r)) for r in returns]

        mean = np.mean(decimal_returns)
        std = np.std(decimal_returns)

        # Z-score for the given confidence level
        z_score = Decimal(str(norm.ppf(1 - confidence)))

        # VaR calculation
        var = mean + z_score * std

        return var

    @staticmethod
    def calculate_cvar(returns, confidence=0.95):
        """
        Calculate Conditional Value at Risk (CVaR), also known as Expected Shortfall (ES).
        CVaR is the expected loss given that the loss is greater than or equal to VaR.

        Args:
            returns (list or np.ndarray): A list or array of portfolio returns.
            confidence (float): The confidence level for CVaR calculation.

        Returns:
            Decimal: The calculated Conditional Value at Risk.
        """
        if not isinstance(returns, (list, np.ndarray)) or len(returns) == 0:
            raise ValueError("Returns must be a non-empty list or numpy array.")

        # Convert returns to Decimal
        decimal_returns = [Decimal(str(r)) for r in returns]

        # Calculate VaR first
        var = RiskMetrics.calculate_var(decimal_returns, confidence)

        # Filter returns that are worse than VaR
        tail_losses = [r for r in decimal_returns if r <= var]

        if not tail_losses:
            # If no losses exceed VaR, CVaR is equal to VaR
            return var

        # CVaR is the average of the tail losses
        cvar = np.mean(tail_losses)

        return cvar

    @staticmethod
    def efficient_frontier(returns, cov_matrix):
        """
        Calculate the optimal portfolio weights for the efficient frontier (max Sharpe ratio).
        Uses the PyPortfolioOpt library.

        Args:
            returns (pd.Series): A pandas Series of expected returns for each asset.
            cov_matrix (pd.DataFrame): A pandas DataFrame of the covariance matrix of asset returns.

        Returns:
            dict: A dictionary of asset tickers and their optimal weights.
        """
        try:
            from pypfopt import EfficientFrontier
        except ImportError:
            raise ImportError(
                "PyPortfolioOpt is not installed. Please install it using `pip install PyPortfolioOpt`."
            )

        ef = EfficientFrontier(returns, cov_matrix)
        ef.max_sharpe()
        cleaned_weights = ef.clean_weights()

        # Convert weights to string for consistent storage, can be parsed later
        return {asset: str(weight) for asset, weight in cleaned_weights.items()}

    @staticmethod
    def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
        """
        Calculate the Sharpe Ratio of a portfolio.

        Args:
            returns (list or np.ndarray): A list or array of portfolio returns.
            risk_free_rate (float): The risk-free rate of return.

        Returns:
            Decimal: The calculated Sharpe Ratio.
        """
        if not isinstance(returns, (list, np.ndarray)) or len(returns) < 2:
            raise ValueError(
                "Returns must be a list or numpy array with at least two elements."
            )

        decimal_returns = [Decimal(str(r)) for r in returns]

        excess_returns = [r - Decimal(str(risk_free_rate)) for r in decimal_returns]

        mean_excess_return = np.mean(excess_returns)
        std_dev_excess_return = np.std(excess_returns)

        if std_dev_excess_return == 0:
            return Decimal("0.0")

        sharpe_ratio = mean_excess_return / std_dev_excess_return

        return sharpe_ratio
