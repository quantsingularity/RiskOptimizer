import React, { useEffect } from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { Box, CircularProgress } from "@mui/material";
import MainLayout from "./layouts/MainLayout";
import Dashboard from "./pages/Dashboard";
import PortfolioManagement from "./pages/PortfolioManagement";
import RiskAnalysis from "./pages/RiskAnalysis";
import Optimization from "./pages/Optimization";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";
import Login from "./pages/Login";
import { useAuth } from "./context/AuthContext";

// Protected Route wrapper component
function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (!user) {
    // Redirect to login but save the location they were trying to access
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}

function App() {
  const { checkAuthState, loading } = useAuth();

  useEffect(() => {
    // Check authentication state on mount
    checkAuthState();
  }, [checkAuthState]);

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
          bgcolor: "background.default",
        }}
      >
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />

        {/* Protected routes with layout */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="portfolio" element={<PortfolioManagement />} />
          <Route path="risk-analysis" element={<RiskAnalysis />} />
          <Route path="optimization" element={<Optimization />} />
          <Route path="settings" element={<Settings />} />
        </Route>

        {/* 404 route */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Box>
  );
}

export default App;
