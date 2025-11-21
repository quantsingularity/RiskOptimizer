import React, { useEffect } from "react";
import { Routes, Route, useNavigate } from "react-router-dom";
import { Box, CircularProgress } from "@mui/material";
import MainLayout from "./layouts/MainLayout";
import Dashboard from "./pages/Dashboard";
import PortfolioManagement from "./pages/PortfolioManagement";
import RiskAnalysis from "./pages/RiskAnalysis";
import Optimization from "./pages/Optimization";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";
import { useAuth } from "./context/AuthContext";
import Login from "./pages/Login";

function App() {
  const { user, checkAuthState, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user is already logged in
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
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />

        {/* Protected routes */}
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="portfolio" element={<PortfolioManagement />} />
          <Route path="risk-analysis" element={<RiskAnalysis />} />
          <Route path="optimization" element={<Optimization />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </Box>
  );
}

export default App;
