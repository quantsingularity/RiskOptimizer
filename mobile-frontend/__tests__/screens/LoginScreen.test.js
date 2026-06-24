// mobile-frontend/__tests__/screens/LoginScreen.test.js

import {
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react-native";
import LoginScreen from "../../src/screens/Auth/LoginScreen";

// Mock context login function (mock-prefixed so jest allows it in factories)
const mockLogin = jest.fn();
const mockNavigate = jest.fn();
const mockNavigation = { navigate: mockNavigate };

// Mock the useAuth hook
jest.mock("../../src/context/AuthContext", () => ({
  useAuth: () => ({
    login: mockLogin,
    loading: false,
    authenticated: false,
    user: null,
  }),
}));

// Mock the apiService
jest.mock("../../src/services/apiService", () => ({
  login: jest.fn(),
  getUserProfile: jest.fn(),
  setAuthHeader: jest.fn(),
}));

// Mock SecureStore
jest.mock("expo-secure-store", () => ({
  setItemAsync: jest.fn(() => Promise.resolve()),
  getItemAsync: jest.fn(() => Promise.resolve(null)),
  deleteItemAsync: jest.fn(() => Promise.resolve()),
}));

// Mock @rneui/themed with real React Native primitives so that React Native
// Testing Library queries (testID) and events (changeText/press) behave as at runtime.
jest.mock("@rneui/themed", () => {
  const React = require("react");
  const { TextInput, TouchableOpacity, Text, View } = require("react-native");

  const Input = ({
    placeholder,
    onChangeText,
    value,
    secureTextEntry,
    disabled,
    testID,
  }) =>
    React.createElement(TextInput, {
      placeholder,
      onChangeText,
      value,
      secureTextEntry,
      editable: !disabled,
      testID: testID || `input-${placeholder}`,
    });

  const Button = ({ title, onPress, disabled, testID }) =>
    React.createElement(
      TouchableOpacity,
      { onPress, disabled, testID: testID || "button" },
      React.createElement(Text, null, title),
    );

  const Card = ({ children }) => React.createElement(View, null, children);
  Card.Title = ({ children }) => React.createElement(Text, null, children);
  Card.Divider = () => React.createElement(View, null);

  return {
    useTheme: () => ({
      theme: {
        colors: {
          primary: "#007AFF",
          background: "#FFFFFF",
          error: "#FF3B30",
          grey0: "#000000",
        },
      },
    }),
    Input,
    Button,
    Text: ({ children }) => React.createElement(Text, null, children),
    Card,
  };
});

describe("Login Screen", () => {
  beforeEach(() => {
    mockLogin.mockClear();
    mockNavigate.mockClear();
    mockLogin.mockResolvedValue(true);
  });

  const renderLoginScreen = () =>
    render(<LoginScreen navigation={mockNavigation} />);

  it("should render email and password inputs and login button", () => {
    renderLoginScreen();
    expect(screen.getByTestId("input-Email")).toBeTruthy();
    expect(screen.getByTestId("input-Password")).toBeTruthy();
    expect(screen.getByTestId("button")).toBeTruthy();
  });

  it("should update input fields when user types", () => {
    renderLoginScreen();
    fireEvent.changeText(screen.getByTestId("input-Email"), "test@example.com");
    fireEvent.changeText(screen.getByTestId("input-Password"), "password123");

    expect(screen.getByTestId("input-Email").props.value).toBe(
      "test@example.com",
    );
    expect(screen.getByTestId("input-Password").props.value).toBe(
      "password123",
    );
  });

  it("should call login function on button press with credentials", async () => {
    renderLoginScreen();

    fireEvent.changeText(screen.getByTestId("input-Email"), "test@example.com");
    fireEvent.changeText(screen.getByTestId("input-Password"), "password123");
    fireEvent.press(screen.getByTestId("button"));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith("test@example.com", "password123");
      expect(mockLogin).toHaveBeenCalledTimes(1);
    });
  });

  it("should display error message on failed login", async () => {
    mockLogin.mockResolvedValue(false);

    renderLoginScreen();

    fireEvent.changeText(
      screen.getByTestId("input-Email"),
      "wrong@example.com",
    );
    fireEvent.changeText(screen.getByTestId("input-Password"), "wrong");
    fireEvent.press(screen.getByTestId("button"));

    await waitFor(() => {
      expect(
        screen.getByText("Login failed. Please check your credentials."),
      ).toBeTruthy();
    });
  });

  it("should validate input fields before submission", () => {
    renderLoginScreen();
    fireEvent.press(screen.getByTestId("button"));

    expect(
      screen.getByText("Please enter both email and password."),
    ).toBeTruthy();
    expect(mockLogin).not.toHaveBeenCalled();
  });
});
