import RefreshIcon from "@mui/icons-material/Refresh";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Grid,
  Stack,
  Typography,
} from "@mui/material";
import { useCallback, useEffect, useState } from "react";
import apiService from "../services/apiService";
import { mono } from "../theme";

// A small status pill driven by a health string.
function StatusPill({ status }) {
  const ok = ["ok", "healthy", "up", "pass", true].includes(status);
  const degraded = ["degraded", "warning"].includes(status);
  return (
    <Chip
      size="small"
      label={typeof status === "string" ? status : ok ? "healthy" : "unknown"}
      sx={{
        fontFamily: mono,
        bgcolor: ok
          ? "rgba(52,199,123,0.14)"
          : degraded
            ? "rgba(229,181,103,0.14)"
            : "rgba(242,85,90,0.14)",
        color: ok ? "success.main" : degraded ? "warning.main" : "error.main",
      }}
    />
  );
}

function KeyValue({ data }) {
  const entries = Object.entries(data || {}).filter(
    ([, v]) => typeof v !== "object",
  );
  if (!entries.length) {
    return (
      <Typography variant="body2" color="text.secondary">
        No detail reported.
      </Typography>
    );
  }
  return (
    <Stack spacing={1}>
      {entries.map(([k, v]) => (
        <Stack
          key={k}
          direction="row"
          justifyContent="space-between"
          sx={{ borderBottom: "1px solid", borderColor: "divider", pb: 0.8 }}
        >
          <Typography variant="body2" color="text.secondary">
            {k}
          </Typography>
          {typeof v === "boolean" ? (
            <StatusPill status={v} />
          ) : (
            <Typography sx={{ fontFamily: mono, fontSize: "0.85rem" }}>
              {String(v)}
            </Typography>
          )}
        </Stack>
      ))}
    </Stack>
  );
}

const Monitoring = () => {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await apiService.healthCheck();
      setHealth(res);
    } catch (err) {
      setError(err.message || "Could not reach the monitoring service.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const overall = health?.status;

  return (
    <Box>
      <Stack
        direction="row"
        alignItems="center"
        justifyContent="space-between"
        sx={{ mb: 0.5 }}
      >
        <Typography variant="h4">System Status</Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={refresh}
          disabled={loading}
        >
          Refresh
        </Button>
      </Stack>
      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Live health for the API and its dependencies, read from the service
        health endpoint.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={5}>
          <Card>
            <CardContent>
              <Stack
                direction="row"
                alignItems="center"
                justifyContent="space-between"
                sx={{ mb: 2 }}
              >
                <Typography variant="h6">Overall</Typography>
                {loading ? (
                  <CircularProgress size={20} />
                ) : (
                  <StatusPill status={overall} />
                )}
              </Stack>
              <KeyValue data={health} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={7}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 1.5 }}>
                About these checks
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                The health endpoint aggregates the application, its database,
                and its cache. A degraded result usually means the cache is
                unreachable while the core API and database remain available.
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Operators can drill into per-subsystem metrics (system, cache,
                database, performance) through the monitoring API; those require
                an operator session.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Monitoring;
