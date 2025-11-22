// code/web-frontend/__tests__/services/apiService.test.js

import apiService from '../../src/services/apiService';
import axios from 'axios';

// Mock axios
jest.mock('axios');

// Mock localStorage
const localStorageMock = (() => {
    let store = {};
    return {
        getItem: jest.fn((key) => store[key] || null),
        setItem: jest.fn((key, value) => {
            store[key] = value.toString();
        }),
        removeItem: jest.fn((key) => {
            delete store[key];
        }),
        clear: jest.fn(() => {
            store = {};
        }),
    };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('API Service', () => {
    beforeEach(() => {
        // Reset mocks before each test
        axios.get.mockReset();
        axios.post.mockReset();
        axios.put.mockReset();
        axios.delete.mockReset();
        localStorageMock.clear();
        jest.clearAllMocks();
    });

    describe('Authentication', () => {
        it('should send POST request to /api/auth/login with credentials', async () => {
            const email = 'test@example.com';
            const password = 'password123';
            const mockResponse = {
                data: { token: 'fake_token', user: { id: 1, email } },
            };

            axios.post.mockResolvedValueOnce(mockResponse);

            const result = await apiService.login(email, password);

            expect(axios.post).toHaveBeenCalledWith('/api/auth/login', {
                email,
                password,
            });
            expect(result).toEqual(mockResponse.data);
            expect(localStorageMock.setItem).toHaveBeenCalledWith('token', 'fake_token');
        });

        it('should throw an error if login request fails', async () => {
            axios.post.mockRejectedValueOnce(new Error('Invalid credentials'));

            await expect(apiService.login('wrong@example.com', 'wrong')).rejects.toThrow(
                'Invalid credentials',
            );
        });

        it('should remove token from localStorage on logout', async () => {
            await apiService.logout();

            expect(localStorageMock.removeItem).toHaveBeenCalledWith('token');
        });

        it('should check if user is authenticated', () => {
            localStorageMock.getItem.mockReturnValueOnce('fake_token');

            expect(apiService.isAuthenticated()).toBe(true);

            localStorageMock.getItem.mockReturnValueOnce(null);

            expect(apiService.isAuthenticated()).toBe(false);
        });
    });

    describe('Dashboard Data', () => {
        it('should send GET request to /api/dashboard with Authorization header', async () => {
            localStorageMock.getItem.mockReturnValue('test_token');
            const mockData = { summary: { totalValue: 10000 }, chartData: [] };
            axios.get.mockResolvedValueOnce({ data: mockData });

            const result = await apiService.getDashboardData();

            expect(axios.get).toHaveBeenCalledWith('/api/dashboard', {
                headers: {
                    Authorization: 'Bearer test_token',
                },
            });
            expect(result).toEqual(mockData);
        });

        it('should throw an error if token is missing for authenticated request', async () => {
            localStorageMock.getItem.mockReturnValueOnce(null);

            await expect(apiService.getDashboardData()).rejects.toThrow('Authentication required');
        });
    });

    describe('Portfolio Management', () => {
        beforeEach(() => {
            localStorageMock.getItem.mockReturnValue('test_token');
        });

        it('should get all portfolios', async () => {
            const mockPortfolios = [
                { id: '1', name: 'Portfolio 1' },
                { id: '2', name: 'Portfolio 2' },
            ];
            axios.get.mockResolvedValueOnce({ data: mockPortfolios });

            const result = await apiService.getPortfolios();

            expect(axios.get).toHaveBeenCalledWith('/api/portfolios', {
                headers: {
                    Authorization: 'Bearer test_token',
                },
            });
            expect(result).toEqual(mockPortfolios);
        });

        it('should get a specific portfolio by ID', async () => {
            const portfolioId = '123';
            const mockPortfolio = {
                id: portfolioId,
                name: 'Test Portfolio',
                assets: [],
            };
            axios.get.mockResolvedValueOnce({ data: mockPortfolio });

            const result = await apiService.getPortfolio(portfolioId);

            expect(axios.get).toHaveBeenCalledWith(`/api/portfolios/${portfolioId}`, {
                headers: {
                    Authorization: 'Bearer test_token',
                },
            });
            expect(result).toEqual(mockPortfolio);
        });

        it('should create a new portfolio', async () => {
            const portfolioData = {
                name: 'New Portfolio',
                description: 'Test description',
            };
            const mockResponse = {
                id: 'new-id',
                ...portfolioData,
                createdAt: new Date().toISOString(),
            };
            axios.post.mockResolvedValueOnce({ data: mockResponse });

            const result = await apiService.createPortfolio(portfolioData);

            expect(axios.post).toHaveBeenCalledWith('/api/portfolios', portfolioData, {
                headers: {
                    Authorization: 'Bearer test_token',
                },
            });
            expect(result).toEqual(mockResponse);
        });

        it('should update an existing portfolio', async () => {
            const portfolioId = '123';
            const updateData = { name: 'Updated Portfolio' };
            const mockResponse = {
                id: portfolioId,
                ...updateData,
                updatedAt: new Date().toISOString(),
            };
            axios.put.mockResolvedValueOnce({ data: mockResponse });

            const result = await apiService.updatePortfolio(portfolioId, updateData);

            expect(axios.put).toHaveBeenCalledWith(`/api/portfolios/${portfolioId}`, updateData, {
                headers: {
                    Authorization: 'Bearer test_token',
                },
            });
            expect(result).toEqual(mockResponse);
        });

        it('should delete a portfolio', async () => {
            const portfolioId = '123';
            axios.delete.mockResolvedValueOnce({ data: { success: true } });

            const result = await apiService.deletePortfolio(portfolioId);

            expect(axios.delete).toHaveBeenCalledWith(`/api/portfolios/${portfolioId}`, {
                headers: {
                    Authorization: 'Bearer test_token',
                },
            });
            expect(result).toEqual({ success: true });
        });
    });

    describe('Optimization', () => {
        beforeEach(() => {
            localStorageMock.getItem.mockReturnValue('test_token');
        });

        it('should run optimization for a portfolio', async () => {
            const portfolioId = '123';
            const params = { riskLevel: 'high', targetReturn: 0.1 };
            const mockResponse = {
                success: true,
                results: {
                    weights: {
                        AAPL: 0.4,
                        MSFT: 0.3,
                        GOOGL: 0.3,
                    },
                    expectedReturn: 0.12,
                    expectedRisk: 0.08,
                    sharpeRatio: 1.5,
                },
            };
            axios.post.mockResolvedValueOnce({ data: mockResponse });

            const result = await apiService.runOptimization(portfolioId, params);

            expect(axios.post).toHaveBeenCalledWith(
                `/api/optimize/portfolio/${portfolioId}`,
                params,
                {
                    headers: {
                        Authorization: 'Bearer test_token',
                    },
                },
            );
            expect(result).toEqual(mockResponse);
        });

        it('should get risk metrics for a portfolio', async () => {
            const portfolioId = '123';
            const mockResponse = {
                sharpeRatio: 1.2,
                volatility: 0.15,
                maxDrawdown: -0.1,
                beta: 0.9,
            };
            axios.get.mockResolvedValueOnce({ data: mockResponse });

            const result = await apiService.getRiskMetrics(portfolioId);

            expect(axios.get).toHaveBeenCalledWith(`/api/risk/metrics/${portfolioId}`, {
                headers: {
                    Authorization: 'Bearer test_token',
                },
            });
            expect(result).toEqual(mockResponse);
        });
    });

    describe('Market Data', () => {
        beforeEach(() => {
            localStorageMock.getItem.mockReturnValue('test_token');
        });

        it('should get asset price history', async () => {
            const symbol = 'AAPL';
            const range = '1y';
            const interval = '1d';
            const mockResponse = {
                prices: [100, 102, 105, 103, 106],
                timestamps: [1620000000, 1620086400, 1620172800, 1620259200, 1620345600],
            };
            axios.get.mockResolvedValueOnce({ data: mockResponse });

            const result = await apiService.getAssetPriceHistory(symbol, range, interval);

            expect(axios.get).toHaveBeenCalledWith(`/api/market/history/${symbol}`, {
                params: { range, interval },
                headers: {
                    Authorization: 'Bearer test_token',
                },
            });
            expect(result).toEqual(mockResponse);
        });

        it('should search for assets', async () => {
            const query = 'apple';
            const mockResponse = {
                assets: [
                    { symbol: 'AAPL', name: 'Apple Inc.' },
                    { symbol: 'AAPL.L', name: 'Apple Inc. (London)' },
                ],
            };
            axios.get.mockResolvedValueOnce({ data: mockResponse });

            const result = await apiService.searchAssets(query);

            expect(axios.get).toHaveBeenCalledWith('/api/market/search', {
                params: { query },
                headers: {
                    Authorization: 'Bearer test_token',
                },
            });
            expect(result).toEqual(mockResponse);
        });
    });

    describe('Error Handling', () => {
        beforeEach(() => {
            localStorageMock.getItem.mockReturnValue('test_token');
            console.error = jest.fn(); // Mock console.error to prevent test output noise
        });

        it('should handle network errors', async () => {
            axios.get.mockRejectedValueOnce(new Error('Network Error'));

            await expect(apiService.getPortfolios()).rejects.toThrow('Network Error');
            expect(console.error).toHaveBeenCalled();
        });

        it('should handle API errors with error messages', async () => {
            const errorResponse = {
                response: {
                    data: { message: 'Resource not found' },
                    status: 404,
                },
            };
            axios.get.mockRejectedValueOnce(errorResponse);

            await expect(apiService.getPortfolio('999')).rejects.toThrow('Resource not found');
            expect(console.error).toHaveBeenCalled();
        });

        it('should handle unexpected API errors', async () => {
            const errorResponse = {
                response: {
                    status: 500,
                },
            };
            axios.post.mockRejectedValueOnce(errorResponse);

            await expect(apiService.createPortfolio({ name: 'Test' })).rejects.toThrow(
                'Server error (500)',
            );
            expect(console.error).toHaveBeenCalled();
        });
    });
});
