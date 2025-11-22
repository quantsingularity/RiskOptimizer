import axios from 'axios';
import { Alert } from 'react-native';

// --- Data API Client (Simulated for Frontend Development) ---
// In a real application, these calls would likely go through your backend,
// which would then securely call the actual Data APIs (like YahooFinance).
// This simulation helps develop the frontend without a live backend connection.
const simulateDataApiCall = async (apiName, query) => {
    console.log(`[Simulated Data API Call] ${apiName}`, query);
    // Simulate network delay
    await new Promise((resolve) => setTimeout(resolve, 500));

    if (apiName === 'YahooFinance/get_stock_chart') {
        const { symbol, interval, range } = query;
        // Return mock data structure based on YahooFinance API docs
        // In a real scenario, your backend would fetch and return this.
        const generateMockData = (numPoints) => {
            const timestamps = [];
            const closes = [];
            const opens = [];
            const highs = [];
            const lows = [];
            const volumes = [];
            const adjCloses = [];
            let lastClose = Math.random() * 200 + 50;
            const now = Date.now();
            const timeStep = range === '1d' ? 5 * 60 * 1000 : 24 * 60 * 60 * 1000; // 5 mins for 1d, 1 day otherwise

            for (let i = 0; i < numPoints; i++) {
                timestamps.push(Math.floor((now - (numPoints - 1 - i) * timeStep) / 1000));
                const change = (Math.random() - 0.48) * (lastClose * 0.05);
                const open = lastClose;
                const close = Math.max(1, lastClose + change);
                const high = Math.max(open, close) * (1 + Math.random() * 0.02);
                const low = Math.min(open, close) * (1 - Math.random() * 0.02);
                const volume = Math.floor(Math.random() * 1000000 + 50000);

                opens.push(open);
                closes.push(close);
                highs.push(high);
                lows.push(low);
                volumes.push(volume);
                adjCloses.push(close); // Simple mock, adjClose often same as close
                lastClose = close;
            }
            return { timestamps, closes, opens, highs, lows, volumes, adjCloses };
        };

        let numPoints = 50;
        if (range === '1d') numPoints = 78; // ~ 5min intervals for a trading day
        if (range === '5d') numPoints = 5;
        if (range === '1mo') numPoints = 22;
        if (range === '6mo') numPoints = 126;
        if (range === '1y') numPoints = 252;

        const mock = generateMockData(numPoints);

        return {
            chart: {
                result: [
                    {
                        meta: {
                            currency: 'USD',
                            symbol: symbol,
                            exchangeName: 'NMS',
                            instrumentType: 'EQUITY',
                            regularMarketPrice: mock.closes[mock.closes.length - 1],
                            chartPreviousClose: mock.opens[0],
                            priceHint: 2,
                            range: range,
                            validRanges: ['1d', '5d', '1mo', '3mo', '6mo', '1y', 'ytd', 'max'],
                        },
                        timestamp: mock.timestamps,
                        indicators: {
                            quote: [
                                {
                                    open: mock.opens,
                                    high: mock.highs,
                                    low: mock.lows,
                                    close: mock.closes,
                                    volume: mock.volumes,
                                },
                            ],
                            adjclose: [
                                {
                                    adjclose: mock.adjCloses,
                                },
                            ],
                        },
                    },
                ],
                error: null,
            },
        };
    } else {
        console.error(`[Simulated Data API Call] Unknown API: ${apiName}`);
        throw new Error(`Simulated API ${apiName} not found`);
    }
};

// --- Original Axios Instance for Backend API ---
const backendApi = axios.create({
    baseURL: 'http://localhost:5000/api', // Default to local dev backend
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
    },
});

// Set environment-specific base URL (Keep this if backend exists)
const setEnvironment = (env) => {
    // ... (keep existing environment logic if needed)
};

// Set auth header (Keep this)
const setAuthHeader = (token) => {
    if (token) {
        backendApi.defaults.headers.common.Authorization = `Bearer ${token}`;
    } else {
        delete backendApi.defaults.headers.common.Authorization;
    }
};

// --- API Service Functions ---

// Authentication (Uses Backend)
const login = (email, password) => {
    return backendApi.post('/auth/login', { email, password });
};

// User Profile (Uses Backend)
const getUserProfile = () => {
    return backendApi.get('/users/profile');
};
const updateUserProfile = (profileData) => {
    return backendApi.put('/users/profile', profileData);
};

