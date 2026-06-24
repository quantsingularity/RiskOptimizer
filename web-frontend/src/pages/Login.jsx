import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Link as MuiLink,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useEffect, useState } from "react";
import { useLocation, useNavigate, Link as RouterLink } from "react-router-dom";
import AuthShell from "../components/auth/AuthShell";
import { useAuth } from "../context/AuthContext";

const Login = () => {
  const [form, setForm] = useState({ email: "", password: "" });
  const [localError, setLocalError] = useState("");
  const { login, loading, error, user, clearError } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || "/dashboard";

  useEffect(() => {
    if (user) navigate(from, { replace: true });
  }, [user, navigate, from]);

  useEffect(() => () => clearError(), [clearError]);

  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
    setLocalError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.email || !form.password) {
      setLocalError("Enter your email and password to sign in.");
      return;
    }
    const ok = await login(form);
    if (ok) navigate(from, { replace: true });
  };

  const displayError = localError || error;

  return (
    <AuthShell
      title="Sign in"
      subtitle="Welcome back. Pick up where you left off."
    >
      <Box component="form" onSubmit={handleSubmit} noValidate>
        {displayError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {displayError}
          </Alert>
        )}
        <TextField
          fullWidth
          label="Email"
          type="email"
          autoComplete="email"
          autoFocus
          value={form.email}
          onChange={handleChange("email")}
          disabled={loading}
          sx={{ mb: 2 }}
        />
        <TextField
          fullWidth
          label="Password"
          type="password"
          autoComplete="current-password"
          value={form.password}
          onChange={handleChange("password")}
          disabled={loading}
          sx={{ mb: 3 }}
        />
        <Button
          type="submit"
          fullWidth
          variant="contained"
          disabled={loading}
          sx={{ py: 1.3 }}
        >
          {loading ? <CircularProgress size={22} /> : "Sign in"}
        </Button>

        <Stack
          direction="row"
          justifyContent="center"
          spacing={0.5}
          sx={{ mt: 3 }}
        >
          <Typography variant="body2" color="text.secondary">
            New to RiskOptimizer?
          </Typography>
          <MuiLink component={RouterLink} to="/register" underline="hover">
            Create an account
          </MuiLink>
        </Stack>
      </Box>
    </AuthShell>
  );
};

export default Login;
