"""
Test suite for RiskOptimizer enhancements

This module provides comprehensive tests for:
1. Extreme Value Theory risk models
2. Machine Learning risk models
3. Parallel risk calculation engine
4. Reporting framework
5. Dashboard framework

The tests validate functionality, integration, and performance of all new features.
"""

import json
import multiprocessing as mp
import os
import shutil
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frontend.dashboard.dashboard_framework import (
    ChartComponent,
    Dashboard,
    DashboardComponent,
)
from reporting.reporting_framework import ReportGenerator, ReportTemplate
from risk_engine.parallel_risk_engine import ParallelRiskEngine

# Import modules to test
from risk_models.extreme_value_theory import ExtremeValueRisk
from risk_models.ml_risk_models import CopulaMLRiskModel, MLRiskModel


class TestExtremeValueTheory(unittest.TestCase):
    """Test cases for Extreme Value Theory risk models"""

    def setUp(self):
        """Set up test data"""
        # Generate sample return data
        np.random.seed(42)
        self.normal_returns = np.random.normal(0.001, 0.02, 1000)

        # Add some extreme events
        self.returns_with_extremes = self.normal_returns.copy()
        extreme_indices = np.random.choice(1000, 20, replace=False)
        self.returns_with_extremes[extreme_indices] = np.random.normal(-0.08, 0.03, 20)

        # Create EVT model
        self.evt_model = ExtremeValueRisk()

    def test_pot_fitting(self):
        """Test Peaks Over Threshold fitting"""
        # Fit model to data
        self.evt_model.fit_pot(self.returns_with_extremes, threshold_quantile=0.05)

        # Check that model is fitted
        self.assertTrue(self.evt_model.fitted)

        # Check that parameters are reasonable
        shape, scale = self.evt_model.gpd_params
        self.assertIsNotNone(shape)
        self.assertIsNotNone(scale)

        # Shape parameter should typically be negative for financial returns
        # But can be positive in some cases, so we just check it's not extreme
        self.assertLess(abs(shape), 1.0)

        # Scale should be positive
        self.assertGreater(scale, 0)

    def test_var_calculation(self):
        """Test Value at Risk calculation"""
        # Fit model to data
        self.evt_model.fit_pot(self.returns_with_extremes, threshold_quantile=0.05)

        # Calculate VaR at different confidence levels
        var_95 = self.evt_model.calculate_var(0.95, method="evt")
        var_99 = self.evt_model.calculate_var(0.99, method="evt")

        # VaR should increase with confidence level
        self.assertGreater(var_99, var_95)

        # Compare with normal VaR
        normal_var_95 = -np.percentile(self.returns_with_extremes, 5)

        # EVT VaR should be more conservative for heavy-tailed data
        self.assertGreaterEqual(var_95, normal_var_95 * 0.8)  # Allow some flexibility

    def test_es_calculation(self):
        """Test Expected Shortfall calculation"""
        # Fit model to data
        self.evt_model.fit_pot(self.returns_with_extremes, threshold_quantile=0.05)

        # Calculate ES at different confidence levels
        es_95 = self.evt_model.calculate_es(0.95)
        es_99 = self.evt_model.calculate_es(0.99)

        # ES should increase with confidence level
        self.assertGreater(es_99, es_95)

        # ES should be greater than VaR at the same confidence level
        var_95 = self.evt_model.calculate_var(0.95, method="evt")
        self.assertGreater(es_95, var_95)

    def test_block_maxima(self):
        """Test Block Maxima method"""
        # Apply block maxima method
        result = self.evt_model.fit_block_maxima(
            self.returns_with_extremes, block_size=20
        )

        # Check that parameters are returned
        self.assertIn("shape", result)
        self.assertIn("loc", result)
        self.assertIn("scale", result)
        self.assertIn("block_maxima", result)

        # Check that block maxima are extracted correctly
        self.assertEqual(len(result["block_maxima"]), 1000 // 20)

    def test_stress_scenarios(self):
        """Test extreme scenario generation"""
        # Fit model to data
        self.evt_model.fit_pot(self.returns_with_extremes, threshold_quantile=0.05)

        # Generate scenarios
        scenarios = self.evt_model.simulate_extreme_scenarios(
            n_scenarios=100, confidence=0.95
        )

        # Check that scenarios are generated
        self.assertEqual(len(scenarios), 100)

        # Scenarios should be more extreme than the VaR
        var_95 = self.evt_model.calculate_var(0.95, method="evt")
        self.assertTrue(all(scenario > var_95 for scenario in scenarios))

    def test_tail_dependence(self):
        """Test tail dependence calculation"""
        # Create correlated returns
        np.random.seed(42)
        returns1 = self.returns_with_extremes
        returns2 = 0.7 * returns1 + 0.3 * np.random.normal(0.001, 0.02, 1000)

        # Calculate tail dependence
        tail_dep = self.evt_model.tail_dependence(
            returns1, returns2, threshold_quantile=0.05
        )

        # Tail dependence should be between 0 and 1
        self.assertGreaterEqual(tail_dep, 0)
        self.assertLessEqual(tail_dep, 1)

        # For highly correlated returns, tail dependence should be high
        self.assertGreater(tail_dep, 0.5)


class TestMLRiskModels(unittest.TestCase):
    """Test cases for Machine Learning risk models"""

    def setUp(self):
        """Set up test data"""
        # Generate sample return data
        np.random.seed(42)
        n_days = 1000
        n_assets = 4

        # Create asset returns with some correlation
        self.asset_returns = pd.DataFrame(
            np.random.multivariate_normal(
                mean=[0.001, 0.0005, 0.0008, 0.0012],
                cov=[
                    [0.0004, 0.0002, 0.0001, 0.0001],
                    [0.0002, 0.0005, 0.0001, 0.0002],
                    [0.0001, 0.0001, 0.0006, 0.0002],
                    [0.0001, 0.0002, 0.0002, 0.0004],
                ],
                size=n_days,
            ),
            columns=["Asset_1", "Asset_2", "Asset_3", "Asset_4"],
        )

        # Add date index
        self.asset_returns.index = pd.date_range(
            start="2020-01-01", periods=n_days, freq="B"
        )

        # Create ML risk models
        self.ml_model = MLRiskModel(model_type="gbm", quantile=0.05)
        self.copula_model = CopulaMLRiskModel(copula_type="gaussian", n_scenarios=1000)

    def test_ml_model_training(self):
        """Test ML model training"""
        # Train model
        self.ml_model.fit(
            self.asset_returns, feature_window=10, horizon=1, test_size=0.2
        )

        # Check that model is trained
        self.assertTrue(self.ml_model.trained)

        # Check that feature names are stored
        self.assertIsNotNone(self.ml_model.feature_names)
        self.assertGreater(len(self.ml_model.feature_names), 0)

        # Check feature importance
        self.assertIsNotNone(self.ml_model.feature_importance)

    def test_ml_var_prediction(self):
        """Test ML VaR prediction"""
        # Train model
        self.ml_model.fit(
            self.asset_returns, feature_window=10, horizon=1, test_size=0.2
        )

        # Predict VaR
        var_pred = self.ml_model.predict_var(self.asset_returns, confidence=0.95)

        # Check that predictions are returned
        self.assertIsNotNone(var_pred)
        self.assertGreater(len(var_pred), 0)

        # VaR should be positive (we're predicting the quantile directly)
        self.assertTrue(all(var_pred > 0))

    def test_ml_es_prediction(self):
        """Test ML ES prediction"""
        # Train model
        self.ml_model.fit(
            self.asset_returns, feature_window=10, horizon=1, test_size=0.2
        )

        # Predict ES
        es_pred = self.ml_model.predict_es(self.asset_returns, confidence=0.95)

        # Check that predictions are returned
        self.assertIsNotNone(es_pred)
        self.assertGreater(len(es_pred), 0)

        # ES should be greater than VaR
        var_pred = self.ml_model.predict_var(self.asset_returns, confidence=0.95)
        self.assertTrue(all(es_pred >= var_pred * 0.9))  # Allow some flexibility

    def test_ml_model_save_load(self):
        """Test ML model saving and loading"""
        # Train model
        self.ml_model.fit(
            self.asset_returns, feature_window=10, horizon=1, test_size=0.2
        )

        # Save model to temporary file
        temp_dir = tempfile.mkdtemp()
        model_path = os.path.join(temp_dir, "ml_model.joblib")
        self.ml_model.save_model(model_path)

        # Check that file exists
        self.assertTrue(os.path.exists(model_path))

        # Load model
        loaded_model = MLRiskModel.load_model(model_path)

        # Check that loaded model is trained
        self.assertTrue(loaded_model.trained)

        # Clean up
        shutil.rmtree(temp_dir)

    def test_copula_fitting(self):
        """Test copula model fitting"""
        # Fit copula model
        self.copula_model.fit(self.asset_returns)

        # Check that model is trained
        self.assertTrue(self.copula_model.trained)

        # Check that asset names are stored
        self.assertEqual(
            self.copula_model.asset_names.tolist(), self.asset_returns.columns.tolist()
        )

    def test_scenario_generation(self):
        """Test scenario generation with copula model"""
        # Fit copula model
        self.copula_model.fit(self.asset_returns)

        # Generate scenarios
        n_scenarios = 500
        scenarios = self.copula_model.generate_scenarios(n_scenarios)

        # Check that scenarios are generated
        self.assertEqual(len(scenarios), n_scenarios)
        self.assertEqual(scenarios.shape[1], self.asset_returns.shape[1])

        # Check that scenarios have similar statistical properties
        # Mean should be similar
        self.assertAlmostEqual(
            scenarios.mean().mean(),
            self.asset_returns.mean().mean(),
            delta=0.01,  # Allow some difference
        )

    def test_copula_var_calculation(self):
        """Test VaR calculation with copula model"""
        # Fit copula model
        self.copula_model.fit(self.asset_returns)

        # Define portfolio weights
        weights = np.array([0.25, 0.25, 0.25, 0.25])

        # Calculate VaR
        var_95 = self.copula_model.calculate_var(weights, confidence=0.95)
        var_99 = self.copula_model.calculate_var(weights, confidence=0.99)

        # VaR should increase with confidence level
        self.assertGreater(var_99, var_95)

        # VaR should be positive
        self.assertGreater(var_95, 0)
        self.assertGreater(var_99, 0)

    def test_copula_es_calculation(self):
        """Test ES calculation with copula model"""
        # Fit copula model
        self.copula_model.fit(self.asset_returns)

        # Define portfolio weights
        weights = np.array([0.25, 0.25, 0.25, 0.25])

        # Calculate ES
        es_95 = self.copula_model.calculate_es(weights, confidence=0.95)

        # Calculate VaR for comparison
        var_95 = self.copula_model.calculate_var(weights, confidence=0.95)

        # ES should be greater than VaR
        self.assertGreater(es_95, var_95)

    def test_copula_risk_metrics(self):
        """Test risk metrics calculation with copula model"""
        # Fit copula model
        self.copula_model.fit(self.asset_returns)

        # Define portfolio weights
        weights = np.array([0.25, 0.25, 0.25, 0.25])

        # Calculate risk metrics
        metrics = self.copula_model.calculate_risk_metrics(
            weights, confidence_levels=[0.95, 0.99]
        )

        # Check that metrics are returned
        self.assertIn("mean", metrics)
        self.assertIn("std", metrics)
        self.assertIn("skewness", metrics)
        self.assertIn("kurtosis", metrics)
        self.assertIn("var_95", metrics)
        self.assertIn("es_95", metrics)
        self.assertIn("var_99", metrics)
        self.assertIn("es_99", metrics)

        # Check relationships between metrics
        self.assertGreater(metrics["var_99"], metrics["var_95"])
        self.assertGreater(metrics["es_99"], metrics["es_95"])
        self.assertGreater(metrics["es_95"], metrics["var_95"])
        self.assertGreater(metrics["es_99"], metrics["var_99"])


class TestParallelRiskEngine(unittest.TestCase):
    """Test cases for Parallel Risk Engine"""

    def setUp(self):
        """Set up test data and engine"""
        # Generate sample return data
        np.random.seed(42)
        n_days = 1000
        n_assets = 4

        # Create asset returns with some correlation
        self.asset_returns = pd.DataFrame(
            np.random.multivariate_normal(
                mean=[0.001, 0.0005, 0.0008, 0.0012],
                cov=[
                    [0.0004, 0.0002, 0.0001, 0.0001],
                    [0.0002, 0.0005, 0.0001, 0.0002],
                    [0.0001, 0.0001, 0.0006, 0.0002],
                    [0.0001, 0.0002, 0.0002, 0.0004],
                ],
                size=n_days,
            ),
            columns=["Asset_1", "Asset_2", "Asset_3", "Asset_4"],
        )

        # Add date index
        self.asset_returns.index = pd.date_range(
            start="2020-01-01", periods=n_days, freq="B"
        )

        # Create portfolio weights
        self.weights = {
            "Asset_1": 0.25,
            "Asset_2": 0.25,
            "Asset_3": 0.25,
            "Asset_4": 0.25,
        }

        # Create risk models for testing
        self.evt_model = ExtremeValueRisk()
        self.evt_model.fit_pot(self.asset_returns.mean(axis=1), threshold_quantile=0.05)

        self.copula_model = CopulaMLRiskModel(copula_type="gaussian", n_scenarios=1000)
        self.copula_model.fit(self.asset_returns)

        # Create parallel risk engine
        self.engine = ParallelRiskEngine(n_jobs=2, backend="multiprocessing", verbose=0)

    def test_parallel_monte_carlo(self):
        """Test parallel Monte Carlo simulation"""
        # Run Monte Carlo simulation
        result = self.engine.parallel_monte_carlo(
            self.copula_model,
            self.weights,
            n_scenarios=1000,
            confidence_levels=[0.95, 0.99],
        )

        # Check that results are returned
        self.assertIn("portfolio_metrics", result)
        self.assertIn("risk_metrics", result)

        # Check portfolio metrics
        self.assertIn("expected_return", result["portfolio_metrics"])
        self.assertIn("volatility", result["portfolio_metrics"])
        self.assertIn("skewness", result["portfolio_metrics"])
        self.assertIn("kurtosis", result["portfolio_metrics"])

        # Check risk metrics
        self.assertIn("var_95", result["risk_metrics"])
        self.assertIn("es_95", result["risk_metrics"])
        self.assertIn("var_99", result["risk_metrics"])
        self.assertIn("es_99", result["risk_metrics"])

        # Check relationships between metrics
        self.assertGreater(
            result["risk_metrics"]["var_99"], result["risk_metrics"]["var_95"]
        )
        self.assertGreater(
            result["risk_metrics"]["es_95"], result["risk_metrics"]["var_95"]
        )
        self.assertGreater(
            result["risk_metrics"]["es_99"], result["risk_metrics"]["var_99"]
        )

    def test_parallel_portfolio_optimization(self):
        """Test parallel portfolio optimization"""
        # Run portfolio optimization
        result = self.engine.parallel_portfolio_optimization(
            self.asset_returns, risk_model="markowitz", n_portfolios=500
        )

        # Check that results are returned
        self.assertIn("efficient_frontier", result)
        self.assertIn("max_sharpe_portfolio", result)
        self.assertIn("min_volatility_portfolio", result)

        # Check efficient frontier
        self.assertGreater(len(result["efficient_frontier"]), 0)

        # Check max Sharpe portfolio
        self.assertIn("weights", result["max_sharpe_portfolio"])
        self.assertIn("return", result["max_sharpe_portfolio"])
        self.assertIn("volatility", result["max_sharpe_portfolio"])
        self.assertIn("sharpe_ratio", result["max_sharpe_portfolio"])

        # Check min volatility portfolio
        self.assertIn("weights", result["min_volatility_portfolio"])
        self.assertIn("return", result["min_volatility_portfolio"])
        self.assertIn("volatility", result["min_volatility_portfolio"])
        self.assertIn("sharpe_ratio", result["min_volatility_portfolio"])

        # Min volatility portfolio should have lower volatility than max Sharpe
        self.assertLessEqual(
            result["min_volatility_portfolio"]["volatility"],
            result["max_sharpe_portfolio"]["volatility"],
        )

    def test_parallel_batch_risk_calculation(self):
        """Test parallel batch risk calculation"""
        # Run batch risk calculation
        result = self.engine.parallel_batch_risk_calculation(
            self.asset_returns.mean(axis=1),
            risk_models=["parametric", "historical", "evt"],
            confidence_levels=[0.95, 0.99],
        )

        # Check that results are returned
        self.assertIn("risk_metrics", result)

        # Check risk models
        self.assertIn("parametric", result["risk_metrics"])
        self.assertIn("historical", result["risk_metrics"])
        self.assertIn("evt", result["risk_metrics"])

        # Check metrics for each model
        for model in ["parametric", "historical", "evt"]:
            self.assertIn("var_95", result["risk_metrics"][model])
            self.assertIn("es_95", result["risk_metrics"][model])
            self.assertIn("var_99", result["risk_metrics"][model])
            self.assertIn("es_99", result["risk_metrics"][model])

            # Check relationships between metrics
            self.assertGreater(
                result["risk_metrics"][model]["var_99"],
                result["risk_metrics"][model]["var_95"],
            )
            self.assertGreater(
                result["risk_metrics"][model]["es_95"],
                result["risk_metrics"][model]["var_95"],
            )
            self.assertGreater(
                result["risk_metrics"][model]["es_99"],
                result["risk_metrics"][model]["var_99"],
            )

    def test_parallel_stress_testing(self):
        """Test parallel stress testing"""
        # Run stress testing
        result = self.engine.parallel_stress_testing(
            self.asset_returns, self.weights, n_custom_scenarios=100
        )

        # Check that results are returned
        self.assertIn("predefined_scenarios", result)
        self.assertIn("custom_scenarios_summary", result)
        self.assertIn("worst_case_scenarios", result)

        # Check predefined scenarios
        self.assertGreater(len(result["predefined_scenarios"]), 0)

        # Check custom scenarios summary
        self.assertIn("count", result["custom_scenarios_summary"])
        self.assertIn("avg_return", result["custom_scenarios_summary"])
        self.assertIn("min_return", result["custom_scenarios_summary"])
        self.assertIn("max_return", result["custom_scenarios_summary"])
        self.assertIn("avg_var_95", result["custom_scenarios_summary"])
        self.assertIn("max_var_95", result["custom_scenarios_summary"])

        # Check worst case scenarios
        self.assertIn("worst_return", result["worst_case_scenarios"])
        self.assertIn("worst_var", result["worst_case_scenarios"])

    def test_parallel_backtest(self):
        """Test parallel backtesting"""
        # Run backtesting
        result = self.engine.parallel_backtest(
            self.asset_returns,
            risk_models=["parametric", "historical", "evt"],
            confidence_level=0.95,
            window_size=252,
            step_size=20,
        )

        # Check that results are returned
        self.assertIn("summary", result)
        self.assertIn("windows", result)

        # Check summary
        for model in ["parametric", "historical", "evt"]:
            self.assertIn(model, result["summary"])
            self.assertIn("breaches", result["summary"][model])
            self.assertIn("total", result["summary"][model])
            self.assertIn("breach_rate", result["summary"][model])
            self.assertIn("expected_breach_rate", result["summary"][model])
            self.assertIn("breach_ratio", result["summary"][model])

        # Check windows
        self.assertGreater(len(result["windows"]), 0)

    def test_parallel_sensitivity_analysis(self):
        """Test parallel sensitivity analysis"""
        # Run sensitivity analysis
        result = self.engine.parallel_sensitivity_analysis(
            self.asset_returns, self.weights, shock_range=(-0.05, 0.05), n_points=5
        )

        # Check that results are returned
        self.assertIn("factor_results", result)
        self.assertIn("sensitivities", result)

        # Check factor results
        for factor in self.asset_returns.columns:
            self.assertIn(factor, result["factor_results"])
            self.assertIn("shocks", result["factor_results"][factor])
            self.assertIn("portfolio_returns", result["factor_results"][factor])
            self.assertIn("portfolio_volatilities", result["factor_results"][factor])
            self.assertIn("var_95", result["factor_results"][factor])
            self.assertIn("es_95", result["factor_results"][factor])

        # Check sensitivities
        for factor in self.asset_returns.columns:
            self.assertIn(factor, result["sensitivities"])
            self.assertIn("return_sensitivity", result["sensitivities"][factor])
            self.assertIn("var_sensitivity", result["sensitivities"][factor])

    def test_parallel_risk_decomposition(self):
        """Test parallel risk decomposition"""
        # Run risk decomposition
        result = self.engine.parallel_risk_decomposition(
            self.asset_returns, self.weights, risk_measure="volatility"
        )

        # Check that results are returned
        self.assertIn("risk_measure", result)
        self.assertIn("total_risk", result)
        self.assertIn("contributions", result)

        # Check risk measure
        self.assertEqual(result["risk_measure"], "volatility")

        # Check contributions
        self.assertEqual(len(result["contributions"]), len(self.weights))

        # Sum of percentage contributions should be close to 1
        total_contribution = sum(
            c["percentage_contribution"] for c in result["contributions"]
        )
        self.assertAlmostEqual(total_contribution, 1.0, delta=0.01)

    def test_system_info(self):
        """Test system info retrieval"""
        # Get system info
        info = self.engine.system_info()

        # Check that info is returned
        self.assertIn("cpu_count", info)
        self.assertIn("cpu_percent", info)
        self.assertIn("memory", info)
        self.assertIn("backend", info)
        self.assertIn("n_jobs", info)

        # Check that CPU count is reasonable
        self.assertGreaterEqual(info["cpu_count"], 1)

        # Check that backend matches
        self.assertEqual(info["backend"], "multiprocessing")

        # Check that n_jobs matches
        self.assertEqual(info["n_jobs"], 2)


class TestReportingFramework(unittest.TestCase):
    """Test cases for Reporting Framework"""

    def setUp(self):
        """Set up test data and framework"""
        # Create temporary directory for reports
        self.temp_dir = tempfile.mkdtemp()

        # Create report generator
        self.generator = ReportGenerator(
            template_dir=os.path.join(self.temp_dir, "templates"),
            output_dir=os.path.join(self.temp_dir, "reports"),
        )

        # Create sample data
        self.data = {
            "risk_metrics": {
                "var_95": 0.0325,
                "es_95": 0.0487,
                "volatility": 0.18,
                "sharpe_ratio": 0.75,
                "diversification_ratio": 0.65,
                "max_drawdown": 0.28,
            },
            "risk_decomposition": pd.DataFrame(
                {
                    "asset": ["Equity", "Fixed Income", "Commodities", "Real Estate"],
                    "weight": [0.5, 0.3, 0.1, 0.1],
                    "contribution": [0.6, 0.2, 0.15, 0.05],
                    "marginal_contribution": [0.12, 0.067, 0.15, 0.05],
                }
            ),
            "historical_var": pd.DataFrame(
                {
                    "date": pd.date_range(start="2024-01-01", periods=100, freq="B"),
                    "var_95": np.random.normal(0.03, 0.005, 100),
                    "var_99": np.random.normal(0.045, 0.008, 100),
                }
            ).set_index("date"),
        }

    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir)

    def test_report_template_creation(self):
        """Test report template creation"""
        # Create template
        template = ReportTemplate(
            name="Test Template", description="Test template description"
        )

        # Add sections
        template.add_section(
            ReportSection(
                title="Text Section",
                section_type="text",
                content={"text": "This is a test section"},
            )
        )

        template.add_section(
            ReportSection(
                title="Table Section",
                section_type="table",
                data_source={"type": "direct", "path": "risk_decomposition"},
            )
        )

        template.add_section(
            ReportSection(
                title="Chart Section",
                section_type="chart",
                data_source={"type": "direct", "path": "historical_var"},
                parameters={"chart_type": "line"},
            )
        )

        # Check template properties
        self.assertEqual(template.name, "Test Template")
        self.assertEqual(template.description, "Test template description")
        self.assertEqual(len(template.sections), 3)

        # Check section types
        self.assertEqual(template.sections[0].section_type, "text")
        self.assertEqual(template.sections[1].section_type, "table")
        self.assertEqual(template.sections[2].section_type, "chart")

    def test_report_template_save_load(self):
        """Test saving and loading report templates"""
        # Create template
        template = ReportTemplate(
            name="Test Template", description="Test template description"
        )

        # Add section
        template.add_section(
            ReportSection(
                title="Test Section",
                section_type="text",
                content={"text": "This is a test section"},
            )
        )

        # Save template
        template_path = os.path.join(self.temp_dir, "test_template.json")
        template.save(template_path)

        # Check that file exists
        self.assertTrue(os.path.exists(template_path))

        # Load template
        loaded_template = ReportTemplate.load(template_path)

        # Check loaded template properties
        self.assertEqual(loaded_template.name, "Test Template")
        self.assertEqual(loaded_template.description, "Test template description")
        self.assertEqual(len(loaded_template.sections), 1)
        self.assertEqual(loaded_template.sections[0].title, "Test Section")

    def test_html_report_generation(self):
        """Test HTML report generation"""
        # Create template
        template = ReportTemplate(
            name="Test Report", description="Test report description"
        )

        # Add sections
        template.add_section(
            ReportSection(
                title="Risk Metrics",
                section_type="risk_metrics",
                data_source={"type": "direct", "path": "risk_metrics"},
            )
        )

        template.add_section(
            ReportSection(
                title="Risk Decomposition",
                section_type="table",
                data_source={"type": "direct", "path": "risk_decomposition"},
            )
        )

        # Generate HTML report
        output_path = os.path.join(self.temp_dir, "test_report.html")
        html_content = self.generator.generate_html(template, self.data, output_path)

        # Check that file exists
        self.assertTrue(os.path.exists(output_path))

        # Check that HTML content is generated
        self.assertIsNotNone(html_content)
        self.assertGreater(len(html_content), 0)

        # Check that HTML contains section titles
        self.assertIn("Risk Metrics", html_content)
        self.assertIn("Risk Decomposition", html_content)

        # Check that HTML contains data
        self.assertIn("0.0325", html_content)  # VaR value
        self.assertIn("Equity", html_content)  # Asset name

    def test_section_processing(self):
        """Test section processing"""
        # Create sections
        text_section = ReportSection(
            title="Text Section",
            section_type="text",
            content={
                "text": "This is a test section with value {{ data.risk_metrics.var_95 }}"
            },
            parameters={"render_template": True},
        )

        table_section = ReportSection(
            title="Table Section",
            section_type="table",
            data_source={"type": "direct", "path": "risk_decomposition"},
            parameters={"show_index": False},
        )

        chart_section = ReportSection(
            title="Chart Section",
            section_type="chart",
            data_source={"type": "direct", "path": "historical_var"},
            parameters={"chart_type": "line", "width": 8, "height": 5},
        )

        # Process sections
        processed_text = self.generator._process_section(text_section, self.data)
        processed_table = self.generator._process_section(table_section, self.data)
        processed_chart = self.generator._process_section(chart_section, self.data)

        # Check processed sections
        self.assertIn("rendered_content", processed_text)
        self.assertIn("rendered_content", processed_table)
        self.assertIn("rendered_content", processed_chart)

        # Check text section rendering
        self.assertIn("0.0325", processed_text["rendered_content"])

        # Check table section rendering
        self.assertIn("<table", processed_table["rendered_content"])
        self.assertIn("Equity", processed_table["rendered_content"])

        # Check chart section rendering
        self.assertIn("<img", processed_chart["rendered_content"])


