import React, { useEffect, useState } from 'react';
import { usePortfolio } from '../context/PortfolioContext';
import { useRiskAnalysis } from '../context/RiskAnalysisContext';

// Custom hook to integrate portfolio management with backend data
export const usePortfolioManagement = () => {
  const { portfolio, fetchPortfolio, savePortfolio, loading: portfolioLoading } = usePortfolio();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [portfolioData, setPortfolioData] = useState({
    assets: [],
    transactions: []
  });

  useEffect(() => {
    const loadPortfolioData = async () => {
      setLoading(true);
      setError(null);

      try {
        // In a real app, this would use the portfolio data from the context
        // For demo purposes, we'll set some mock data
        setPortfolioData({
          assets: generateMockAssets(),
          transactions: generateMockTransactions()
        });
      } catch (err) {
        setError(err.message || 'Failed to load portfolio data');
        console.error('Portfolio data loading error:', err);
      } finally {
        setLoading(false);
      }
    };

    loadPortfolioData();
  }, []);

  // Function to save portfolio changes
  const updatePortfolio = async (updatedAssets) => {
    setLoading(true);
    setError(null);

    try {
      // In a real app, this would call the savePortfolio function from the context
      // For demo purposes, we'll just update the local state
      setPortfolioData({
        ...portfolioData,
        assets: updatedAssets
      });

      return true;
    } catch (err) {
      setError(err.message || 'Failed to update portfolio');
      console.error('Portfolio update error:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading: loading || portfolioLoading,
    error,
    portfolioData,
    updatePortfolio
  };
};

// Helper functions to generate mock data
const generateMockAssets = () => {
  return [
    { name: 'Apple Inc.', symbol: 'AAPL', allocation: 15, value: '$18,679.93', performance: '+2.3%' },
    { name: 'Microsoft Corp.', symbol: 'MSFT', allocation: 12, value: '$14,943.95', performance: '+1.7%' },
    { name: 'Amazon.com Inc.', symbol: 'AMZN', allocation: 10, value: '$12,453.29', performance: '-0.8%' },
    { name: 'Tesla Inc.', symbol: 'TSLA', allocation: 8, value: '$9,962.63', performance: '+3.5%' },
    { name: 'Alphabet Inc.', symbol: 'GOOGL', allocation: 10, value: '$12,453.29', performance: '+0.5%' },
    { name: 'Bitcoin', symbol: 'BTC', allocation: 5, value: '$6,226.64', performance: '+4.2%' },
    { name: 'Ethereum', symbol: 'ETH', allocation: 5, value: '$6,226.64', performance: '+2.8%' },
    { name: 'S&P 500 ETF', symbol: 'SPY', allocation: 20, value: '$24,906.58', performance: '+1.1%' },
    { name: 'Gold ETF', symbol: 'GLD', allocation: 10, value: '$12,453.29', performance: '-0.3%' },
    { name: 'Cash', symbol: 'USD', allocation: 5, value: '$6,226.64', performance: '0.0%' }
  ];
};

const generateMockTransactions = () => {
  return [
    { date: '2025-04-05', asset: 'AAPL', type: 'Buy', amount: '$2,500.00' },
    { date: '2025-04-01', asset: 'TSLA', type: 'Sell', amount: '$1,800.00' },
    { date: '2025-03-28', asset: 'BTC', type: 'Buy', amount: '$1,000.00' },
    { date: '2025-03-15', asset: 'MSFT', type: 'Buy', amount: '$3,200.00' },
    { date: '2025-03-10', asset: 'GLD', type: 'Sell', amount: '$2,100.00' },
    { date: '2025-03-01', asset: 'SPY', type: 'Buy', amount: '$5,000.00' },
    { date: '2025-02-22', asset: 'AMZN', type: 'Buy', amount: '$2,800.00' },
    { date: '2025-02-15', asset: 'GOOGL', type: 'Sell', amount: '$1,500.00' }
  ];
};

export default usePortfolioManagement;
