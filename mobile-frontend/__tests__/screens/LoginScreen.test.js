// mobile-frontend/__tests__/screens/LoginScreen.test.js

import React from "react";
import { render, fireEvent, waitFor, screen } from "@testing-library/react-native";
import LoginScreen from "../../src/screens/Auth/LoginScreen";
import { AuthProvider, AuthContext } from "../../src/context/AuthContext";

// Mock navigation
const mockNavigate = jest.fn();
const mockNavigation = { navigate: mockNavigate };

// Mock the useAuth hook
jest.mock("../../src/context/AuthContext", () => {
  const originalModule = jest.requireActual("../../src/context/AuthContext");
  return {
    ...originalModule,
    useAuth: () => ({
      login: mockLogin,
      loading: false,
      authenticated: false,
      user: null
    })
  };
});

// Mock the apiService
jest.mock("../../src/services/apiService", () => ({
  login: jest.fn(),
  getUserProfile: jest.fn(),
  setAuthHeader: jest.fn()
}));

// Mock SecureStore
jest.mock("expo-secure-store", () => ({
  setItemAsync: jest.fn(() => Promise.resolve()),
  getItemAsync: jest.fn(() => Promise.resolve(null)),
  deleteItemAsync: jest.fn(() => Promise.resolve())
}));

// Mock context login function
const mockLogin = jest.fn();

// Mock theme
jest.mock("@rneui/themed", () => {
  const React = require("react");
  const originalModule = jest.requireActual("@rneui/themed");

  return {
    ...originalModule,
    useTheme: () => ({
      theme: {
        colors: {
          primary: "#007AFF",
          background: "#FFFFFF",
          error: "#FF3B30",
          grey0: "#000000"
        }
      }
    }),
    Input: ({ placeholder, leftIcon, onChangeText, value, secureTextEntry, containerStyle, disabled, testID }) => (
      <React.Fragment>
        <input
          placeholder={placeholder}
          onChange={(e) => onChangeText(e.target.value)}
          value={value}
          type={secureTextEntry ? "password" : "text"}
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
      Title: ({ h3, style, children }) => <h3 style={style}>{children}</h3>,
      Divider: () => <hr />,
      ...React.forwardRef(({ containerStyle, children }, ref) => (
        <div ref={ref} style={containerStyle}>
          {children}
        </div>
      ))
    }
  };
});

describe("Login Screen", () => {
  beforeEach(() => {
    mockLogin.mockClear();
    mockNavigate.mockClear();
    mockLogin.mockResolvedValue(true); // Default to successful login
  });

  const renderLoginScreen = () => {
    return render(<LoginScreen navigation={mockNavigation} />);
  };

  it("should render email and password inputs and login button", () => {
    renderLoginScreen();
    expect(screen.getByTestId("input-Email")).toBeTruthy();
    expect(screen.getByTestId("input-Password")).toBeTruthy();
    expect(screen.getByTestId("button")).toBeTruthy();
  });

  it("should update input fields when user types", () => {
    renderLoginScreen();
    const emailInput = screen.getByTestId("input-Email");
    const passwordInput = screen.getByTestId("input-Password");

    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "password123" } });

    expect(emailInput.value).toBe("test@example.com");
    expect(passwordInput.value).toBe("password123");
  });

  it("should call login function on button press with credentials", async () => {
    renderLoginScreen();
    const emailInput = screen.getByTestId("input-Email");
    const passwordInput = screen.getByTestId("input-Password");
    const loginButton = screen.getByTestId("button");

    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "password123" } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith("test@example.com", "password123");
      expect(mockLogin).toHaveBeenCalledTimes(1);
    });
  });

  it("should display error message on failed login", async () => {
    mockLogin.mockResolvedValue(false); // Simulate failed login

    renderLoginScreen();
    const emailInput = screen.getByTestId("input-Email");
    const passwordInput = screen.getByTestId("input-Password");
    const loginButton = screen.getByTestId("button");

    fireEvent.change(emailInput, { target: { value: "wrong@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "wrong" } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByText("Login failed. Please check your credentials.")).toBeTruthy();
    });
  });

  it("should validate input fields before submission", async () => {
    renderLoginScreen();
    const loginButton = screen.getByTestId("button");

    // Try to login without entering credentials
    fireEvent.click(loginButton);

    expect(screen.getByText("Please enter both email and password.")).toBeTruthy();
    expect(mockLogin).not.toHaveBeenCalled();
  });
});