// Portfolios (Uses Backend)
const getPortfolios = () => {
    return backendApi.get('/portfolios');
};
const getPortfolioDetails = (portfolioId) => {
    return backendApi.get(`/portfolios/${portfolioId}`);
};
const createPortfolio = (portfolioData) => {
    return backendApi.post('/portfolios', portfolioData);
};
const addAssetToPortfolio = (portfolioId, assetData) => {
    return backendApi.post(`/portfolios/${portfolioId}/assets`, assetData);
};

// Optimization (Uses Backend)
const getOptimizationRecommendations = (optimizationParams) => {
    return backendApi.post('/optimization/recommendations', optimizationParams);
};

// Risk Analysis (Uses Backend)
const getRiskMetrics = (portfolioId) => {
    return backendApi.get(`/risk/metrics/${portfolioId}`);
};

// Blockchain (Uses Backend)
const getTransactionHistory = (portfolioId) => {
    return backendApi.get(`/blockchain/transactions/${portfolioId}`);
};
const verifyPortfolioIntegrity = (portfolioId) => {
    return backendApi.get(`/blockchain/verify/${portfolioId}`);
};

// Market Data (Simulated - Calls Data API via Backend in reality)
const getAssetPriceHistory = async (symbol, range = '1y', interval = '1d') => {
    // In a real app, this would call your backend: return backendApi.get(`/market/history/${symbol}?range=${range}&interval=${interval}`);
    // For frontend development, we simulate the call directly:
    try {
        const response = await simulateDataApiCall('YahooFinance/get_stock_chart', {
            symbol: symbol,
            range: range,
            interval: interval,
        });
        // Simulate the structure your backend might return (e.g., just the data part)
        if (response.chart && response.chart.result && response.chart.result.length > 0) {
            // Add a 'data' wrapper to mimic potential backend structure if needed
            return { data: response.chart.result[0] };
        } else {
            throw new Error('Invalid data structure from simulated API');
        }
    } catch (error) {
        console.error(`Error fetching simulated price history for ${symbol}:`, error);
        Alert.alert('Error', `Could not load market data for ${symbol}. Using simulated data.`);
        // Fallback to returning the raw error structure or a specific error format
        // For robustness, might return a specific error object or re-throw
        throw error; // Re-throw the error to be caught by the calling component
    }
};

// Add other market data functions as needed (e.g., search, top movers)
const searchAssets = async (query) => {
    console.log(`[Simulated API Call] Search Assets: ${query}`);
    await new Promise((resolve) => setTimeout(resolve, 300));
    // Mock search results
    const mockResults = [
        { symbol: 'AAPL', name: 'Apple Inc.' },
        { symbol: 'MSFT', name: 'Microsoft Corporation' },
        { symbol: 'GOOGL', name: 'Alphabet Inc. (Class A)' },
        { symbol: 'AMZN', name: 'Amazon.com, Inc.' },
        { symbol: 'TSLA', name: 'Tesla, Inc.' },
        { symbol: 'NVDA', name: 'NVIDIA Corporation' },
        { symbol: 'BTC-USD', name: 'Bitcoin USD' },
        { symbol: 'ETH-USD', name: 'Ethereum USD' },
    ].filter(
        (asset) =>
            asset.symbol.toLowerCase().includes(query.toLowerCase()) ||
            asset.name.toLowerCase().includes(query.toLowerCase()),
    );
    return { data: { assets: mockResults.slice(0, 10) } }; // Return max 10 results
};

// Error handling interceptor (Keep for Backend API)
backendApi.interceptors.response.use(
    (response) => response,
    (error) => {
        // ... (keep existing error handling logic)
        console.error('Backend API Error:', error.response?.data || error.message);
        return Promise.reject(error);
    },
);

export default {
    setEnvironment,
    setAuthHeader,
    // Auth
    login,
    // User
    getUserProfile,
    updateUserProfile,
    // Portfolios
    getPortfolios,
    getPortfolioDetails,
    createPortfolio,
    addAssetToPortfolio,
    // Optimization & Risk
    getOptimizationRecommendations,
    getRiskMetrics,
    // Blockchain
    getTransactionHistory,
    verifyPortfolioIntegrity,
    // Market Data (Using Simulation)
    getAssetPriceHistory,
    searchAssets,
};
