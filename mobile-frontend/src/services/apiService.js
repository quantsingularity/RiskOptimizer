import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: 'https://api.riskoptimizer.com/api', // Default to production
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Set environment-specific base URL
// In a real app, this would be configured via environment variables
const setEnvironment = (env) => {
  switch (env) {
    case 'development':
      api.defaults.baseURL = 'http://localhost:5000/api';
      break;
    case 'staging':
      api.defaults.baseURL = 'https://staging-api.riskoptimizer.com/api';
      break;
    case 'production':
      api.defaults.baseURL = 'https://api.riskoptimizer.com/api';
      break;
    default:
      api.defaults.baseURL = 'https://api.riskoptimizer.com/api';
  }
};

// Set auth header
const setAuthHeader = (token) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

// Authentication endpoints
const login = (email, password) => {
  return api.post('/auth/login', { email, password });
};

// User endpoints
const getUserProfile = () => {
  return api.get('/users/profile');
};

const updateUserProfile = (profileData) => {
  return api.put('/users/profile', profileData);
};

// Portfolio endpoints
const getPortfolios = () => {
  return api.get('/portfolios');
};

const getPortfolioDetails = (portfolioId) => {
  return api.get(`/portfolios/${portfolioId}`);
};

const createPortfolio = (portfolioData) => {
  return api.post('/portfolios', portfolioData);
};

const addAssetToPortfolio = (portfolioId, assetData) => {
  return api.post(`/portfolios/${portfolioId}/assets`, assetData);
};

// Optimization endpoints
const getOptimizationRecommendations = (optimizationParams) => {
  return api.post('/optimization/recommendations', optimizationParams);
};

// Risk analysis endpoints
const getRiskMetrics = (portfolioId) => {
  return api.get(`/risk/metrics/${portfolioId}`);
};

// Blockchain integration endpoints
const getTransactionHistory = (portfolioId) => {
  return api.get(`/blockchain/transactions/${portfolioId}`);
};

const verifyPortfolioIntegrity = (portfolioId) => {
  return api.get(`/blockchain/verify/${portfolioId}`);
};

// Market data endpoints
const getAssetPriceHistory = (symbol, period = '1y', interval = '1d') => {
  return api.get(`/market/history/${symbol}?period=${period}&interval=${interval}`);
};

// Error handling interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle specific error cases
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.data);
      
      // Handle 401 Unauthorized - could trigger token refresh or logout
      if (error.response.status === 401) {
        // TODO: Implement token refresh or logout logic
      }
    } else if (error.request) {
      // Request made but no response received
      console.error('Network Error:', error.request);
    } else {
      // Error in setting up the request
      console.error('Request Error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export default {
  setEnvironment,
  setAuthHeader,
  login,
  getUserProfile,
  updateUserProfile,
  getPortfolios,
  getPortfolioDetails,
  createPortfolio,
  addAssetToPortfolio,
  getOptimizationRecommendations,
  getRiskMetrics,
  getTransactionHistory,
  verifyPortfolioIntegrity,
  getAssetPriceHistory,
};
