"""
Extreme Value Theory (EVT) Risk Models for RiskOptimizer

This module provides advanced risk modeling using Extreme Value Theory:
1. Peaks Over Threshold (POT) method with Generalized Pareto Distribution
2. Block Maxima method with Generalized Extreme Value Distribution
3. EVT-based VaR and ES calculation
4. Extreme scenario generation
5. Tail dependence estimation
6. Stress testing with extreme events
"""

import logging
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("extreme_value_theory")

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")


class ExtremeValueRisk:
    """Extreme Value Theory Risk Model"""

    def __init__(self):
        """Initialize Extreme Value Risk Model"""
        self.data = None
        self.pot_params = None
        self.bm_params = None
        self.threshold = None
        self.threshold_quantile = None
        self.block_size = None

    def fit_pot(self, data, threshold=None, threshold_quantile=0.1):
        """
        Fit Peaks Over Threshold model with Generalized Pareto Distribution

        Args:
            data: Array-like of returns
            threshold: Explicit threshold value (optional)
            threshold_quantile: Quantile for threshold selection (default: 0.1)

        Returns:
            self: The fitted model
        """
        # Store data
        if isinstance(data, pd.Series) or isinstance(data, pd.DataFrame):
            self.data = data.values.flatten()
        else:
            self.data = np.array(data).flatten()

        # Determine threshold
        if threshold is None:
            self.threshold = np.percentile(self.data, threshold_quantile * 100)
        else:
            self.threshold = threshold

        self.threshold_quantile = threshold_quantile

        # Extract exceedances
        exceedances = -self.data[self.data <= -self.threshold]

        if len(exceedances) < 10:
            logger.warning("Too few exceedances for reliable GPD fitting")
            # Use conservative parameters
            shape = 0.2  # Slightly heavy-tailed
            scale = np.std(self.data) * 0.5
        else:
            # Fit Generalized Pareto Distribution
            try:
                # Shift exceedances to be relative to threshold
                excess = exceedances - self.threshold

                # Fit GPD using MLE
                shape, loc, scale = stats.genpareto.fit(excess)

                # Log results
                logger.info(
                    f"GPD fit: shape={shape:.4f}, scale={scale:.4f}, threshold={self.threshold:.4f}"
                )
            except:
                # Fallback to method of moments
                logger.warning("MLE fitting failed, using method of moments")
                excess = exceedances - self.threshold
                mean_excess = np.mean(excess)
                var_excess = np.var(excess)

                # Method of moments estimators
                shape = 0.5 * (1 - (mean_excess**2 / var_excess))
                scale = 0.5 * mean_excess * (1 + (mean_excess**2 / var_excess))

        # Store parameters
        self.pot_params = {"shape": shape, "scale": scale, "threshold": self.threshold}

        return self

    def fit_block_maxima(self, data, block_size=20):
        """
        Fit Block Maxima model with Generalized Extreme Value Distribution

        Args:
            data: Array-like of returns
            block_size: Size of blocks for maxima extraction

        Returns:
            self: The fitted model
        """
        # Store data
        if isinstance(data, pd.Series) or isinstance(data, pd.DataFrame):
            self.data = data.values.flatten()
        else:
            self.data = np.array(data).flatten()

        self.block_size = block_size

        # Extract block maxima
        n_blocks = len(self.data) // block_size
        block_maxima = np.zeros(n_blocks)

        for i in range(n_blocks):
            block = -self.data[i * block_size : (i + 1) * block_size]
            block_maxima[i] = np.max(block)

        if len(block_maxima) < 10:
            logger.warning("Too few blocks for reliable GEV fitting")
            # Use conservative parameters
            shape = 0.2  # Slightly heavy-tailed
            loc = np.mean(block_maxima)
            scale = np.std(block_maxima)
        else:
            # Fit Generalized Extreme Value Distribution
            try:
                shape, loc, scale = stats.genextreme.fit(block_maxima)

                # Log results
                logger.info(
                    f"GEV fit: shape={shape:.4f}, loc={loc:.4f}, scale={scale:.4f}"
                )
            except:
                # Fallback to normal approximation
                logger.warning("GEV fitting failed, using normal approximation")
                loc = np.mean(block_maxima)
                scale = np.std(block_maxima)
                shape = 0.1  # Slightly heavy-tailed

        # Store parameters
        self.bm_params = {"shape": shape, "loc": loc, "scale": scale}

        return self

    def calculate_var(self, confidence=0.95, method="evt", return_period=None):
        """
        Calculate Value at Risk (VaR) using EVT

        Args:
            confidence: Confidence level (default: 0.95 for 95% VaR)
            method: Method to use ('evt', 'historical', 'normal')
            return_period: Return period in days (alternative to confidence)

        Returns:
            var: Value at Risk at specified confidence level (positive value)
        """
        if self.data is None:
            raise ValueError("Model must be fitted before calculating VaR")

        # Convert return period to confidence level
        if return_period is not None:
            confidence = 1 - 1 / return_period

        if method == "evt":
            if self.pot_params is not None:
                # Calculate VaR using POT method
                shape = self.pot_params["shape"]
                scale = self.pot_params["scale"]
                threshold = self.pot_params["threshold"]

                # Probability of exceeding threshold
                p_threshold = self.threshold_quantile

                # Calculate VaR
                p = 1 - confidence
                if abs(shape) < 1e-10:  # Shape close to 0
                    var = threshold + scale * np.log(p_threshold / p)
                else:
                    var = threshold + (scale / shape) * ((p_threshold / p) ** shape - 1)

                # Ensure VaR is positive (absolute value)
                return abs(var)
            elif self.bm_params is not None:
                # Calculate VaR using Block Maxima method
                shape = self.bm_params["shape"]
                loc = self.bm_params["loc"]
                scale = self.bm_params["scale"]

                # Calculate VaR
                p = confidence
                var = loc - scale / shape * (1 - (-np.log(p)) ** (-shape))

                # Ensure VaR is positive (absolute value)
                return abs(var)
            else:
                raise ValueError("Either POT or Block Maxima model must be fitted")

        elif method == "historical":
            # Historical VaR
            var = -np.percentile(self.data, 100 * (1 - confidence))
            return abs(var)

        elif method == "normal":
            # Parametric VaR (normal distribution)
            mean = np.mean(self.data)
            std = np.std(self.data)
            z_score = stats.norm.ppf(confidence)
            var = -(mean + z_score * std)
            return abs(var)

        else:
            raise ValueError("Method must be 'evt', 'historical', or 'normal'")

    def calculate_es(self, confidence=0.95, method="evt"):
        """
        Calculate Expected Shortfall (ES) using EVT

        Args:
            confidence: Confidence level (default: 0.95 for 95% ES)
            method: Method to use ('evt', 'historical', 'normal')

        Returns:
            es: Expected Shortfall at specified confidence level
        """
        if self.data is None:
            raise ValueError("Model must be fitted before calculating ES")

        if method == "evt":
            if self.pot_params is not None:
                # Calculate ES using POT method
                shape = self.pot_params["shape"]
                scale = self.pot_params["scale"]
                threshold = self.pot_params["threshold"]

                # Calculate VaR first
                var = self.calculate_var(confidence, method="evt")

                # Calculate ES
                if shape >= 1:
                    logger.warning("Shape parameter >= 1, ES is infinite")
                    # Use a conservative approximation
                    es = var * 1.5
                else:
                    es = var / (1 - shape) + (scale - shape * threshold) / (1 - shape)

                return es
            elif self.bm_params is not None:
                # Calculate ES using Block Maxima method
                # For GEV, ES is more complex, use numerical integration
                var = self.calculate_var(confidence, method="evt")

                # Use empirical ES beyond VaR as approximation
                es = -np.mean(self.data[self.data <= -var])

                return es
            else:
                raise ValueError("Either POT or Block Maxima model must be fitted")

        elif method == "historical":
            # Historical ES
            var = self.calculate_var(confidence, method="historical")
            es = -np.mean(self.data[self.data <= -var])
            return es

        elif method == "normal":
            # Parametric ES (normal distribution)
            mean = np.mean(self.data)
            std = np.std(self.data)
            z_score = stats.norm.ppf(confidence)
            es = -(mean + std * stats.norm.pdf(z_score) / (1 - confidence))
            return es

        else:
            raise ValueError("Method must be 'evt', 'historical', or 'normal'")

    def generate_scenarios(self, n_scenarios=1000, method="evt", severity="extreme"):
        """
        Generate extreme scenarios based on fitted EVT model

        Args:
            n_scenarios: Number of scenarios to generate
            method: Method to use ('evt', 'historical', 'normal')
            severity: Severity of scenarios ('extreme', 'moderate', 'mixed')

        Returns:
            scenarios: Array of generated scenarios
        """
        if self.data is None:
            raise ValueError("Model must be fitted before generating scenarios")

        if method == "evt":
            if self.pot_params is not None:
                # Generate scenarios using POT method
                shape = self.pot_params["shape"]
                scale = self.pot_params["scale"]
                threshold = self.pot_params["threshold"]

                # Determine severity factor
                if severity == "extreme":
                    severity_factor = 0.01  # Focus on 1% tail
                elif severity == "moderate":
                    severity_factor = 0.05  # Focus on 5% tail
                else:  # mixed
                    severity_factor = 0.1  # Focus on 10% tail

                # Generate uniform random variables
                u = np.random.uniform(0, severity_factor, n_scenarios)

                # Transform to GPD
                if abs(shape) < 1e-10:  # Shape close to 0
                    scenarios = threshold + scale * np.log(u / severity_factor)
                else:
                    scenarios = threshold + (scale / shape) * (
                        (u / severity_factor) ** shape - 1
                    )

                # Negate to get losses
                scenarios = -scenarios

                return scenarios
            elif self.bm_params is not None:
                # Generate scenarios using Block Maxima method
                shape = self.bm_params["shape"]
                loc = self.bm_params["loc"]
                scale = self.bm_params["scale"]

                # Generate GEV random variables
                scenarios = stats.genextreme.rvs(
                    shape, loc=loc, scale=scale, size=n_scenarios
                )

                # Negate to get losses
                scenarios = -scenarios

                return scenarios
            else:
                raise ValueError("Either POT or Block Maxima model must be fitted")

        elif method == "historical":
            # Generate scenarios by bootstrapping historical data
            indices = np.random.choice(len(self.data), n_scenarios)
            scenarios = self.data[indices]

            # If extreme scenarios requested, filter for more extreme values
            if severity == "extreme":
                threshold = np.percentile(self.data, 5)  # 5th percentile
                extreme_indices = np.where(self.data <= threshold)[0]
                if len(extreme_indices) > 0:
                    extreme_indices = np.random.choice(
                        extreme_indices, n_scenarios // 2
                    )
                    scenarios[: n_scenarios // 2] = self.data[extreme_indices]

            return scenarios

        elif method == "normal":
            # Generate scenarios from normal distribution
            mean = np.mean(self.data)
            std = np.std(self.data)

            # Adjust std based on severity
            if severity == "extreme":
                std *= 1.5  # Increase volatility for more extreme scenarios
            elif severity == "moderate":
                std *= 1.2  # Slightly increase volatility

            scenarios = np.random.normal(mean, std, n_scenarios)
            return scenarios

        else:
            raise ValueError("Method must be 'evt', 'historical', or 'normal'")

    def calculate_tail_dependence(
        self, x, y, method="empirical", threshold_quantile=0.1
    ):
        """
        Calculate tail dependence between two return series

        Args:
            x: First return series
            y: Second return series
            method: Method to use ('empirical', 'copula')
            threshold_quantile: Quantile for threshold selection

        Returns:
            tail_dep: Tail dependence coefficient
        """
        # Convert to numpy arrays
        x = np.array(x).flatten()
        y = np.array(y).flatten()

        if method == "empirical":
            # Calculate empirical tail dependence
            threshold_x = np.percentile(x, threshold_quantile * 100)
            threshold_y = np.percentile(y, threshold_quantile * 100)

            # Count joint exceedances
            joint_exceedances = np.sum((x <= threshold_x) & (y <= threshold_y))
            x_exceedances = np.sum(x <= threshold_x)

            # Calculate tail dependence
            tail_dep = joint_exceedances / x_exceedances if x_exceedances > 0 else 0

            return tail_dep

        elif method == "copula":
            # Calculate rank correlation
            rho = stats.spearmanr(x, y)[0]

            # Calculate tail dependence using t-copula approximation
            df = 4  # Degrees of freedom (lower = more tail dependence)
            tail_dep = 2 * stats.t.cdf(
                -np.sqrt((df + 1) * (1 - rho) / (1 + rho)), df + 1
            )

            return tail_dep

        else:
            raise ValueError("Method must be 'empirical' or 'copula'")

    def plot_tail_distribution(self, confidence_levels=[0.9, 0.95, 0.99, 0.999]):
        """
        Plot tail distribution with VaR and ES

        Args:
            confidence_levels: List of confidence levels to plot

        Returns:
            fig: Matplotlib figure
        """
        if self.data is None:
            raise ValueError("Model must be fitted before plotting")

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot histogram of returns
        ax.hist(self.data, bins=50, density=True, alpha=0.5, label="Returns")

        # Plot normal distribution for comparison
        x = np.linspace(min(self.data), max(self.data), 1000)
        ax.plot(
            x,
            stats.norm.pdf(x, np.mean(self.data), np.std(self.data)),
            "r--",
            label="Normal Distribution",
        )

        # Plot EVT tail distribution
        if self.pot_params is not None:
            # Get parameters
            shape = self.pot_params["shape"]
            scale = self.pot_params["scale"]
            threshold = self.pot_params["threshold"]

            # Plot GPD for exceedances
            x_tail = np.linspace(-max(self.data), -threshold, 1000)
            y_tail = stats.genpareto.pdf(-x_tail - threshold, shape, scale=scale)

            # Scale by probability of exceeding threshold
            p_threshold = np.mean(self.data <= -threshold)
            y_tail *= p_threshold

            ax.plot(-x_tail, y_tail, "g-", linewidth=2, label="EVT Tail Distribution")

        # Plot VaR and ES for each confidence level
        colors = ["b", "g", "r", "c", "m"]
        for i, conf in enumerate(confidence_levels):
            color = colors[i % len(colors)]

            # Calculate VaR and ES
            var = self.calculate_var(conf, method="evt")
            es = self.calculate_es(conf, method="evt")

            # Plot VaR
            ax.axvline(
                -var,
                color=color,
                linestyle="--",
                label=f"VaR ({conf*100:.1f}%): {var:.4f}",
            )

            # Plot ES
            ax.axvline(
                -es, color=color, linestyle=":", label=f"ES ({conf*100:.1f}%): {es:.4f}"
            )

        # Add labels and legend
        ax.set_xlabel("Return")
        ax.set_ylabel("Density")
        ax.set_title("Tail Distribution with VaR and ES")
        ax.legend()

        # Focus on the tail
        ax.set_xlim(left=-max(abs(self.data)), right=0)

        return fig

    def plot_mean_excess(self):
        """
        Plot mean excess function to help with threshold selection

        Returns:
            fig: Matplotlib figure
        """
        if self.data is None:
            raise ValueError("Data must be provided before plotting")

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))

        # Calculate mean excess function
        losses = -self.data
        losses.sort()
        losses = losses[losses > 0]  # Only consider losses

        n_points = min(100, len(losses) // 2)
        thresholds = np.linspace(0, np.percentile(losses, 95), n_points)
        mean_excess = np.zeros(n_points)

        for i, threshold in enumerate(thresholds):
            exceedances = losses[losses > threshold] - threshold
            mean_excess[i] = np.mean(exceedances) if len(exceedances) > 0 else np.nan

        # Plot mean excess function
        ax.plot(thresholds, mean_excess, "b-", linewidth=2)

        # Add current threshold if available
        if self.threshold is not None:
            ax.axvline(
                -self.threshold,
                color="r",
                linestyle="--",
                label=f"Current Threshold: {-self.threshold:.4f}",
            )

        # Add labels and legend
        ax.set_xlabel("Threshold")
        ax.set_ylabel("Mean Excess")
        ax.set_title("Mean Excess Function")
        if self.threshold is not None:
            ax.legend()

        return fig

    def plot_return_level(self, return_periods=[1, 2, 5, 10, 20, 50, 100]):
        """
        Plot return level plot

        Args:
            return_periods: List of return periods in days

        Returns:
            fig: Matplotlib figure
        """
        if self.data is None:
            raise ValueError("Model must be fitted before plotting")

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))

        # Calculate return levels for each return period
        return_levels = np.zeros(len(return_periods))

        for i, period in enumerate(return_periods):
            confidence = 1 - 1 / period
            return_levels[i] = self.calculate_var(confidence, method="evt")

        # Plot return level curve
        ax.semilogx(return_periods, return_levels, "bo-", linewidth=2)

        # Add labels
        ax.set_xlabel("Return Period (days)")
        ax.set_ylabel("Return Level (VaR)")
        ax.set_title("Return Level Plot")

        # Add grid
        ax.grid(True, which="both", linestyle="--", linewidth=0.5)

        return fig


