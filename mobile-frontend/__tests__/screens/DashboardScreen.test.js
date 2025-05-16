// mobile-frontend/__tests__/screens/DashboardScreen.test.js

import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react-native";
import DashboardScreen from "../../src/screens/Dashboard/DashboardScreen";
import apiService from "../../src/services/apiService";

// Mock the apiService
jest.mock("../../src/services/apiService", () => ({
  getPortfolios: jest.fn(),
  getRiskMetrics: jest.fn(),
  getAssetPriceHistory: jest.fn()
}));

// Mock the useNavigation hook
jest.mock("@react-navigation/native", () => {
  return {
    ...jest.requireActual("@react-navigation/native"),
    useNavigation: () => ({
      navigate: jest.fn()
    })
  };
});

// Mock the components used in DashboardScreen
jest.mock("@rneui/themed", () => {
  const React = require("react");
  return {
    ...jest.requireActual("@rneui/themed"),
    Card: {
      ...React.forwardRef(({ children, containerStyle }, ref) => (
        <div ref={ref} style={containerStyle} data-testid="card">
          {children}
        </div>
      )),
      Title: ({ children }) => <h3 data-testid="card-title">{children}</h3>,
      Divider: () => <hr />,
    },
    Button: ({ title, onPress, icon, type, testID }) => (
      <button onClick={onPress} data-testid={testID || "button"}>
        {title}
      </button>
    ),
    Icon: ({ name, type, color, size }) => (
      <span data-testid={`icon-${name}`}>Icon</span>
    ),
    Text: ({ style, children }) => <span style={style}>{children}</span>,
    ListItem: {
      ...React.forwardRef(({ children, onPress }, ref) => (
        <div ref={ref} onClick={onPress} data-testid="list-item">
          {children}
        </div>
      )),
      Content: ({ children }) => <div data-testid="list-item-content">{children}</div>,
      Title: ({ children }) => <div data-testid="list-item-title">{children}</div>,
      Subtitle: ({ children }) => <div data-testid="list-item-subtitle">{children}</div>,
      Chevron: () => <span data-testid="list-item-chevron">></span>,
    }
  };
});

// Mock the chart component
jest.mock("react-native-chart-kit", () => ({
  LineChart: () => <div data-testid="line-chart">Chart</div>
}));

describe("Dashboard Screen", () => {
  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
    
    // Setup default mock responses
    apiService.getPortfolios.mockResolvedValue({
      data: [
        {
          id: "1",
          name: "Test Portfolio",
          totalValue: 10000,
          dailyChange: 2.5,
          assets: [
            { symbol: "AAPL", allocation: 0.4, value: 4000 },
            { symbol: "MSFT", allocation: 0.3, value: 3000 },
            { symbol: "GOOGL", allocation: 0.3, value: 3000 }
          ]
        }
      ]
    });
    
    apiService.getRiskMetrics.mockResolvedValue({
      data: {
        sharpeRatio: 1.2,
        volatility: 0.15,
        maxDrawdown: -0.1,
        beta: 0.9
      }
    });
    
    apiService.getAssetPriceHistory.mockResolvedValue({
      data: {
        indicators: {
          quote: [{
            close: [100, 102, 105, 103, 106]
          }]
        },
        timestamp: [1620000000, 1620086400, 1620172800, 1620259200, 1620345600]
      }
    });
  });

  const renderDashboardScreen = () => {
    return render(<DashboardScreen />);
  };

  it("should display loading indicator initially", () => {
    renderDashboardScreen();
    expect(screen.getByTestId("loading-indicator")).toBeTruthy();
  });

  it("should fetch portfolio data on mount", async () => {
    renderDashboardScreen();
    await waitFor(() => {
      expect(apiService.getPortfolios).toHaveBeenCalledTimes(1);
    });
  });

  it("should display portfolio summary after successful data load", async () => {
    renderDashboardScreen();
    
    await waitFor(() => {
      expect(screen.queryByTestId("loading-indicator")).toBeNull();
    });
    
    expect(screen.getByText("Test Portfolio")).toBeTruthy();
    expect(screen.getByText("$10,000.00")).toBeTruthy();
    expect(screen.getByText("+2.5%")).toBeTruthy();
  });

  it("should display risk metrics after successful data load", async () => {
    renderDashboardScreen();
    
    await waitFor(() => {
      expect(screen.queryByTestId("loading-indicator")).toBeNull();
    });
    
    expect(screen.getByText("Sharpe Ratio: 1.2")).toBeTruthy();
    expect(screen.getByText("Volatility: 15%")).toBeTruthy();
    expect(screen.getByText("Max Drawdown: -10%")).toBeTruthy();
    expect(screen.getByText("Beta: 0.9")).toBeTruthy();
  });

  it("should display performance chart after successful data load", async () => {
    renderDashboardScreen();
    
    await waitFor(() => {
      expect(screen.queryByTestId("loading-indicator")).toBeNull();
    });
    
    expect(screen.getByTestId("line-chart")).toBeTruthy();
  });

  it("should display error message if data loading fails", async () => {
    // Mock API to throw error
    apiService.getPortfolios.mockRejectedValueOnce(new Error("API Error"));
    
    renderDashboardScreen();
    
    await waitFor(() => {
      expect(screen.queryByTestId("loading-indicator")).toBeNull();
    });
    
    expect(screen.getByText("Failed to load dashboard data")).toBeTruthy();
  });

  it("should navigate to portfolio details when portfolio card is pressed", async () => {
    const { navigate } = require("@react-navigation/native").useNavigation();
    
    renderDashboardScreen();
    
    await waitFor(() => {
      expect(screen.queryByTestId("loading-indicator")).toBeNull();
    });
    
    fireEvent.click(screen.getByTestId("card"));
    
    expect(navigate).toHaveBeenCalledWith("PortfolioDetail", { portfolioId: "1" });
  });
});

