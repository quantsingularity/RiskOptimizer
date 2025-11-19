"""
Parallel Risk Calculation Engine for RiskOptimizer

This module provides optimized risk calculation capabilities using parallel processing:
1. Parallel Monte Carlo simulation for risk metrics
2. Parallel portfolio optimization
3. Parallel batch risk calculation across multiple models
4. Parallel stress testing and scenario analysis
5. Parallel backtesting of risk models
6. Parallel sensitivity analysis
7. Parallel risk decomposition
"""

import logging
import multiprocessing as mp
import time
import warnings

import numpy as np
import pandas as pd
import psutil
from joblib import Parallel, delayed
from scipy import stats

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("parallel_risk_engine")

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")


class ParallelRiskEngine:
    """Parallel Risk Calculation Engine"""

    def __init__(self, n_jobs=None, backend="multiprocessing", verbose=0):
        """
        Initialize Parallel Risk Engine

        Args:
            n_jobs: Number of jobs to run in parallel (None = use all available cores)
            backend: Backend for parallel processing ("multiprocessing", "threading", "loky")
            verbose: Verbosity level (0 = silent, 1 = progress bar, 10 = debug)
        """
        # Set number of jobs
        if n_jobs is None:
            self.n_jobs = mp.cpu_count()
        else:
            self.n_jobs = n_jobs

        self.backend = backend
        self.verbose = verbose

        logger.info(
            f"Initialized ParallelRiskEngine with {self.n_jobs} jobs using {backend} backend"
        )

    def parallel_monte_carlo(
        self, risk_model, weights, n_scenarios=10000, confidence_levels=[0.95, 0.99]
    ):
        """
        Run Monte Carlo simulation in parallel

        Args:
            risk_model: Risk model with generate_scenarios method
            weights: Portfolio weights
            n_scenarios: Number of scenarios to generate
            confidence_levels: List of confidence levels for VaR and ES

        Returns:
            results: Dictionary of simulation results
        """
        logger.info(
            f"Running parallel Monte Carlo simulation with {n_scenarios} scenarios"
        )
        start_time = time.time()

        # Determine batch size
        batch_size = max(100, n_scenarios // (self.n_jobs * 10))
        n_batches = n_scenarios // batch_size

        # Generate scenarios in parallel
        scenario_batches = Parallel(
            n_jobs=self.n_jobs, backend=self.backend, verbose=self.verbose
        )(
            delayed(self._generate_scenarios_batch)(risk_model, batch_size)
            for _ in range(n_batches)
        )

        # Combine scenario batches
        all_scenarios = pd.concat(scenario_batches)

        # Calculate portfolio returns
        if isinstance(weights, dict):
            # Convert dict to array
            weight_array = np.zeros(len(risk_model.asset_names))
            for i, asset in enumerate(risk_model.asset_names):
                if asset in weights:
                    weight_array[i] = weights[asset]
            weights = weight_array

        portfolio_returns = all_scenarios.dot(weights)

        # Calculate portfolio metrics
        portfolio_metrics = {
            "expected_return": portfolio_returns.mean(),
            "volatility": portfolio_returns.std(),
            "skewness": stats.skew(portfolio_returns),
            "kurtosis": stats.kurtosis(portfolio_returns),
            "min_return": portfolio_returns.min(),
            "max_return": portfolio_returns.max(),
        }

        # Calculate risk metrics for each confidence level
        risk_metrics = {}
        for conf in confidence_levels:
            var = -np.percentile(portfolio_returns, 100 * (1 - conf))
            es = -portfolio_returns[portfolio_returns <= -var].mean()

            risk_metrics[f"var_{int(conf*100)}"] = var
            risk_metrics[f"es_{int(conf*100)}"] = es

        # Calculate time taken
        time_taken = time.time() - start_time

        logger.info(f"Monte Carlo simulation completed in {time_taken:.2f} seconds")

        return {
            "portfolio_metrics": portfolio_metrics,
            "risk_metrics": risk_metrics,
            "time_taken": time_taken,
        }

    def _generate_scenarios_batch(self, risk_model, batch_size):
        """
        Generate a batch of scenarios

        Args:
            risk_model: Risk model with generate_scenarios method
            batch_size: Number of scenarios to generate

        Returns:
            scenarios: DataFrame of generated scenarios
        """
        return risk_model.generate_scenarios(batch_size)

    def parallel_portfolio_optimization(
        self,
        returns,
        risk_model="markowitz",
        n_portfolios=1000,
        risk_free_rate=0.02,
        target_return=None,
        target_risk=None,
    ):
        """
        Run portfolio optimization in parallel

        Args:
            returns: DataFrame of asset returns
            risk_model: Risk model to use ("markowitz", "cvar", "mad")
            n_portfolios: Number of portfolios to generate
            risk_free_rate: Risk-free rate (annualized)
            target_return: Target return for minimum risk portfolio (optional)
            target_risk: Target risk for maximum return portfolio (optional)

        Returns:
            results: Dictionary of optimization results
        """
        logger.info(
            f"Running parallel portfolio optimization with {n_portfolios} portfolios"
        )
        start_time = time.time()

        # Get asset names and count
        assets = returns.columns
        len(assets)

        # Determine batch size
        batch_size = max(100, n_portfolios // (self.n_jobs * 10))
        n_batches = n_portfolios // batch_size

        # Generate random portfolios in parallel
        portfolio_batches = Parallel(
            n_jobs=self.n_jobs, backend=self.backend, verbose=self.verbose
        )(
            delayed(self._generate_portfolios_batch)(
                returns, risk_model, batch_size, risk_free_rate
            )
            for _ in range(n_batches)
        )

        # Combine portfolio batches
        all_portfolios = []
        for batch in portfolio_batches:
            all_portfolios.extend(batch)

        # Convert to DataFrame
        portfolios_df = pd.DataFrame(all_portfolios)

        # Ensure required columns exist before proceeding
        required_cols = ["return", "volatility", "sharpe_ratio"]
        if not all(col in portfolios_df.columns for col in required_cols):
            logger.error("Missing required columns in generated portfolios DataFrame")
            return None

        # Find efficient frontier
        efficient_frontier = self._find_efficient_frontier(portfolios_df)

        # Find maximum Sharpe ratio portfolio
        max_sharpe_idx = portfolios_df["sharpe_ratio"].idxmax()
        max_sharpe_portfolio = {
            "weights": dict(zip(assets, portfolios_df.loc[max_sharpe_idx, assets])),
            "return": portfolios_df.loc[max_sharpe_idx, "return"],
            "volatility": portfolios_df.loc[max_sharpe_idx, "volatility"],
            "sharpe_ratio": portfolios_df.loc[max_sharpe_idx, "sharpe_ratio"],
        }

        # Find minimum volatility portfolio
        min_vol_idx = portfolios_df["volatility"].idxmin()
        min_volatility_portfolio = {
            "weights": dict(zip(assets, portfolios_df.loc[min_vol_idx, assets])),
            "return": portfolios_df.loc[min_vol_idx, "return"],
            "volatility": portfolios_df.loc[min_vol_idx, "volatility"],
            "sharpe_ratio": portfolios_df.loc[min_vol_idx, "sharpe_ratio"],
        }

        # Find target portfolios if specified
        target_portfolios = {}

        if target_return is not None:
            target_return_portfolio = self._find_target_return_portfolio(
                portfolios_df, target_return, assets
            )
            target_portfolios["target_return"] = target_return_portfolio

        if target_risk is not None:
            target_risk_portfolio = self._find_target_risk_portfolio(
                portfolios_df, target_risk, assets
            )
            target_portfolios["target_risk"] = target_risk_portfolio

        # Calculate time taken
        time_taken = time.time() - start_time

        logger.info(f"Portfolio optimization completed in {time_taken:.2f} seconds")

        return {
            "efficient_frontier": efficient_frontier,
            "max_sharpe_portfolio": max_sharpe_portfolio,
            "min_volatility_portfolio": min_volatility_portfolio,
            "target_portfolios": target_portfolios,
            "all_portfolios": portfolios_df,
            "time_taken": time_taken,
        }

    def _generate_portfolios_batch(
        self, returns, risk_model, batch_size, risk_free_rate
    ):
        """
        Generate a batch of random portfolios

        Args:
            returns: DataFrame of asset returns
            risk_model: Risk model to use
            batch_size: Number of portfolios to generate
            risk_free_rate: Risk-free rate (annualized)

        Returns:
            portfolios: List of portfolio dictionaries
        """
        assets = returns.columns
        n_assets = len(assets)

        # Calculate annualization factor based on return frequency
        if isinstance(returns.index, pd.DatetimeIndex):
            # Estimate frequency
            if len(returns) >= 2:
                freq = pd.infer_freq(returns.index)
                if freq and "D" in freq:
                    annualization_factor = 252  # Daily returns
                elif freq and "W" in freq:
                    annualization_factor = 52  # Weekly returns
                elif freq and "M" in freq:
                    annualization_factor = 12  # Monthly returns
                else:
                    annualization_factor = 252  # Default to daily
            else:
                annualization_factor = 252  # Default to daily
        else:
            annualization_factor = 252  # Default to daily

        # Calculate mean returns and covariance matrix
        mean_returns = returns.mean() * annualization_factor
        cov_matrix = returns.cov() * annualization_factor

        portfolios = []

        for _ in range(batch_size):
            # Generate random weights
            weights = np.random.random(n_assets)
            weights /= np.sum(weights)

            # Calculate portfolio return and volatility
            portfolio_return = np.sum(mean_returns * weights)
            portfolio_volatility = np.sqrt(
                np.dot(weights.T, np.dot(cov_matrix, weights))
            )

            # Calculate risk metric based on model
            if risk_model == "markowitz":
                risk_metric = portfolio_volatility
            elif risk_model == "cvar":
                # Simplified CVaR calculation
                portfolio_returns = returns.dot(weights)
                var_95 = -np.percentile(portfolio_returns, 5)
                cvar_95 = -portfolio_returns[portfolio_returns <= -var_95].mean()
                risk_metric = cvar_95 * np.sqrt(annualization_factor)
            elif risk_model == "mad":
                # Mean Absolute Deviation
                portfolio_returns = returns.dot(weights)
                mad = np.mean(np.abs(portfolio_returns - portfolio_returns.mean()))
                risk_metric = mad * np.sqrt(annualization_factor)
            else:
                risk_metric = portfolio_volatility

            # Calculate Sharpe ratio
            sharpe_ratio = (
                (portfolio_return - risk_free_rate) / portfolio_volatility
                if portfolio_volatility > 0
                else 0
            )

            # Create portfolio dictionary
            portfolio = {
                **dict(zip(assets, weights)),
                "return": portfolio_return,  # Ensure this key is present
                "volatility": portfolio_volatility,
                "risk_metric": risk_metric,
                "sharpe_ratio": sharpe_ratio,
            }

            portfolios.append(portfolio)

        return portfolios

    def _find_efficient_frontier(self, portfolios_df, n_points=100):
        """
        Find the efficient frontier from a set of portfolios

        Args:
            portfolios_df: DataFrame of portfolios
            n_points: Number of points on the efficient frontier

        Returns:
            efficient_frontier: DataFrame of efficient frontier portfolios
        """
        # Sort portfolios by return
        sorted_portfolios = portfolios_df.sort_values("return")

        # Initialize efficient frontier
        efficient_frontier = []

        # Define return range
        min_return = sorted_portfolios["return"].min()
        max_return = sorted_portfolios["return"].max()
        return_range = np.linspace(min_return, max_return, n_points)

        # Find minimum risk portfolio for each return level
        for target_return in return_range:
            # Find portfolios with similar return
            similar_return = sorted_portfolios[
                (sorted_portfolios["return"] >= target_return - 0.001)
                & (sorted_portfolios["return"] <= target_return + 0.001)
            ]

            if len(similar_return) > 0:
                # Find minimum risk portfolio
                min_risk_idx = similar_return["volatility"].idxmin()
                efficient_frontier.append(sorted_portfolios.loc[min_risk_idx])

        return pd.DataFrame(efficient_frontier)

    def _find_target_return_portfolio(self, portfolios_df, target_return, assets):
        """
        Find portfolio with target return

        Args:
            portfolios_df: DataFrame of portfolios
            target_return: Target return
            assets: List of asset names

        Returns:
            portfolio: Dictionary of portfolio with target return
        """
        # Find portfolio with closest return
        closest_idx = (portfolios_df["return"] - target_return).abs().idxmin()

        return {
            "weights": dict(zip(assets, portfolios_df.loc[closest_idx, assets])),
            "return": portfolios_df.loc[closest_idx, "return"],
            "volatility": portfolios_df.loc[closest_idx, "volatility"],
            "sharpe_ratio": portfolios_df.loc[closest_idx, "sharpe_ratio"],
        }

    def _find_target_risk_portfolio(self, portfolios_df, target_risk, assets):
        """
        Find portfolio with target risk

        Args:
            portfolios_df: DataFrame of portfolios
            target_risk: Target risk (volatility)
            assets: List of asset names

        Returns:
            portfolio: Dictionary of portfolio with target risk
        """
        # Find portfolio with closest volatility
        closest_idx = (portfolios_df["volatility"] - target_risk).abs().idxmin()

        return {
            "weights": dict(zip(assets, portfolios_df.loc[closest_idx, assets])),
            "return": portfolios_df.loc[closest_idx, "return"],
            "volatility": portfolios_df.loc[closest_idx, "volatility"],
            "sharpe_ratio": portfolios_df.loc[closest_idx, "sharpe_ratio"],
        }

    def parallel_batch_risk_calculation(
        self,
        returns,
        risk_models=["parametric", "historical", "evt"],
        confidence_levels=[0.95, 0.99],
    ):
        """
        Run batch risk calculation in parallel

        Args:
            returns: Series or DataFrame of returns
            risk_models: List of risk models to use
            confidence_levels: List of confidence levels for VaR and ES

        Returns:
            results: Dictionary of risk calculation results
        """
        logger.info(
            f"Running parallel batch risk calculation with {len(risk_models)} models"
        )
        start_time = time.time()

        # Convert to Series if DataFrame with single column
        if isinstance(returns, pd.DataFrame) and returns.shape[1] == 1:
            returns = returns.iloc[:, 0]

        # Run risk calculations in parallel
        risk_results = Parallel(
            n_jobs=self.n_jobs, backend=self.backend, verbose=self.verbose
        )(
            delayed(self._calculate_risk_metrics)(returns, model, confidence_levels)
            for model in risk_models
        )

        # Combine results
        risk_metrics = {}
        for model, result in zip(risk_models, risk_results):
            risk_metrics[model] = result

        # Calculate time taken
        time_taken = time.time() - start_time

        logger.info(f"Batch risk calculation completed in {time_taken:.2f} seconds")

        return {"risk_metrics": risk_metrics, "time_taken": time_taken}

    def _calculate_risk_metrics(self, returns, model, confidence_levels):
        """
        Calculate risk metrics for a specific model

        Args:
            returns: Series or DataFrame of returns
            model: Risk model to use
            confidence_levels: List of confidence levels

        Returns:
            metrics: Dictionary of risk metrics
        """
        metrics = {}

        # Convert to numpy array
        if isinstance(returns, (pd.Series, pd.DataFrame)):
            returns_array = returns.values
        else:
            returns_array = returns

        # Calculate metrics for each confidence level
        for conf in confidence_levels:
            # Calculate VaR
            if model == "parametric":
                # Parametric VaR (normal distribution)
                mean = np.mean(returns_array)
                std = np.std(returns_array)
                z_score = stats.norm.ppf(conf)  # Use conf directly for left tail
                var = -(mean + z_score * std)

                # Parametric ES
                es = -(mean - std * stats.norm.pdf(z_score) / (1 - conf))

            elif model == "historical":
                # Historical VaR
                var = -np.percentile(returns_array, 100 * (1 - conf))

                # Historical ES
                es = -np.mean(returns_array[returns_array <= -var])

            elif model == "evt":
                try:
                    # Import EVT model if available
                    from services.extreme_value_theory import ExtremeValueRisk

                    # Create and fit EVT model
                    evt_model = ExtremeValueRisk()
                    evt_model.fit_pot(returns_array, threshold_quantile=0.1)

                    # Calculate VaR and ES
                    var = evt_model.calculate_var(conf, method="evt")
                    es = evt_model.calculate_es(conf)
                except ImportError:
                    # Fallback to historical method
                    var = -np.percentile(returns_array, 100 * (1 - conf))
                    es = -np.mean(returns_array[returns_array <= -var])

            else:
                # Default to historical method
                var = -np.percentile(returns_array, 100 * (1 - conf))
                es = -np.mean(returns_array[returns_array <= -var])

            # Store metrics (ensure positive values for loss)
            metrics[f"var_{int(conf*100)}"] = max(0, var)
            metrics[f"es_{int(conf*100)}"] = max(0, es)

        return metrics

    def parallel_stress_testing(
        self, returns, weights, predefined_scenarios=None, n_custom_scenarios=100
    ):
        """
        Run stress testing in parallel

        Args:
            returns: DataFrame of asset returns
            weights: Portfolio weights
            predefined_scenarios: Dictionary of predefined scenarios
            n_custom_scenarios: Number of custom scenarios to generate

        Returns:
            results: Dictionary of stress testing results
        """
        logger.info(
            f"Running parallel stress testing with {n_custom_scenarios} custom scenarios"
        )
        start_time = time.time()

        # Convert weights to array if dict
        if isinstance(weights, dict):
            assets = returns.columns
            weight_array = np.zeros(len(assets))
            for i, asset in enumerate(assets):
                if asset in weights:
                    weight_array[i] = weights[asset]
            weights = weight_array

        # Define predefined scenarios if not provided
        if predefined_scenarios is None:
            predefined_scenarios = {
                "market_crash": {
                    "description": "Market crash scenario",
                    "shocks": {"all": -0.15},
                },
                "interest_rate_spike": {
                    "description": "Interest rate spike",
                    "shocks": {"bonds": -0.05, "equities": -0.03},
                },
                "commodity_shock": {
                    "description": "Commodity price shock",
                    "shocks": {"commodities": -0.10, "energy": -0.15},
                },
                "currency_crisis": {
                    "description": "Currency crisis",
                    "shocks": {"emerging_markets": -0.12, "currencies": -0.08},
                },
                "liquidity_crunch": {
                    "description": "Liquidity crunch",
                    "shocks": {"credit": -0.08, "real_estate": -0.10},
                },
            }

        # Run predefined scenarios in parallel
        predefined_results = Parallel(
            n_jobs=self.n_jobs, backend=self.backend, verbose=self.verbose
        )(
            delayed(self._run_predefined_scenario)(
                returns, weights, scenario_name, scenario
            )
            for scenario_name, scenario in predefined_scenarios.items()
        )

        # Combine predefined scenario results
        predefined_scenario_results = {}
        for scenario_name, result in zip(
            predefined_scenarios.keys(), predefined_results
        ):
            predefined_scenario_results[scenario_name] = result

        # Generate custom scenarios in parallel
        custom_results = Parallel(
            n_jobs=self.n_jobs, backend=self.backend, verbose=self.verbose
        )(
            delayed(self._generate_custom_scenario)(returns, weights)
            for _ in range(n_custom_scenarios)
        )

        # Calculate custom scenario summary
        custom_returns = [result["portfolio_return"] for result in custom_results]
        custom_vars = [result["var_95"] for result in custom_results]

        custom_summary = {
            "count": n_custom_scenarios,
            "avg_return": np.mean(custom_returns),
            "min_return": np.min(custom_returns),
            "max_return": np.max(custom_returns),
            "std_return": np.std(custom_returns),
            "avg_var_95": np.mean(custom_vars),
            "max_var_95": np.max(custom_vars),
        }

        # Find worst case scenarios
        worst_return_idx = np.argmin(custom_returns)
        worst_var_idx = np.argmax(custom_vars)

        worst_case = {
            "worst_return": custom_results[worst_return_idx],
            "worst_var": custom_results[worst_var_idx],
        }

        # Calculate time taken
        time_taken = time.time() - start_time

        logger.info(f"Stress testing completed in {time_taken:.2f} seconds")

        return {
            "predefined_scenarios": predefined_scenario_results,
            "custom_scenarios_summary": custom_summary,
            "worst_case_scenarios": worst_case,
            "time_taken": time_taken,
        }

    def _run_predefined_scenario(self, returns, weights, scenario_name, scenario):
        """
        Run a predefined stress scenario

        Args:
            returns: DataFrame of asset returns
            weights: Portfolio weights
            scenario_name: Name of the scenario
            scenario: Scenario definition

        Returns:
            result: Dictionary of scenario results
        """
        # Apply shocks to returns
        shocked_returns = returns.copy()

        for asset_class, shock in scenario["shocks"].items():
            if asset_class == "all":
                # Apply shock to all assets
                shocked_returns = shocked_returns + shock
            else:
                # Apply shock to specific asset class
                # This is a simplified approach - in practice, you would map assets to asset classes
                for col in shocked_returns.columns:
                    if asset_class.lower() in col.lower():
                        shocked_returns[col] = shocked_returns[col] + shock

        # Calculate portfolio return under scenario
        portfolio_return = np.dot(shocked_returns.mean(), weights)

        # Calculate VaR under scenario
        portfolio_returns = shocked_returns.dot(weights)
        var_95 = -np.percentile(portfolio_returns, 5)
        var_99 = -np.percentile(portfolio_returns, 1)

        # Calculate ES under scenario
        es_95 = -portfolio_returns[portfolio_returns <= -var_95].mean()
        es_99 = -portfolio_returns[portfolio_returns <= -var_99].mean()

        return {
            "scenario_name": scenario_name,
            "description": scenario["description"],
            "shocks": scenario["shocks"],
            "portfolio_return": portfolio_return,
            "var_95": var_95,
            "var_99": var_99,
            "es_95": es_95,
            "es_99": es_99,
        }

    def _generate_custom_scenario(self, returns, weights):
        """
        Generate a custom stress scenario

        Args:
            returns: DataFrame of asset returns
            weights: Portfolio weights

        Returns:
            result: Dictionary of scenario results
        """
        # Calculate mean and covariance
        returns.mean()
        cov_matrix = returns.cov()

        # Generate random shock factors
        shock_factors = np.random.normal(0, 1, len(returns.columns))

        # Apply shocks based on covariance structure
        chol_decomp = np.linalg.cholesky(cov_matrix)
        shocks = (
            np.dot(chol_decomp, shock_factors) * 3
        )  # Scale for more extreme scenarios

        # Create shocked returns
        shocked_returns = returns.copy()
        for i, col in enumerate(shocked_returns.columns):
            shocked_returns[col] = shocked_returns[col] + shocks[i]

        # Calculate portfolio return under scenario
        portfolio_return = np.dot(shocked_returns.mean(), weights)

        # Calculate VaR under scenario
        portfolio_returns = shocked_returns.dot(weights)
        var_95 = -np.percentile(portfolio_returns, 5)
        var_99 = -np.percentile(portfolio_returns, 1)

        # Calculate ES under scenario
        es_95 = -portfolio_returns[portfolio_returns <= -var_95].mean()
        es_99 = -portfolio_returns[portfolio_returns <= -var_99].mean()

        return {
            "scenario_type": "custom",
            "shocks": dict(zip(returns.columns, shocks)),
            "portfolio_return": portfolio_return,
            "var_95": var_95,
            "var_99": var_99,
            "es_95": es_95,
            "es_99": es_99,
        }

    def parallel_backtest(
        self,
        returns,
        risk_models=["parametric", "historical", "evt"],
        confidence_level=0.95,
        window_size=252,
        step_size=20,
    ):
        """
        Run backtesting of risk models in parallel

        Args:
            returns: Series or DataFrame of returns
            risk_models: List of risk models to use
            confidence_level: Confidence level for VaR
            window_size: Size of rolling window
            step_size: Step size for rolling window

        Returns:
            results: Dictionary of backtesting results
        """
        logger.info(f"Running parallel backtesting with window size {window_size}")
        start_time = time.time()

        # Convert to Series if DataFrame with single column
        if isinstance(returns, pd.DataFrame) and returns.shape[1] == 1:
            returns = returns.iloc[:, 0]

        # Determine number of windows
        n_returns = len(returns)
        n_windows = (n_returns - window_size) // step_size + 1

        # Run backtests in parallel
        backtest_results = Parallel(
            n_jobs=self.n_jobs, backend=self.backend, verbose=self.verbose
        )(
            delayed(self._run_backtest_window)(
                returns, i, window_size, step_size, risk_models, confidence_level
            )
            for i in range(n_windows)
        )

        # Combine results
        windows = []
        breaches = {model: 0 for model in risk_models}

        for result in backtest_results:
            windows.append(result)

            for model in risk_models:
                if result[f"{model}_breach"]:
                    breaches[model] += 1

        # Calculate breach rates
        expected_breach_rate = 1 - confidence_level
        summary = {}

        for model in risk_models:
            breach_rate = breaches[model] / n_windows
            breach_ratio = breach_rate / expected_breach_rate

            summary[model] = {
                "breaches": breaches[model],
                "total": n_windows,
                "breach_rate": breach_rate,
                "expected_breach_rate": expected_breach_rate,
                "breach_ratio": breach_ratio,
            }

        # Calculate time taken
        time_taken = time.time() - start_time

        logger.info(f"Backtesting completed in {time_taken:.2f} seconds")

        return {"summary": summary, "windows": windows, "time_taken": time_taken}

    def _run_backtest_window(
        self, returns, window_idx, window_size, step_size, risk_models, confidence_level
    ):
        """
        Run backtest for a specific window

        Args:
            returns: Series or DataFrame of returns
            window_idx: Window index
            window_size: Size of rolling window
            step_size: Step size for rolling window
            risk_models: List of risk models to use
            confidence_level: Confidence level for VaR

        Returns:
            result: Dictionary of window results
        """
        # Calculate window indices
        start_idx = window_idx * step_size
        end_idx = start_idx + window_size
        test_idx = end_idx

        # Extract window and test return
        window_returns = returns.iloc[start_idx:end_idx]

        test_return_value = np.nan
        if test_idx < len(returns):
            # Ensure test_return is a scalar
            test_return_value = returns.iloc[test_idx]
            if isinstance(test_return_value, (pd.Series, pd.DataFrame)):
                test_return_value = test_return_value.iloc[0]  # Assuming single value

        # Calculate VaR for each model
        result = {
            "window_idx": window_idx,
            "start_idx": start_idx,
            "end_idx": end_idx,
            "test_idx": test_idx,
            "test_return": test_return_value,
        }

        for model in risk_models:
            # Calculate VaR
            if model == "parametric":
                # Parametric VaR (normal distribution)
                mean = np.mean(window_returns)
                std = np.std(window_returns)
                z_score = stats.norm.ppf(1 - confidence_level)
                var = -(mean + z_score * std)

            elif model == "historical":
                # Historical VaR
                var = -np.percentile(window_returns, 100 * (1 - confidence_level))

            elif model == "evt":
                try:
                    # Import EVT model if available
                    from services.extreme_value_theory import ExtremeValueRisk

                    # Create and fit EVT model
                    evt_model = ExtremeValueRisk()
                    evt_model.fit_pot(window_returns, threshold_quantile=0.1)

                    # Calculate VaR
                    var = evt_model.calculate_var(confidence_level, method="evt")
                except ImportError:
                    # Fallback to historical method
                    var = -np.percentile(window_returns, 100 * (1 - confidence_level))

            else:
                # Default to historical method
                var = -np.percentile(window_returns, 100 * (1 - confidence_level))

            # Check for breach
            breach = False
            if not np.isnan(test_return_value):
                breach = test_return_value < -var

            # Store results
            result[f"{model}_var"] = var
            result[f"{model}_breach"] = breach

        return result

    def parallel_sensitivity_analysis(
        self, returns, weights, shock_range=(-0.1, 0.1), n_points=10
    ):
        """
        Run sensitivity analysis in parallel

        Args:
            returns: DataFrame of asset returns
            weights: Portfolio weights
            shock_range: Range of shocks to apply (min, max)
            n_points: Number of points in the shock range

        Returns:
            results: Dictionary of sensitivity analysis results
        """
        logger.info(f"Running parallel sensitivity analysis with {n_points} points")
        start_time = time.time()

        # Convert weights to dict if array
        if isinstance(weights, np.ndarray):
            weights = dict(zip(returns.columns, weights))

        # Generate shock points
        shock_points = np.linspace(shock_range[0], shock_range[1], n_points)

        # Run sensitivity analysis for each factor in parallel
        factor_results = {}
        sensitivities = {}

        for factor in returns.columns:
            # Run sensitivity analysis for factor
            factor_result = self._analyze_factor_sensitivity(
                returns, weights, factor, shock_points
            )
            factor_results[factor] = factor_result

            # Calculate sensitivities
            return_sensitivity = (
                factor_result["portfolio_returns"][-1]
                - factor_result["portfolio_returns"][0]
            ) / (shock_points[-1] - shock_points[0])

            var_sensitivity = (
                factor_result["var_95"][-1] - factor_result["var_95"][0]
            ) / (shock_points[-1] - shock_points[0])

            sensitivities[factor] = {
                "return_sensitivity": return_sensitivity,
                "var_sensitivity": var_sensitivity,
            }

        # Calculate time taken
        time_taken = time.time() - start_time

        logger.info(f"Sensitivity analysis completed in {time_taken:.2f} seconds")

        return {
            "factor_results": factor_results,
            "sensitivities": sensitivities,
            "time_taken": time_taken,
        }

    def _analyze_factor_sensitivity(self, returns, weights, factor, shock_points):
        """
        Analyze sensitivity to a specific factor

        Args:
            returns: DataFrame of asset returns
            weights: Portfolio weights
            factor: Factor to analyze
            shock_points: Points in the shock range

        Returns:
            result: Dictionary of factor sensitivity results
        """
        # Initialize result arrays
        n_points = len(shock_points)
        portfolio_returns = np.zeros(n_points)
        portfolio_volatilities = np.zeros(n_points)
        var_95 = np.zeros(n_points)
        es_95 = np.zeros(n_points)

        # Apply shocks and calculate metrics
        for i, shock in enumerate(shock_points):
            # Apply shock to factor
            shocked_returns = returns.copy()
            shocked_returns[factor] = shocked_returns[factor] + shock

            # Calculate portfolio metrics
            portfolio_return = 0
            portfolio_volatility = 0

            for asset, weight in weights.items():
                if asset in shocked_returns.columns:
                    portfolio_return += shocked_returns[asset].mean() * weight
                    portfolio_volatility += shocked_returns[asset].std() * weight

            # Calculate portfolio returns for VaR and ES
            portfolio_rets = 0
            for asset, weight in weights.items():
                if asset in shocked_returns.columns:
                    portfolio_rets += shocked_returns[asset] * weight

            # Calculate VaR and ES
            var = -np.percentile(portfolio_rets, 5)
            es = -portfolio_rets[portfolio_rets <= -var].mean()

            # Store results
            portfolio_returns[i] = portfolio_return
            portfolio_volatilities[i] = portfolio_volatility
            var_95[i] = var
            es_95[i] = es

        return {
            "factor": factor,
            "shocks": shock_points,
            "portfolio_returns": portfolio_returns,
            "portfolio_volatilities": portfolio_volatilities,
            "var_95": var_95,
            "es_95": es_95,
        }

    def parallel_risk_decomposition(self, returns, weights, risk_measure="volatility"):
        """
        Run risk decomposition in parallel

        Args:
            returns: DataFrame of asset returns
            weights: Portfolio weights
            risk_measure: Risk measure to decompose ("volatility", "var", "es")

        Returns:
            results: Dictionary of risk decomposition results
        """
        logger.info(f"Running parallel risk decomposition for {risk_measure}")
        start_time = time.time()

        # Convert weights to dict if array
        if isinstance(weights, np.ndarray):
            weights = dict(zip(returns.columns, weights))

        # Calculate portfolio risk
        if risk_measure == "volatility":
            # Calculate covariance matrix
            cov_matrix = returns.cov()

            # Calculate portfolio volatility
            weight_array = np.array(
                [weights.get(asset, 0) for asset in returns.columns]
            )
            portfolio_risk = np.sqrt(
                np.dot(weight_array.T, np.dot(cov_matrix, weight_array))
            )

            # Calculate marginal contributions
            marginal_contributions = np.dot(cov_matrix, weight_array) / portfolio_risk

            # Calculate component contributions
            component_contributions = weight_array * marginal_contributions

            # Calculate percentage contributions
            percentage_contributions = component_contributions / portfolio_risk

        elif risk_measure == "var" or risk_measure == "es":
            # Calculate portfolio returns
            portfolio_returns = 0
            for asset, weight in weights.items():
                if asset in returns.columns:
                    portfolio_returns += returns[asset] * weight

            # Calculate portfolio risk
            if risk_measure == "var":
                portfolio_risk = -np.percentile(portfolio_returns, 5)  # 95% VaR
            else:  # es
                var_95 = -np.percentile(portfolio_returns, 5)
                portfolio_risk = -portfolio_returns[portfolio_returns <= -var_95].mean()

            # Calculate marginal and component contributions using parallel processing
            contributions = Parallel(
                n_jobs=self.n_jobs, backend=self.backend, verbose=self.verbose
            )(
                delayed(self._calculate_risk_contribution)(
                    returns, weights, asset, risk_measure
                )
                for asset in returns.columns
            )

            # Extract results
            marginal_contributions = np.array(
                [c["marginal_contribution"] for c in contributions]
            )
            component_contributions = np.array(
                [c["component_contribution"] for c in contributions]
            )
            percentage_contributions = np.array(
                [c["percentage_contribution"] for c in contributions]
            )

        else:
            raise ValueError(f"Unsupported risk measure: {risk_measure}")

        # Create result dictionary
        contributions = []
        for i, asset in enumerate(returns.columns):
            contributions.append(
                {
                    "asset": asset,
                    "weight": weights.get(asset, 0),
                    "marginal_contribution": marginal_contributions[i],
                    "component_contribution": component_contributions[i],
                    "percentage_contribution": percentage_contributions[i],
                }
            )

        # Sort by percentage contribution
        contributions.sort(key=lambda x: x["percentage_contribution"], reverse=True)

        # Calculate time taken
        time_taken = time.time() - start_time

        logger.info(f"Risk decomposition completed in {time_taken:.2f} seconds")

        return {
            "risk_measure": risk_measure,
            "total_risk": portfolio_risk,
            "contributions": contributions,
            "time_taken": time_taken,
        }

    def _calculate_risk_contribution(self, returns, weights, asset, risk_measure):
        """
        Calculate risk contribution for a specific asset

        Args:
            returns: DataFrame of asset returns
            weights: Portfolio weights
            asset: Asset to analyze
            risk_measure: Risk measure to decompose

        Returns:
            result: Dictionary of risk contribution results
        """
        # Calculate base portfolio risk
        portfolio_returns = 0
        for a, weight in weights.items():
            if a in returns.columns:
                portfolio_returns += returns[a] * weight

        if risk_measure == "var":
            base_risk = -np.percentile(portfolio_returns, 5)  # 95% VaR
        else:  # es
            var_95 = -np.percentile(portfolio_returns, 5)
            base_risk = -portfolio_returns[portfolio_returns <= -var_95].mean()

        # Calculate marginal contribution using finite difference approximation
        delta = 0.0001
        modified_weights = weights.copy()
        modified_weights[asset] = weights.get(asset, 0) + delta

        # Normalize weights
        total_weight = sum(modified_weights.values())
        for a in modified_weights:
            modified_weights[a] /= total_weight

        # Calculate modified portfolio risk
        modified_portfolio_returns = 0
        for a, weight in modified_weights.items():
            if a in returns.columns:
                modified_portfolio_returns += returns[a] * weight

        if risk_measure == "var":
            modified_risk = -np.percentile(modified_portfolio_returns, 5)
        else:  # es
            var_95 = -np.percentile(modified_portfolio_returns, 5)
            modified_risk = -modified_portfolio_returns[
                modified_portfolio_returns <= -var_95
            ].mean()

        # Calculate marginal contribution
        marginal_contribution = (modified_risk - base_risk) / delta

        # Calculate component contribution
        component_contribution = weights.get(asset, 0) * marginal_contribution

        # Calculate percentage contribution
        percentage_contribution = (
            component_contribution / base_risk if base_risk != 0 else 0
        )

        return {
            "asset": asset,
            "marginal_contribution": marginal_contribution,
            "component_contribution": component_contribution,
            "percentage_contribution": percentage_contribution,
        }

    def system_info(self):
        """
        Get system information

        Returns:
            info: Dictionary of system information
        """
        # Get CPU information
        cpu_count = mp.cpu_count()
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
        except:
            cpu_percent = None

        # Get memory information
        try:
            memory = psutil.virtual_memory()
            memory_info = {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
            }
        except:
            memory_info = None

        return {
            "cpu_count": cpu_count,
            "cpu_percent": cpu_percent,
            "memory": memory_info,
            "backend": self.backend,
            "n_jobs": self.n_jobs,
        }


# Example usage
if __name__ == "__main__":
    # Generate sample data
    np.random.seed(42)
    n_days = 1000

    # Create asset returns
    returns = pd.DataFrame(
        {
            "Asset_1": np.random.normal(0.001, 0.02, n_days),
            "Asset_2": np.random.normal(0.0005, 0.015, n_days),
            "Asset_3": np.random.normal(0.0008, 0.025, n_days),
        }
    )

    # Add date index
    returns.index = pd.date_range(start="2020-01-01", periods=n_days, freq="B")

    # Create portfolio weights
    weights = {"Asset_1": 0.4, "Asset_2": 0.3, "Asset_3": 0.3}

    # Create parallel risk engine
    engine = ParallelRiskEngine(n_jobs=4)

    # Run batch risk calculation
    result = engine.parallel_batch_risk_calculation(
        returns.mean(axis=1),
        risk_models=["parametric", "historical"],
        confidence_levels=[0.95, 0.99],
    )

    print("Batch Risk Calculation Results:")
    for model, metrics in result["risk_metrics"].items():
        print(f"  {model}:")
        for metric, value in metrics.items():
            print(f"    {metric}: {value:.6f}")

    # Run portfolio optimization
    result = engine.parallel_portfolio_optimization(
        returns, risk_model="markowitz", n_portfolios=1000
    )

    print("\nPortfolio Optimization Results:")
    print(f"  Max Sharpe Ratio: {result['max_sharpe_portfolio']['sharpe_ratio']:.4f}")
    print(f"  Min Volatility: {result['min_volatility_portfolio']['volatility']:.4f}")

    # Run risk decomposition
    result = engine.parallel_risk_decomposition(
        returns, weights, risk_measure="volatility"
    )

    print("\nRisk Decomposition Results:")
    for contribution in result["contributions"]:
        print(
            f"  {contribution['asset']}: {contribution['percentage_contribution']:.2%}"
        )

    # Get system info
    info = engine.system_info()
    print(
        f"\nSystem Info: {info['cpu_count']} CPUs, {info['backend']} backend, {info['n_jobs']} jobs"
    )