# Example usage
if __name__ == "__main__":
    # Generate sample data with fat tails
    np.random.seed(42)
    n_samples = 1000
    returns = np.random.standard_t(3, n_samples) * 0.02 + 0.001

    # Create EVT model
    evt_model = ExtremeValueRisk()

    # Fit POT model
    evt_model.fit_pot(returns, threshold_quantile=0.1)

    # Calculate VaR and ES
    var_95 = evt_model.calculate_var(0.95, method="evt")
    es_95 = evt_model.calculate_es(0.95, method="evt")

    print(f"EVT VaR (95%): {var_95:.4f}")
    print(f"EVT ES (95%): {es_95:.4f}")

    # Compare with historical and normal methods
    var_hist = evt_model.calculate_var(0.95, method="historical")
    var_norm = evt_model.calculate_var(0.95, method="normal")

    print(f"Historical VaR (95%): {var_hist:.4f}")
    print(f"Normal VaR (95%): {var_norm:.4f}")

    # Generate extreme scenarios
    scenarios = evt_model.generate_scenarios(n_scenarios=1000, method="evt")

    print(f"Mean scenario: {np.mean(scenarios):.4f}")
    print(f"Min scenario: {np.min(scenarios):.4f}")
    print(f"Max scenario: {np.max(scenarios):.4f}")

    # Plot tail distribution
    fig = evt_model.plot_tail_distribution()
    plt.tight_layout()
    plt.savefig("evt_tail_distribution.png")

    # Plot mean excess function
    fig = evt_model.plot_mean_excess()
    plt.tight_layout()
    plt.savefig("evt_mean_excess.png")

    # Plot return level
    fig = evt_model.plot_return_level()
    plt.tight_layout()
    plt.savefig("evt_return_level.png")
