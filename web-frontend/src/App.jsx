import { Box, CircularProgress } from "@mui/material";
import { useEffect } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import MainLayout from "./layouts/MainLayout";
import Dashboard from "./pages/Dashboard";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Monitoring from "./pages/Monitoring";
import NotFound from "./pages/NotFound";
import Optimization from "./pages/Optimization";
import PortfolioManagement from "./pages/PortfolioManagement";
import Register from "./pages/Register";
import RiskAnalysis from "./pages/RiskAnalysis";
import Settings from "./pages/Settings";

const Center = ({ children }) => (
  <Box
    sx={{
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      height: "100vh",
      bgcolor: "background.default",
    }}
  >
    {children}
  </Box>
);

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading)
    return (
      <Center>
        <CircularProgress />
      </Center>
    );
  if (!user) return <Navigate to="/login" state={{ from: location }} replace />;
  return children;
}

function App() {
  const { checkAuthState, loading } = useAuth();

  useEffect(() => {
    checkAuthState();
  }, [checkAuthState]);

  if (loading)
    return (
      <Center>
        <CircularProgress size={60} />
      </Center>
    );

  return (
    <Routes>
      {/* Public: the homepage is always the entry point */}
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Protected app shell with shared layout */}
      <Route
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/portfolio" element={<PortfolioManagement />} />
        <Route path="/risk-analysis" element={<RiskAnalysis />} />
        <Route path="/optimization" element={<Optimization />} />
        <Route path="/monitoring" element={<Monitoring />} />
        <Route path="/settings" element={<Settings />} />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

export default App;
