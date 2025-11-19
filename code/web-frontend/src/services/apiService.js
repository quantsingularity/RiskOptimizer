import axios from 'axios';

// Create an axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// API endpoints
const endpoints = {
  // Portfolio endpoints
  getPortfolio: (address) => `/api/portfolio/${address}`,
  getPortfolioFromDb: (address) => `/api/portfolio/db/${address}`,
  savePortfolio: '/api/portfolio/save',

  // Optimization endpoints
  optimizePortfolio: '/api/optimize',

  // Risk analysis endpoints
  calculateVaR: '/api/risk/var',
};

// API service functions
const apiService = {
  // Portfolio services
  getPortfolio: async (address) => {
    try {
      const response = await api.get(endpoints.getPortfolio(address));
      return response.data;
    } catch (error) {
      console.error('Error fetching portfolio:', error);
      throw error;
    }
  },

  getPortfolioFromDb: async (address) => {
    try {
      const response = await api.get(endpoints.getPortfolioFromDb(address));
      return response.data;
    } catch (error) {
      console.error('Error fetching portfolio from database:', error);
      throw error;
    }
  },

  savePortfolio: async (portfolioData) => {
    try {
      const response = await api.post(endpoints.savePortfolio, portfolioData);
      return response.data;
    } catch (error) {
      console.error('Error saving portfolio:', error);
      throw error;
    }
  },

  // Optimization services
  optimizePortfolio: async (historicalData, parameters = {}) => {
    try {
      const response = await api.post(endpoints.optimizePortfolio, {
        historical_data: historicalData,
        parameters,
      });
      return response.data;
    } catch (error) {
      console.error('Error optimizing portfolio:', error);
      throw error;
    }
  },

  // Risk analysis services
  calculateVaR: async (returns, confidence = 0.95) => {
    try {
      const response = await api.post(endpoints.calculateVaR, {
        returns,
        confidence,
      });
      return response.data;
    } catch (error) {
      console.error('Error calculating VaR:', error);
      throw error;
    }
  },
};

export default apiService;
