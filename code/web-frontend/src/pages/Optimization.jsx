import React, { useState } from 'react';
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
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Switch,
  FormControlLabel,
  Tooltip
} from '@mui/material';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import SaveAltIcon from '@mui/icons-material/SaveAlt';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import TuneIcon from '@mui/icons-material/Tune';

const Optimization = () => {
  const [riskTolerance, setRiskTolerance] = useState(50);

  const handleRiskToleranceChange = (event, newValue) => {
    setRiskTolerance(newValue);
  };

  return (
    <Box className="fade-in">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Portfolio Optimization
        </Typography>
        <Button
          variant="contained"
          startIcon={<SaveAltIcon />}
        >
          Save Optimization
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Optimization Parameters */}
        <Grid item xs={12} md={5}>
          <Card>
            <CardHeader
              title="Optimization Parameters"
              action={
                <IconButton>
                  <MoreVertIcon />
                </IconButton>
              }
            />
            <Divider />
            <CardContent>
              <Box sx={{ mb: 4 }}>
                <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                  Risk Tolerance
                  <Tooltip title="Higher risk tolerance may lead to higher potential returns but with increased volatility">
                    <IconButton size="small">
                      <InfoOutlinedIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Typography>
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs>
                    <Slider
                      value={riskTolerance}
                      onChange={handleRiskToleranceChange}
                      aria-labelledby="risk-tolerance-slider"
                      valueLabelDisplay="auto"
                      step={5}
                      marks
                      min={0}
                      max={100}
                    />
                  </Grid>
                  <Grid item>
                    <Typography variant="body2" color="text.secondary">
                      {riskTolerance < 30 ? 'Conservative' :
                       riskTolerance < 70 ? 'Moderate' : 'Aggressive'}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Optimization Method
                </Typography>
                <FormControl fullWidth size="small">
                  <Select
                    defaultValue="sharpe"
                  >
                    <MenuItem value="sharpe">Maximum Sharpe Ratio</MenuItem>
                    <MenuItem value="minrisk">Minimum Risk</MenuItem>
                    <MenuItem value="target">Target Return</MenuItem>
                    <MenuItem value="efficient">Efficient Frontier</MenuItem>
                  </Select>
                </FormControl>
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Time Horizon
                </Typography>
                <FormControl fullWidth size="small">
                  <Select
                    defaultValue="medium"
                  >
                    <MenuItem value="short">Short Term (1-2 years)</MenuItem>
                    <MenuItem value="medium">Medium Term (3-5 years)</MenuItem>
                    <MenuItem value="long">Long Term (5+ years)</MenuItem>
                  </Select>
                </FormControl>
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Constraints
                </Typography>
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="No Short Selling"
                />
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Max 20% per Asset"
                />
                <FormControlLabel
                  control={<Switch />}
                  label="Include ESG Factors"
                />
              </Box>

              <Button
                variant="contained"
                fullWidth
                startIcon={<PlayArrowIcon />}
                size="large"
                sx={{ mt: 2 }}
              >
                Run Optimization
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Optimization Results */}
        <Grid item xs={12} md={7}>
          <Card>
            <CardHeader
              title="Optimization Results"
              subheader="Maximum Sharpe Ratio Portfolio"
              action={
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<TuneIcon />}
                >
                  Adjust
                </Button>
              }
            />
            <Divider />
            <CardContent>
              <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={4}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Expected Return
                    </Typography>
                    <Typography variant="h5" color="success.main" sx={{ fontWeight: 600 }}>
                      12.4%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Annualized
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Expected Risk
                    </Typography>
                    <Typography variant="h5" sx={{ fontWeight: 600 }}>
                      9.8%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Volatility
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Sharpe Ratio
                    </Typography>
                    <Typography variant="h5" sx={{ fontWeight: 600 }}>
                      1.87
                    </Typography>
                    <Typography variant="body2" color="success.main">
                      Above Average
                    </Typography>
                  </Box>
                </Grid>
              </Grid>

              <Typography variant="subtitle2" gutterBottom>
                Optimized Asset Allocation
              </Typography>

              <Box sx={{ mb: 3 }}>
                {[
                  { name: 'Apple Inc. (AAPL)', current: 15, optimized: 12 },
                  { name: 'Microsoft Corp. (MSFT)', current: 12, optimized: 15 },
                  { name: 'Amazon.com Inc. (AMZN)', current: 10, optimized: 8 },
                  { name: 'Tesla Inc. (TSLA)', current: 8, optimized: 5 },
                  { name: 'Alphabet Inc. (GOOGL)', current: 10, optimized: 12 },
                  { name: 'Bitcoin (BTC)', current: 5, optimized: 3 },
                  { name: 'Ethereum (ETH)', current: 5, optimized: 5 },
                  { name: 'S&P 500 ETF (SPY)', current: 20, optimized: 25 },
                  { name: 'Gold ETF (GLD)', current: 10, optimized: 12 },
                  { name: 'Cash (USD)', current: 5, optimized: 3 },
                ].map((asset, index) => (
                  <Box key={index} sx={{ mb: 1 }}>
                    <Grid container alignItems="center">
                      <Grid item xs={5}>
                        <Typography variant="body2">{asset.name}</Typography>
                      </Grid>
                      <Grid item xs={3}>
                        <Typography variant="body2" color="text.secondary">
                          Current: {asset.current}%
                        </Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography
                          variant="body2"
                          sx={{
                            fontWeight: 600,
                            color: asset.optimized > asset.current ? 'success.main' :
                                   asset.optimized < asset.current ? 'error.main' : 'text.primary'
                          }}
                        >
                          {asset.optimized > asset.current ? '↑' :
                           asset.optimized < asset.current ? '↓' : '→'} {asset.optimized}%
                        </Typography>
                      </Grid>
                    </Grid>
                  </Box>
                ))}
              </Box>

              <Box sx={{ height: 300, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  Efficient frontier chart will be implemented with real data integration
                </Typography>
              </Box>

              <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
                <Button variant="outlined">
                  Compare with Current
                </Button>
                <Button variant="contained">
                  Apply Optimization
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Optimization;
