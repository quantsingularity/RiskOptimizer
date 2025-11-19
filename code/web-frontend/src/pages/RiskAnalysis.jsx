import React from 'react';
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
  Tabs,
  Tab,
  TextField,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import CalculateIcon from '@mui/icons-material/Calculate';
import DownloadIcon from '@mui/icons-material/Download';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';

const RiskAnalysis = () => {
  const [tabValue, setTabValue] = React.useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <Box className="fade-in">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Risk Analysis
        </Typography>
        <Button
          variant="contained"
          startIcon={<DownloadIcon />}
        >
          Export Report
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Risk Metrics Summary */}
        <Grid item xs={12}>
          <Card>
            <CardHeader
              title="Risk Metrics Summary"
              action={
                <IconButton>
                  <MoreVertIcon />
                </IconButton>
              }
            />
            <Divider />
            <CardContent>
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Value at Risk (95%)
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 600 }}>
                      $4,532.12
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      3.64% of portfolio
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Volatility (Annualized)
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 600 }}>
                      14.2%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Moderate volatility
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Sharpe Ratio
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 600 }}>
                      1.87
                    </Typography>
                    <Typography variant="body2" color="success.main">
                      Good risk-adjusted return
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Maximum Drawdown
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 600 }}>
                      -12.4%
                    </Typography>
                    <Typography variant="body2" color="warning.main">
                      Moderate risk
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Risk Analysis Tools */}
        <Grid item xs={12}>
          <Card>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs value={tabValue} onChange={handleTabChange} aria-label="risk analysis tabs">
                <Tab label="Value at Risk (VaR)" />
                <Tab label="Stress Testing" />
                <Tab label="Correlation Analysis" />
                <Tab label="Risk Contribution" />
              </Tabs>
            </Box>
            <CardContent>
              {tabValue === 0 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Value at Risk (VaR) Calculator
                  </Typography>
                  <Typography variant="body2" paragraph>
                    Value at Risk (VaR) estimates the maximum potential loss of your portfolio over a specific time period at a given confidence level.
                  </Typography>

                  <Grid container spacing={3} sx={{ mb: 3 }}>
                    <Grid item xs={12} md={6}>
                      <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                        <InputLabel>Confidence Level</InputLabel>
                        <Select
                          defaultValue={95}
                          label="Confidence Level"
                        >
                          <MenuItem value={90}>90%</MenuItem>
                          <MenuItem value={95}>95%</MenuItem>
                          <MenuItem value={99}>99%</MenuItem>
                        </Select>
                      </FormControl>

                      <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                        <InputLabel>Time Horizon</InputLabel>
                        <Select
                          defaultValue={1}
                          label="Time Horizon"
                        >
                          <MenuItem value={1}>1 Day</MenuItem>
                          <MenuItem value={5}>1 Week (5 Days)</MenuItem>
                          <MenuItem value={20}>1 Month (20 Days)</MenuItem>
                          <MenuItem value={60}>3 Months (60 Days)</MenuItem>
                        </Select>
                      </FormControl>

                      <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                        <InputLabel>Calculation Method</InputLabel>
                        <Select
                          defaultValue="historical"
                          label="Calculation Method"
                        >
                          <MenuItem value="historical">Historical Simulation</MenuItem>
                          <MenuItem value="parametric">Parametric (Variance-Covariance)</MenuItem>
                          <MenuItem value="montecarlo">Monte Carlo Simulation</MenuItem>
                        </Select>
                      </FormControl>

                      <Button
                        variant="contained"
                        startIcon={<CalculateIcon />}
                        fullWidth
                      >
                        Calculate VaR
                      </Button>
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <Card variant="outlined" sx={{ height: '100%', backgroundColor: 'background.default' }}>
                        <CardContent>
                          <Typography variant="subtitle2" gutterBottom>
                            VaR Results
                          </Typography>
                          <Box sx={{ mb: 2 }}>
                            <Typography variant="body2" color="text.secondary">
                              Absolute VaR (95% confidence, 1 day)
                            </Typography>
                            <Typography variant="h5" sx={{ fontWeight: 600 }}>
                              $4,532.12
                            </Typography>
                          </Box>
                          <Box sx={{ mb: 2 }}>
                            <Typography variant="body2" color="text.secondary">
                              Relative VaR (% of portfolio)
                            </Typography>
                            <Typography variant="h5" sx={{ fontWeight: 600 }}>
                              3.64%
                            </Typography>
                          </Box>
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Interpretation
                            </Typography>
                            <Typography variant="body2">
                              With 95% confidence, your maximum loss will not exceed $4,532.12 (3.64% of your portfolio) over the next day.
                            </Typography>
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  </Grid>

                  <Box sx={{ height: 300, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      VaR distribution chart will be implemented with real data integration
                    </Typography>
                  </Box>
                </Box>
              )}

              {tabValue === 1 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Stress Testing
                  </Typography>
                  <Typography variant="body2" paragraph>
                    Stress testing evaluates how your portfolio would perform under extreme market conditions or historical crisis scenarios.
                  </Typography>

                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2" gutterBottom>
                        Historical Scenarios
                      </Typography>
                      <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                        <Select
                          defaultValue="2008"
                          displayEmpty
                        >
                          <MenuItem value="2008">2008 Financial Crisis</MenuItem>
                          <MenuItem value="2020">2020 COVID-19 Crash</MenuItem>
                          <MenuItem value="2000">2000 Dot-com Bubble</MenuItem>
                          <MenuItem value="1987">1987 Black Monday</MenuItem>
                          <MenuItem value="custom">Custom Scenario</MenuItem>
                        </Select>
                      </FormControl>

                      <Button
                        variant="contained"
                        fullWidth
                        sx={{ mb: 3 }}
                      >
                        Run Stress Test
                      </Button>

                      <Typography variant="subtitle2" gutterBottom>
                        Custom Stress Factors
                      </Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={8}>
                          <Typography variant="body2">Equity Markets</Typography>
                        </Grid>
                        <Grid item xs={4}>
                          <TextField
                            size="small"
                            defaultValue="-30"
                            InputProps={{ endAdornment: '%' }}
                          />
                        </Grid>

                        <Grid item xs={8}>
                          <Typography variant="body2">Bond Yields</Typography>
                        </Grid>
                        <Grid item xs={4}>
                          <TextField
                            size="small"
                            defaultValue="+1.5"
                            InputProps={{ endAdornment: '%' }}
                          />
                        </Grid>

                        <Grid item xs={8}>
                          <Typography variant="body2">Cryptocurrency</Typography>
                        </Grid>
                        <Grid item xs={4}>
                          <TextField
                            size="small"
                            defaultValue="-45"
                            InputProps={{ endAdornment: '%' }}
                          />
                        </Grid>
                      </Grid>
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <Card variant="outlined" sx={{ backgroundColor: 'background.default' }}>
                        <CardContent>
                          <Typography variant="subtitle2" gutterBottom>
                            Stress Test Results: 2008 Financial Crisis
                          </Typography>
                          <Box sx={{ mb: 2 }}>
                            <Typography variant="body2" color="text.secondary">
                              Estimated Portfolio Loss
                            </Typography>
                            <Typography variant="h5" color="error.main" sx={{ fontWeight: 600 }}>
                              -32.8%
                            </Typography>
                          </Box>
                          <Typography variant="subtitle2" gutterBottom>
                            Impact by Asset Class
                          </Typography>
                          <Box sx={{ mb: 1 }}>
                            <Typography variant="body2" display="inline">
                              Equities:
                            </Typography>
                            <Typography variant="body2" color="error.main" display="inline" sx={{ ml: 1 }}>
                              -42.5%
                            </Typography>
                          </Box>
                          <Box sx={{ mb: 1 }}>
                            <Typography variant="body2" display="inline">
                              Bonds:
                            </Typography>
                            <Typography variant="body2" color="success.main" display="inline" sx={{ ml: 1 }}>
                              +5.2%
                            </Typography>
                          </Box>
                          <Box sx={{ mb: 1 }}>
                            <Typography variant="body2" display="inline">
                              Crypto:
                            </Typography>
                            <Typography variant="body2" color="error.main" display="inline" sx={{ ml: 1 }}>
                              -60.8%
                            </Typography>
                          </Box>
                          <Box sx={{ mb: 1 }}>
                            <Typography variant="body2" display="inline">
                              Gold:
                            </Typography>
                            <Typography variant="body2" color="success.main" display="inline" sx={{ ml: 1 }}>
                              +12.3%
                            </Typography>
                          </Box>
                        </CardContent>
                      </Card>

                      <Box sx={{ mt: 3, height: 200, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                        <Typography variant="body2" color="text.secondary">
                          Stress test visualization will be implemented with real data integration
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </Box>
              )}

              {tabValue === 2 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Correlation Analysis
                  </Typography>
                  <Typography variant="body2" paragraph>
                    Correlation analysis helps you understand how assets in your portfolio move in relation to each other, which is crucial for diversification.
                  </Typography>

                  <Box sx={{ height: 400, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      Correlation matrix heatmap will be implemented with real data integration
                    </Typography>
                  </Box>
                </Box>
              )}

              {tabValue === 3 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Risk Contribution
                  </Typography>
                  <Typography variant="body2" paragraph>
                    Risk contribution analysis shows how much each asset contributes to your portfolio's overall risk.
                  </Typography>

                  <Box sx={{ height: 400, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      Risk contribution chart will be implemented with real data integration
                    </Typography>
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default RiskAnalysis;