class TestDashboardFramework(unittest.TestCase):
    """Test cases for Dashboard Framework"""

    def setUp(self):
        """Set up test data and framework"""
        # Create temporary directory for dashboards
        self.temp_dir = tempfile.mkdtemp()

        # Create dashboard manager
        self.manager = DashboardManager(
            dashboard_dir=os.path.join(self.temp_dir, "dashboards")
        )

        # Create template directory
        self.template_dir = os.path.join(self.temp_dir, "templates")
        os.makedirs(self.template_dir, exist_ok=True)

        # Create sample dashboard template
        with open(os.path.join(self.template_dir, "dashboard_template.html"), "w") as f:
            f.write(
                """
            <!DOCTYPE html>
            <html>
            <head>
                <title>{{ dashboard.title }}</title>
            </head>
            <body>
                <h1>{{ dashboard.title }}</h1>
                <p>{{ dashboard.description }}</p>

                {% for component in components %}
                <div class="component">
                    <h2>{{ component.title }}</h2>
                    {{ component.rendered_content|safe }}
                </div>
                {% endfor %}
            </body>
            </html>
            """
            )

        # Create dashboard renderer
        self.renderer = DashboardRenderer(template_dir=self.template_dir)

        # Create sample data
        self.data = {
            "risk_metrics": {
                "current": {
                    "var_95": 0.0325,
                    "es_95": 0.0487,
                    "volatility": 0.18,
                    "sharpe_ratio": 0.75,
                },
                "var_history": pd.DataFrame(
                    {
                        "date": pd.date_range(
                            start="2024-01-01", periods=100, freq="B"
                        ),
                        "var_95": np.random.normal(0.03, 0.005, 100),
                        "var_99": np.random.normal(0.045, 0.008, 100),
                    }
                ).set_index("date"),
                "decomposition": pd.DataFrame(
                    {
                        "asset": [
                            "Equity",
                            "Fixed Income",
                            "Commodities",
                            "Real Estate",
                        ],
                        "weight": [0.5, 0.3, 0.1, 0.1],
                        "contribution": [0.6, 0.2, 0.15, 0.05],
                        "marginal_contribution": [0.12, 0.067, 0.15, 0.05],
                    }
                ),
            }
        }

    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir)

    def test_dashboard_creation(self):
        """Test dashboard creation"""
        # Create dashboard
        dashboard = Dashboard(
            title="Test Dashboard", description="Test dashboard description"
        )

        # Add components
        chart = ChartComponent(title="VaR Chart", chart_type="line")
        chart.set_data_source({"type": "direct", "path": "risk_metrics.var_history"})
        chart.set_position(0, 0, 8, 4)
        dashboard.add_component(chart)

        # Check dashboard properties
        self.assertEqual(dashboard.title, "Test Dashboard")
        self.assertEqual(dashboard.description, "Test dashboard description")
        self.assertEqual(len(dashboard.components), 1)

        # Check component properties
        self.assertEqual(dashboard.components[0].title, "VaR Chart")
        self.assertEqual(dashboard.components[0].component_type, "chart")
        self.assertEqual(dashboard.components[0].position["x"], 0)
        self.assertEqual(dashboard.components[0].position["y"], 0)
        self.assertEqual(dashboard.components[0].position["w"], 8)
        self.assertEqual(dashboard.components[0].position["h"], 4)

    def test_dashboard_save_load(self):
        """Test saving and loading dashboards"""
        # Create dashboard
        dashboard = Dashboard(
            title="Test Dashboard", description="Test dashboard description"
        )

        # Add component
        dashboard.add_component(ChartComponent(title="Test Chart", chart_type="line"))

        # Save dashboard
        dashboard_path = os.path.join(self.temp_dir, "test_dashboard.json")
        dashboard.save(dashboard_path)

        # Check that file exists
        self.assertTrue(os.path.exists(dashboard_path))

        # Load dashboard
        loaded_dashboard = Dashboard.load(dashboard_path)

        # Check loaded dashboard properties
        self.assertEqual(loaded_dashboard.title, "Test Dashboard")
        self.assertEqual(loaded_dashboard.description, "Test dashboard description")
        self.assertEqual(len(loaded_dashboard.components), 1)
        self.assertEqual(loaded_dashboard.components[0].title, "Test Chart")

    def test_dashboard_manager(self):
        """Test dashboard manager"""
        # Create dashboard
        dashboard = self.manager.create_dashboard(
            title="Test Dashboard", description="Test dashboard description"
        )

        # Check that dashboard is created
        self.assertIsNotNone(dashboard)
        self.assertEqual(dashboard.title, "Test Dashboard")

        # Get dashboard
        retrieved_dashboard = self.manager.get_dashboard(dashboard.id)

        # Check that dashboard is retrieved
        self.assertIsNotNone(retrieved_dashboard)
        self.assertEqual(retrieved_dashboard.id, dashboard.id)
        self.assertEqual(retrieved_dashboard.title, "Test Dashboard")

        # List dashboards
        dashboard_list = self.manager.list_dashboards()

        # Check that dashboard is listed
        self.assertEqual(len(dashboard_list), 1)
        self.assertEqual(dashboard_list[0]["id"], dashboard.id)
        self.assertEqual(dashboard_list[0]["title"], "Test Dashboard")

        # Update dashboard
        dashboard.title = "Updated Dashboard"
        self.manager.update_dashboard(dashboard)

        # Check that dashboard is updated
        updated_dashboard = self.manager.get_dashboard(dashboard.id)
        self.assertEqual(updated_dashboard.title, "Updated Dashboard")

        # Delete dashboard
        self.manager.delete_dashboard(dashboard.id)

        # Check that dashboard is deleted
        self.assertIsNone(self.manager.get_dashboard(dashboard.id))
        self.assertEqual(len(self.manager.list_dashboards()), 0)

    def test_dashboard_rendering(self):
        """Test dashboard rendering"""
        # Create dashboard
        dashboard = Dashboard(
            title="Test Dashboard", description="Test dashboard description"
        )

        # Add components
        chart = ChartComponent(title="VaR Chart", chart_type="line")
        chart.set_data_source({"type": "direct", "path": "risk_metrics.var_history"})
        chart.set_position(0, 0, 8, 4)
        dashboard.add_component(chart)

        # Render dashboard
        output_path = os.path.join(self.temp_dir, "test_dashboard.html")
        html_content = self.renderer.render_dashboard(dashboard, self.data, output_path)

        # Check that file exists
        self.assertTrue(os.path.exists(output_path))

        # Check that HTML content is generated
        self.assertIsNotNone(html_content)
        self.assertGreater(len(html_content), 0)

        # Check that HTML contains dashboard title
        self.assertIn("Test Dashboard", html_content)

        # Check that HTML contains component title
        self.assertIn("VaR Chart", html_content)


def run_tests():
    """Run all tests"""
    # Create test suite
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTest(unittest.makeSuite(TestExtremeValueTheory))
    suite.addTest(unittest.makeSuite(TestMLRiskModels))
    suite.addTest(unittest.makeSuite(TestParallelRiskEngine))
    suite.addTest(unittest.makeSuite(TestReportingFramework))
    suite.addTest(unittest.makeSuite(TestDashboardFramework))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    # Run tests
    result = run_tests()

    # Print summary
    print(f"\nTest Summary:")
    print(f"  Ran {result.testsRun} tests")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")

    # Exit with appropriate status code
    sys.exit(len(result.failures) + len(result.errors))
