import React, { createContext, useContext, useState, useEffect } from "react";
import apiService from "../services/apiService";

// Create context
const PortfolioContext = createContext();

// Provider component
export const PortfolioProvider = ({ children }) => {
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch portfolio data
  const fetchPortfolio = async (address) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiService.getPortfolio(address);
      if (response.status === "success") {
        setPortfolio(response.portfolio);
      } else {
        setError(response.message || "Failed to fetch portfolio");
      }
    } catch (err) {
      setError(err.message || "An error occurred while fetching portfolio");
      console.error("Portfolio fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  // Save portfolio data
  const savePortfolio = async (portfolioData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiService.savePortfolio(portfolioData);
      if (response.status === "success") {
        setPortfolio(portfolioData);
        return true;
      } else {
        setError(response.message || "Failed to save portfolio");
        return false;
      }
    } catch (err) {
      setError(err.message || "An error occurred while saving portfolio");
      console.error("Portfolio save error:", err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Optimize portfolio
  const optimizePortfolio = async (historicalData, parameters) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiService.optimizePortfolio(
        historicalData,
        parameters,
      );
      if (response.status === "success") {
        return response;
      } else {
        setError(response.message || "Failed to optimize portfolio");
        return null;
      }
    } catch (err) {
      setError(err.message || "An error occurred while optimizing portfolio");
      console.error("Portfolio optimization error:", err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Context value
  const value = {
    portfolio,
    loading,
    error,
    fetchPortfolio,
    savePortfolio,
    optimizePortfolio,
  };

  return (
    <PortfolioContext.Provider value={value}>
      {children}
    </PortfolioContext.Provider>
  );
};

// Custom hook to use the portfolio context
export const usePortfolio = () => {
  const context = useContext(PortfolioContext);
  if (context === undefined) {
    throw new Error("usePortfolio must be used within a PortfolioProvider");
  }
  return context;
};

export default PortfolioContext;
