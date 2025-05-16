// mobile-frontend/__tests__/screens/CreatePortfolioScreen.test.js

import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react-native";
import CreatePortfolioScreen from "../../src/screens/Portfolios/CreatePortfolioScreen";
import apiService from "../../src/services/apiService";

// Mock the apiService
jest.mock("../../src/services/apiService", () => ({
  createPortfolio: jest.fn()
}));

// Mock the navigation
const mockGoBack = jest.fn();
const mockNavigation = { 
  goBack: mockGoBack,
  setOptions: jest.fn()
};

// Mock the components used in CreatePortfolioScreen
jest.mock("@rneui/themed", () => {
  const React = require("react");
  return {
    ...jest.requireActual("@rneui/themed"),
    Input: ({ placeholder, leftIcon, onChangeText, value, multiline, containerStyle, disabled, testID }) => (
      <React.Fragment>
        <input
          placeholder={placeholder}
          onChange={(e) => onChangeText(e.target.value)}
          value={value}
          multiline={multiline}
          disabled={disabled}
          data-testid={testID || `input-${placeholder}`}
        />
      </React.Fragment>
    ),
    Button: ({ title, onPress, buttonStyle, disabled, testID }) => (
      <button onClick={onPress} disabled={disabled} data-testid={testID || "button"}>
        {title}
      </button>
    ),
    Text: ({ style, children }) => <span style={style}>{children}</span>,
    Card: {
      ...React.forwardRef(({ containerStyle, children }, ref) => (
        <div ref={ref} style={containerStyle} data-testid="card">
          {children}
        </div>
      ))
    }
  };
});

describe("Create Portfolio Screen", () => {
  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
    
    // Setup default mock response
    apiService.createPortfolio.mockResolvedValue({
      data: {
        id: "new-portfolio-id",
        name: "Test Portfolio",
        description: "Test Description",
        createdAt: new Date().toISOString()
      }
    });
  });

  const renderCreateScreen = () => {
    return render(<CreatePortfolioScreen navigation={mockNavigation} />);
  };

  it("should render name and description inputs and create button", () => {
    renderCreateScreen();
    expect(screen.getByTestId("input-Portfolio Name")).toBeTruthy();
    expect(screen.getByTestId("input-Description (Optional)")).toBeTruthy();
    expect(screen.getByTestId("button")).toBeTruthy();
  });

  it("should update input fields when user types", () => {
    renderCreateScreen();
    const nameInput = screen.getByTestId("input-Portfolio Name");
    const descriptionInput = screen.getByTestId("input-Description (Optional)");

    fireEvent.change(nameInput, { target: { value: "My New Portfolio" } });
    fireEvent.change(descriptionInput, { target: { value: "Focus on tech stocks" } });

    expect(nameInput.value).toBe("My New Portfolio");
    expect(descriptionInput.value).toBe("Focus on tech stocks");
  });

  it("should call createPortfolio function and goBack on successful creation", async () => {
    renderCreateScreen();
    const nameInput = screen.getByTestId("input-Portfolio Name");
    const descriptionInput = screen.getByTestId("input-Description (Optional)");
    const createButton = screen.getByTestId("button");

    fireEvent.change(nameInput, { target: { value: "Success Portfolio" } });
    fireEvent.change(descriptionInput, { target: { value: "Description" } });
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(apiService.createPortfolio).toHaveBeenCalledWith({
        name: "Success Portfolio",
        description: "Description"
      });
      expect(apiService.createPortfolio).toHaveBeenCalledTimes(1);
      expect(mockGoBack).toHaveBeenCalledTimes(1);
    });
  });

  it("should display error message if name is missing", async () => {
    renderCreateScreen();
    const createButton = screen.getByTestId("button");

    fireEvent.click(createButton);

    await waitFor(() => {
      expect(screen.getByText("Portfolio name is required")).toBeTruthy();
    });
    expect(apiService.createPortfolio).not.toHaveBeenCalled();
    expect(mockGoBack).not.toHaveBeenCalled();
  });

  it("should display error message if creation fails", async () => {
    apiService.createPortfolio.mockRejectedValueOnce(new Error("API Error"));
    
    renderCreateScreen();
    const nameInput = screen.getByTestId("input-Portfolio Name");
    const createButton = screen.getByTestId("button");

    fireEvent.change(nameInput, { target: { value: "Fail Portfolio" } });
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(screen.getByText("Failed to create portfolio")).toBeTruthy();
    });
    expect(mockGoBack).not.toHaveBeenCalled();
  });
});

