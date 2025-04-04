import numpy as np
from scipy.stats import norm

class RiskMetrics:
    @staticmethod
    def calculate_var(returns, confidence=0.95):
        mean = np.mean(returns)
        std = np.std(returns)
        z_score = norm.ppf(1 - confidence)
        return mean + z_score * std

    @staticmethod
    def efficient_frontier(returns, cov_matrix):
        from pypfopt import EfficientFrontier
        ef = EfficientFrontier(returns, cov_matrix)
        ef.max_sharpe()
        return ef.clean_weights()