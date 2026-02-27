import axios from "axios";

// Create an axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:5000",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000, // 30 seconds for longer operations
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const user = localStorage.getItem("user");
    if (user) {
      try {
        const userData = JSON.parse(user);
        if (userData.token) {
          config.headers.Authorization = `Bearer ${userData.token}`;
        }
      } catch (error) {
        console.error("Error parsing user data:", error);
      }
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      const message =
        error.response.data?.error?.message ||
        error.response.data?.message ||
        "An error occurred";
      console.error("API Error:", message);
      return Promise.reject(new Error(message));
    } else if (error.request) {
      // Request made but no response
      console.error("Network Error:", error.message);
      return Promise.reject(
        new Error("Network error. Please check your connection."),
      );
    } else {
      // Something else happened
      console.error("Error:", error.message);
      return Promise.reject(error);
    }
  },
);

// API endpoints
const endpoints = {
  // Auth endpoints
  login: "/api/v1/auth/login",
  register: "/api/v1/auth/register",
  logout: "/api/v1/auth/logout",
  refreshToken: "/api/v1/auth/refresh",

  // Portfolio endpoints
  getPortfolio: (address) => `/api/v1/portfolios/address/${address}`,
  getAllPortfolios: "/api/v1/portfolios",
  createPortfolio: "/api/v1/portfolios",
  updatePortfolio: (id) => `/api/v1/portfolios/${id}`,
  deletePortfolio: (id) => `/api/v1/portfolios/${id}`,

  // Risk analysis endpoints
  calculateVaR: "/api/v1/risk/var",
  stressTest: "/api/v1/risk/stress-test",
  correlationAnalysis: "/api/v1/risk/correlation",
  riskMetrics: "/api/v1/risk/metrics",

  // Optimization endpoints
  optimizePortfolio: "/api/v1/optimization/optimize",
  efficientFrontier: "/api/v1/optimization/efficient-frontier",
  constraints: "/api/v1/optimization/constraints",

  // Market data endpoints
  marketData: "/api/v1/market/data",
  historicalPrices: "/api/v1/market/historical",
  realtimePrice: "/api/v1/market/realtime",
};

// API service functions
const apiService = {
  // Health check
  healthCheck: async () => {
    try {
      const response = await api.get("/health");
      return response.data;
    } catch (error) {
      console.error("Health check failed:", error);
      throw error;
    }
  },

  // Auth services
  auth: {
    login: async (credentials) => {
      try {
        const response = await api.post(endpoints.login, credentials);
        return response.data;
      } catch (error) {
        console.error("Login error:", error);
        throw error;
      }
    },

    register: async (userData) => {
      try {
        const response = await api.post(endpoints.register, userData);
        return response.data;
      } catch (error) {
        console.error("Registration error:", error);
        throw error;
      }
    },

    logout: async () => {
      try {
        const response = await api.post(endpoints.logout);
        return response.data;
      } catch (error) {
        console.error("Logout error:", error);
        throw error;
      }
    },
  },

  // Portfolio services
  portfolio: {
    getByAddress: async (address) => {
      try {
        const response = await api.get(endpoints.getPortfolio(address));
        return response.data;
      } catch (error) {
        console.error("Error fetching portfolio:", error);
        throw error;
      }
    },

    getAll: async (params = {}) => {
      try {
        const response = await api.get(endpoints.getAllPortfolios, { params });
        return response.data;
      } catch (error) {
        console.error("Error fetching portfolios:", error);
        throw error;
      }
    },

    create: async (portfolioData) => {
      try {
        const response = await api.post(
          endpoints.createPortfolio,
          portfolioData,
        );
        return response.data;
      } catch (error) {
        console.error("Error creating portfolio:", error);
        throw error;
      }
    },

    update: async (id, portfolioData) => {
      try {
        const response = await api.put(
          endpoints.updatePortfolio(id),
          portfolioData,
        );
        return response.data;
      } catch (error) {
        console.error("Error updating portfolio:", error);
        throw error;
      }
    },

    delete: async (id) => {
      try {
        const response = await api.delete(endpoints.deletePortfolio(id));
        return response.data;
      } catch (error) {
        console.error("Error deleting portfolio:", error);
        throw error;
      }
    },
  },

  // Risk analysis services
  risk: {
    calculateVaR: async (params) => {
      try {
        const response = await api.post(endpoints.calculateVaR, params);
        return response.data;
      } catch (error) {
        console.error("Error calculating VaR:", error);
        throw error;
      }
    },

    stressTest: async (params) => {
      try {
        const response = await api.post(endpoints.stressTest, params);
        return response.data;
      } catch (error) {
        console.error("Error running stress test:", error);
        throw error;
      }
    },

    correlationAnalysis: async (params) => {
      try {
        const response = await api.post(endpoints.correlationAnalysis, params);
        return response.data;
      } catch (error) {
        console.error("Error analyzing correlation:", error);
        throw error;
      }
    },

    getMetrics: async (portfolioId) => {
      try {
        const response = await api.get(endpoints.riskMetrics, {
          params: { portfolio_id: portfolioId },
        });
        return response.data;
      } catch (error) {
        console.error("Error fetching risk metrics:", error);
        throw error;
      }
    },
  },

  // Optimization services
  optimization: {
    optimize: async (params) => {
      try {
        const response = await api.post(endpoints.optimizePortfolio, params);
        return response.data;
      } catch (error) {
        console.error("Error optimizing portfolio:", error);
        throw error;
      }
    },

    efficientFrontier: async (params) => {
      try {
        const response = await api.post(endpoints.efficientFrontier, params);
        return response.data;
      } catch (error) {
        console.error("Error calculating efficient frontier:", error);
        throw error;
      }
    },

    getConstraints: async () => {
      try {
        const response = await api.get(endpoints.constraints);
        return response.data;
      } catch (error) {
        console.error("Error fetching constraints:", error);
        throw error;
      }
    },
  },

  // Market data services
  market: {
    getData: async (symbols, params = {}) => {
      try {
        const response = await api.get(endpoints.marketData, {
          params: { symbols: symbols.join(","), ...params },
        });
        return response.data;
      } catch (error) {
        console.error("Error fetching market data:", error);
        throw error;
      }
    },

    getHistoricalPrices: async (symbol, startDate, endDate) => {
      try {
        const response = await api.get(endpoints.historicalPrices, {
          params: { symbol, start_date: startDate, end_date: endDate },
        });
        return response.data;
      } catch (error) {
        console.error("Error fetching historical prices:", error);
        throw error;
      }
    },

    getRealtimePrice: async (symbol) => {
      try {
        const response = await api.get(endpoints.realtimePrice, {
          params: { symbol },
        });
        return response.data;
      } catch (error) {
        console.error("Error fetching realtime price:", error);
        throw error;
      }
    },
  },
};

export default apiService;
