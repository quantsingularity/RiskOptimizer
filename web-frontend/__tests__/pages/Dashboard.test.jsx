import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import Dashboard from "../../src/pages/Dashboard";

const theme = createTheme();

const renderWithProviders = (component) => {
  return render(
    <BrowserRouter>
      <ThemeProvider theme={theme}>{component}</ThemeProvider>
    </BrowserRouter>,
  );
};

describe("Dashboard", () => {
  it("should render dashboard heading", () => {
    renderWithProviders(<Dashboard />);
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
  });

  it("should display portfolio value card", () => {
    renderWithProviders(<Dashboard />);
    expect(screen.getByText("Total Portfolio Value")).toBeInTheDocument();
  });

  it("should display daily change card", () => {
    renderWithProviders(<Dashboard />);
    expect(screen.getByText("Daily Change")).toBeInTheDocument();
  });

  it("should display risk score card", () => {
    renderWithProviders(<Dashboard />);
    expect(screen.getByText("Risk Score")).toBeInTheDocument();
  });

  it("should display sharpe ratio card", () => {
    renderWithProviders(<Dashboard />);
    expect(screen.getByText("Sharpe Ratio")).toBeInTheDocument();
  });

  it("should display portfolio performance section", () => {
    renderWithProviders(<Dashboard />);
    expect(screen.getByText("Portfolio Performance")).toBeInTheDocument();
  });

  it("should display asset allocation section", () => {
    renderWithProviders(<Dashboard />);
    expect(screen.getByText("Asset Allocation")).toBeInTheDocument();
  });

  it("should display risk metrics section", () => {
    renderWithProviders(<Dashboard />);
    expect(screen.getByText("Risk Metrics")).toBeInTheDocument();
  });

  it("should display recent transactions section", () => {
    renderWithProviders(<Dashboard />);
    expect(screen.getByText("Recent Transactions")).toBeInTheDocument();
  });

  it("should display optimization suggestions", () => {
    renderWithProviders(<Dashboard />);
    expect(screen.getByText("Optimization Suggestions")).toBeInTheDocument();
  });

  it("should have refresh data button", () => {
    renderWithProviders(<Dashboard />);
    const refreshButton = screen.getByRole("button", { name: /refresh data/i });
    expect(refreshButton).toBeInTheDocument();
  });

  it("should display mock portfolio values", () => {
    renderWithProviders(<Dashboard />);
    expect(screen.getByText("$124,532.89")).toBeInTheDocument();
  });

  it("should display positive performance indicators", () => {
    renderWithProviders(<Dashboard />);
    const positiveIndicators = screen.getAllByText(/\+/);
    expect(positiveIndicators.length).toBeGreaterThan(0);
  });

  it("should display percentage changes", () => {
    renderWithProviders(<Dashboard />);
    expect(screen.getByText("+2.45% ($3,012.34)")).toBeInTheDocument();
  });

  it("should render VaR metric", () => {
    renderWithProviders(<Dashboard />);
    expect(screen.getByText("Value at Risk (VaR)")).toBeInTheDocument();
    expect(screen.getByText("$4,532.12")).toBeInTheDocument();
  });

  it("should render volatility metric", () => {
    renderWithProviders(<Dashboard />);
    expect(screen.getByText("Volatility")).toBeInTheDocument();
    expect(screen.getByText("14.2%")).toBeInTheDocument();
  });
});
