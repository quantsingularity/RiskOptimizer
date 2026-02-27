import { describe, it, expect, beforeEach, vi } from "vitest";
import axios from "axios";
import apiService from "../../src/services/apiService";

// Mock axios
vi.mock("axios");

describe("API Service", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe("Health Check", () => {
    it("should successfully check API health", async () => {
      const mockResponse = {
        data: {
          status: "ok",
          version: "1.0.0",
        },
      };

      axios.create.mockReturnValue({
        get: vi.fn().mockResolvedValue(mockResponse),
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() },
        },
      });

      const result = await apiService.healthCheck();
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe("Portfolio Services", () => {
    const mockPortfolio = {
      status: "success",
      data: {
        id: "1",
        total_value: "100000",
        assets: [],
      },
    };

    it("should fetch portfolio by address", async () => {
      const mockApi = {
        get: vi.fn().mockResolvedValue({ data: mockPortfolio }),
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() },
        },
      };

      axios.create.mockReturnValue(mockApi);

      const result = await apiService.portfolio.getByAddress("0x123");
      expect(result).toEqual(mockPortfolio);
      expect(mockApi.get).toHaveBeenCalledWith(
        "/api/v1/portfolios/address/0x123",
      );
    });

    it("should create new portfolio", async () => {
      const newPortfolio = {
        address: "0x123",
        assets: [],
      };

      const mockApi = {
        post: vi.fn().mockResolvedValue({ data: mockPortfolio }),
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() },
        },
      };

      axios.create.mockReturnValue(mockApi);

      const result = await apiService.portfolio.create(newPortfolio);
      expect(result).toEqual(mockPortfolio);
    });
  });

  describe("Risk Analysis Services", () => {
    it("should calculate VaR", async () => {
      const mockVaRData = {
        status: "success",
        data: {
          var_95: 4532.12,
          var_99: 6254.89,
        },
      };

      const mockApi = {
        post: vi.fn().mockResolvedValue({ data: mockVaRData }),
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() },
        },
      };

      axios.create.mockReturnValue(mockApi);

      const params = {
        returns: [0.01, 0.02, -0.01],
        confidence: 0.95,
      };

      const result = await apiService.risk.calculateVaR(params);
      expect(result).toEqual(mockVaRData);
    });

    it("should run stress test", async () => {
      const mockStressTest = {
        status: "success",
        data: {
          scenario: "2008_crisis",
          loss: -32.8,
        },
      };

      const mockApi = {
        post: vi.fn().mockResolvedValue({ data: mockStressTest }),
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() },
        },
      };

      axios.create.mockReturnValue(mockApi);

      const params = {
        scenario: "2008_crisis",
        portfolio_id: "1",
      };

      const result = await apiService.risk.stressTest(params);
      expect(result).toEqual(mockStressTest);
    });
  });

  describe("Optimization Services", () => {
    it("should optimize portfolio", async () => {
      const mockOptimization = {
        status: "success",
        data: {
          expected_return: 12.4,
          expected_risk: 9.8,
          sharpe_ratio: 1.87,
        },
      };

      const mockApi = {
        post: vi.fn().mockResolvedValue({ data: mockOptimization }),
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() },
        },
      };

      axios.create.mockReturnValue(mockApi);

      const params = {
        assets: ["AAPL", "GOOGL", "MSFT"],
        method: "sharpe",
      };

      const result = await apiService.optimization.optimize(params);
      expect(result).toEqual(mockOptimization);
    });
  });

  describe("Error Handling", () => {
    it("should handle network errors", async () => {
      const mockApi = {
        get: vi.fn().mockRejectedValue(new Error("Network error")),
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() },
        },
      };

      axios.create.mockReturnValue(mockApi);

      await expect(apiService.healthCheck()).rejects.toThrow("Network error");
    });

    it("should handle API errors", async () => {
      const mockError = {
        response: {
          data: {
            error: {
              message: "Invalid parameters",
            },
          },
        },
      };

      const mockApi = {
        post: vi.fn().mockRejectedValue(mockError),
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() },
        },
      };

      axios.create.mockReturnValue(mockApi);

      await expect(apiService.risk.calculateVaR({})).rejects.toThrow();
    });
  });
});
