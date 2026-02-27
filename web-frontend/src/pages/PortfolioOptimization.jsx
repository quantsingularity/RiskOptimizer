import React, { useState } from "react";
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Divider,
  Button,
  IconButton,
  TextField,
  MenuItem,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
} from "@mui/material";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import CalculateIcon from "@mui/icons-material/Calculate";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

// Dummy data for the Efficient Frontier chart
const efficientFrontierData = [
  { risk: 0.05, return: 0.08, type: "Efficient Frontier" },
  { risk: 0.07, return: 0.1, type: "Efficient Frontier" },
  { risk: 0.1, return: 0.12, type: "Efficient Frontier" },
  { risk: 0.13, return: 0.13, type: "Efficient Frontier" },
  { risk: 0.16, return: 0.14, type: "Efficient Frontier" },
  { risk: 0.2, return: 0.15, type: "Efficient Frontier" },
];

const PortfolioOptimization = () => {
  const [optimizationGoal, setOptimizationGoal] = useState("max_sharpe");
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optimizationResult, setOptimizationResult] = useState(null);
  const [error, setError] = useState(null);

  const handleOptimize = () => {
    setIsOptimizing(true);
    setError(null);
    setOptimizationResult(null);

    // Simulate API call
    setTimeout(() => {
      setIsOptimizing(false);
      if (Math.random() > 0.1) {
        // 90% success rate
        setOptimizationResult({
          goal: optimizationGoal,
          expectedReturn: 0.145,
          expectedRisk: 0.112,
          sharpeRatio: 1.3,
          weights: [
            { asset: "Stock A", weight: 0.35 },
            { asset: "Stock B", weight: 0.25 },
            { asset: "Bond C", weight: 0.4 },
          ],
        });
      } else {
        setError("Optimization failed. Please check your input and try again.");
      }
    }, 2000);
  };

  const optimizedPortfolioData = optimizationResult
    ? [
        {
          risk: optimizationResult.expectedRisk,
          return: optimizationResult.expectedReturn,
          type: "Optimized Portfolio",
        },
      ]
    : [];

  return (
    <Box className="fade-in">
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <Typography variant="h4" component="h1" gutterBottom>
          Portfolio Optimization
        </Typography>
        <Button
          variant="contained"
          startIcon={<CalculateIcon />}
          onClick={handleOptimize}
          disabled={isOptimizing}
        >
          {isOptimizing ? (
            <CircularProgress size={24} color="inherit" />
          ) : (
            "Run Optimization"
          )}
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Optimization Controls */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: "100%" }}>
            <CardHeader title="Optimization Settings" />
            <Divider />
            <CardContent>
              <TextField
                select
                label="Optimization Goal"
                value={optimizationGoal}
                onChange={(e) => setOptimizationGoal(e.target.value)}
                fullWidth
                margin="normal"
                helperText="Select the objective for the portfolio optimization"
              >
                <MenuItem value="max_sharpe">Maximize Sharpe Ratio</MenuItem>
                <MenuItem value="min_volatility">Minimize Volatility</MenuItem>
                <MenuItem value="target_return">Target Return</MenuItem>
              </TextField>
              {optimizationGoal === "target_return" && (
                <TextField
                  label="Target Return (%)"
                  type="number"
                  fullWidth
                  margin="normal"
                  defaultValue={10}
                  inputProps={{ step: "0.1" }}
                />
              )}
              <TextField
                label="Risk-Free Rate (%)"
                type="number"
                fullWidth
                margin="normal"
                defaultValue={2.0}
                inputProps={{ step: "0.1" }}
                helperText="Used in Sharpe Ratio calculation"
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Efficient Frontier Chart */}
        <Grid item xs={12} md={8}>
          <Card sx={{ height: "100%" }}>
            <CardHeader
              title="Efficient Frontier"
              action={
                <IconButton>
                  <MoreVertIcon />
                </IconButton>
              }
            />
            <Divider />
            <CardContent sx={{ height: 400, p: 2 }}>
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart
                  margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
                >
                  <CartesianGrid />
                  <XAxis
                    type="number"
                    dataKey="risk"
                    name="Risk (Volatility)"
                    unit="%"
                    tickFormatter={(tick) => (tick * 100).toFixed(1)}
                  />
                  <YAxis
                    type="number"
                    dataKey="return"
                    name="Return"
                    unit="%"
                    tickFormatter={(tick) => (tick * 100).toFixed(1)}
                  />
                  <Tooltip
                    cursor={{ strokeDasharray: "3 3" }}
                    formatter={(value, name, props) => [
                      `${(value * 100).toFixed(2)}%`,
                      name === "risk" ? "Risk" : "Return",
                    ]}
                  />
                  <Legend />
                  <Scatter
                    name="Efficient Frontier"
                    data={efficientFrontierData}
                    fill="#8884d8"
                  />
                  <Scatter
                    name="Optimized Portfolio"
                    data={optimizedPortfolioData}
                    fill="#ff7300"
                    shape="star"
                  />
                </ScatterChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Optimization Results */}
        {error && (
          <Grid item xs={12}>
            <Alert severity="error">{error}</Alert>
          </Grid>
        )}
        {optimizationResult && (
          <Grid item xs={12}>
            <Card>
              <CardHeader
                title={`Optimization Results (${optimizationResult.goal.replace("_", " ").toUpperCase()})`}
              />
              <Divider />
              <CardContent>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={4}>
                    <Typography variant="subtitle1">
                      Expected Return:
                    </Typography>
                    <Typography variant="h4" color="primary">
                      {(optimizationResult.expectedReturn * 100).toFixed(2)}%
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Typography variant="subtitle1">
                      Expected Risk (Volatility):
                    </Typography>
                    <Typography variant="h4" color="secondary">
                      {(optimizationResult.expectedRisk * 100).toFixed(2)}%
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Typography variant="subtitle1">Sharpe Ratio:</Typography>
                    <Typography variant="h4" color="success.main">
                      {optimizationResult.sharpeRatio.toFixed(2)}
                    </Typography>
                  </Grid>
                </Grid>
                <Divider sx={{ my: 3 }} />
                <Typography variant="h6" gutterBottom>
                  Optimal Asset Weights
                </Typography>
                <List dense>
                  {optimizationResult.weights.map((item) => (
                    <ListItem key={item.asset}>
                      <ListItemText
                        primary={item.asset}
                        secondary={`Weight: ${(item.weight * 100).toFixed(2)}%`}
                      />
                    </ListItem>
                  ))}
                </List>
                <Button variant="contained" sx={{ mt: 2 }}>
                  Apply Weights to Portfolio
                </Button>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default PortfolioOptimization;
