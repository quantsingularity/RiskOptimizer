import React, { useEffect, useState } from "react";
import { usePortfolio } from "../context/PortfolioContext";
import { useRiskAnalysis } from "../context/RiskAnalysisContext";
import { useAuth } from "../context/AuthContext";

// Custom hook to integrate dashboard with backend data
export const useDashboardData = () => {
  const { user } = useAuth();
  const {
    portfolio,
    fetchPortfolio,
    loading: portfolioLoading,
  } = usePortfolio();
  const { riskMetrics, loading: riskLoading } = useRiskAnalysis();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardData, setDashboardData] = useState({
    portfolioValue: 0,
    dailyChange: 0,
    riskScore: 0,
    sharpeRatio: 0,
    performanceData: [],
    assetAllocation: [],
    riskMetrics: {},
    recentTransactions: [],
  });

  useEffect(() => {
    const loadDashboardData = async () => {
      setLoading(true);
      setError(null);

      try {
        if (user && user.address) {
          // Fetch portfolio data
          await fetchPortfolio(user.address);

          // For demo purposes, we'll set some mock data
          // In a real app, this would come from the backend
          setDashboardData({
            portfolioValue: 124532.89,
            dailyChange: 1245.67,
            riskScore: 65,
            sharpeRatio: 1.87,
            performanceData: generateMockPerformanceData(),
            assetAllocation: generateMockAssetAllocation(),
            riskMetrics: {
              valueAtRisk: 4532.12,
              maxDrawdown: -12.4,
              volatility: 14.2,
              beta: 0.85,
            },
            recentTransactions: generateMockTransactions(),
          });
        }
      } catch (err) {
        setError(err.message || "Failed to load dashboard data");
        console.error("Dashboard data loading error:", err);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, [user, fetchPortfolio]);

  return {
    loading: loading || portfolioLoading || riskLoading,
    error,
    dashboardData,
  };
};

// Helper functions to generate mock data
const generateMockPerformanceData = () => {
  const data = [];
  const now = new Date();

  // Generate data for the past year
  for (let i = 365; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);

    data.push({
      date: date.toISOString().split("T")[0],
      value: 100000 + Math.random() * 30000,
    });
  }

  return data;
};

const generateMockAssetAllocation = () => {
  return [
    { name: "Stocks", value: 60 },
    { name: "Bonds", value: 20 },
    { name: "Crypto", value: 10 },
    { name: "Cash", value: 5 },
    { name: "Gold", value: 5 },
  ];
};

const generateMockTransactions = () => {
  return [
    { date: "2025-04-05", asset: "AAPL", type: "Buy", amount: "$2,500.00" },
    { date: "2025-04-01", asset: "TSLA", type: "Sell", amount: "$1,800.00" },
    { date: "2025-03-28", asset: "BTC", type: "Buy", amount: "$1,000.00" },
    { date: "2025-03-15", asset: "MSFT", type: "Buy", amount: "$3,200.00" },
    { date: "2025-03-10", asset: "GLD", type: "Sell", amount: "$2,100.00" },
  ];
};

export default useDashboardData;
