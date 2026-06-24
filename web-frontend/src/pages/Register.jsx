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
import { useNavigate, Link as RouterLink } from "react-router-dom";
import AuthShell from "../components/auth/AuthShell";
import { useAuth } from "../context/AuthContext";

// Mirrors the backend policy: 12+ chars, upper, lower, digit, special.
function passwordIssues(pw) {
  const issues = [];
  if (pw.length < 12) issues.push("at least 12 characters");
  if (!/[A-Z]/.test(pw)) issues.push("an uppercase letter");
  if (!/[a-z]/.test(pw)) issues.push("a lowercase letter");
  if (!/[0-9]/.test(pw)) issues.push("a digit");
  if (!/[^A-Za-z0-9]/.test(pw)) issues.push("a special character");
  return issues;
}

const Register = () => {
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [localError, setLocalError] = useState("");
  const { register, loading, error, user, clearError } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) navigate("/dashboard", { replace: true });
  }, [user, navigate]);

  useEffect(() => () => clearError(), [clearError]);

  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
    setLocalError("");
  };

  const pwIssues = form.password ? passwordIssues(form.password) : [];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.username || !form.email || !form.password) {
      setLocalError("Fill in every field to create your account.");
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
      setLocalError("Enter a valid email address.");
      return;
    }
    if (pwIssues.length) {
      setLocalError(`Your password needs ${pwIssues.join(", ")}.`);
      return;
    }
    const ok = await register(form);
    if (ok) navigate("/dashboard", { replace: true });
  };

  const displayError = localError || error;

  return (
    <AuthShell
      title="Create your account"
      subtitle="Set up a workspace and run your first risk report."
    >
      <Box component="form" onSubmit={handleSubmit} noValidate>
        {displayError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {displayError}
          </Alert>
        )}
        <TextField
          fullWidth
          label="Username"
          autoComplete="username"
          autoFocus
          value={form.username}
          onChange={handleChange("username")}
          disabled={loading}
          sx={{ mb: 2 }}
        />
        <TextField
          fullWidth
          label="Email"
          type="email"
          autoComplete="email"
          value={form.email}
          onChange={handleChange("email")}
          disabled={loading}
          sx={{ mb: 2 }}
        />
        <TextField
          fullWidth
          label="Password"
          type="password"
          autoComplete="new-password"
          value={form.password}
          onChange={handleChange("password")}
          disabled={loading}
          error={Boolean(form.password) && pwIssues.length > 0}
          helperText={
            form.password && pwIssues.length
              ? `Needs ${pwIssues.join(", ")}.`
              : "12+ characters with upper, lower, a digit, and a symbol."
          }
          sx={{ mb: 3 }}
        />
        <Button
          type="submit"
          fullWidth
          variant="contained"
          disabled={loading}
          sx={{ py: 1.3 }}
        >
          {loading ? <CircularProgress size={22} /> : "Create account"}
        </Button>

        <Stack
          direction="row"
          justifyContent="center"
          spacing={0.5}
          sx={{ mt: 3 }}
        >
          <Typography variant="body2" color="text.secondary">
            Already have an account?
          </Typography>
          <MuiLink component={RouterLink} to="/login" underline="hover">
            Sign in
          </MuiLink>
        </Stack>
      </Box>
    </AuthShell>
  );
};

export default Register;
