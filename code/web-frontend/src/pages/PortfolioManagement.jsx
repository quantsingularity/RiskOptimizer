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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';

const PortfolioManagement = () => {
  return (
    <Box className="fade-in">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Portfolio Management
        </Typography>
        <Button 
          variant="contained" 
          startIcon={<AddIcon />}
        >
          Add Asset
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Current Portfolio */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title="Current Portfolio" 
              action={
                <Box sx={{ display: 'flex' }}>
                  <Button 
                    variant="outlined" 
                    size="small" 
                    startIcon={<EditIcon />}
                    sx={{ mr: 1 }}
                  >
                    Edit
                  </Button>
                  <Button 
                    variant="contained" 
                    size="small" 
                    startIcon={<SaveIcon />}
                  >
                    Save
                  </Button>
                </Box>
              }
            />
            <Divider />
            <CardContent>
              <TableContainer component={Paper} sx={{ backgroundColor: 'background.paper' }}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Asset</TableCell>
                      <TableCell>Symbol</TableCell>
                      <TableCell>Allocation (%)</TableCell>
                      <TableCell>Current Value</TableCell>
                      <TableCell>Performance</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {[
                      { name: 'Apple Inc.', symbol: 'AAPL', allocation: 15, value: '$18,679.93', performance: '+2.3%' },
                      { name: 'Microsoft Corp.', symbol: 'MSFT', allocation: 12, value: '$14,943.95', performance: '+1.7%' },
                      { name: 'Amazon.com Inc.', symbol: 'AMZN', allocation: 10, value: '$12,453.29', performance: '-0.8%' },
                      { name: 'Tesla Inc.', symbol: 'TSLA', allocation: 8, value: '$9,962.63', performance: '+3.5%' },
                      { name: 'Alphabet Inc.', symbol: 'GOOGL', allocation: 10, value: '$12,453.29', performance: '+0.5%' },
                      { name: 'Bitcoin', symbol: 'BTC', allocation: 5, value: '$6,226.64', performance: '+4.2%' },
                      { name: 'Ethereum', symbol: 'ETH', allocation: 5, value: '$6,226.64', performance: '+2.8%' },
                      { name: 'S&P 500 ETF', symbol: 'SPY', allocation: 20, value: '$24,906.58', performance: '+1.1%' },
                      { name: 'Gold ETF', symbol: 'GLD', allocation: 10, value: '$12,453.29', performance: '-0.3%' },
                      { name: 'Cash', symbol: 'USD', allocation: 5, value: '$6,226.64', performance: '0.0%' },
                    ].map((asset, index) => (
                      <TableRow key={index}>
                        <TableCell>{asset.name}</TableCell>
                        <TableCell>{asset.symbol}</TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Slider
                              value={asset.allocation}
                              disabled
                              sx={{ 
                                width: '100px', 
                                mr: 2,
                                color: asset.performance.startsWith('+') ? 'success.main' : 
                                       asset.performance.startsWith('-') ? 'error.main' : 'primary.main'
                              }}
                            />
                            <Typography>{asset.allocation}%</Typography>
                          </Box>
                        </TableCell>
                        <TableCell>{asset.value}</TableCell>
                        <TableCell sx={{ 
                          color: asset.performance.startsWith('+') ? 'success.main' : 
                                 asset.performance.startsWith('-') ? 'error.main' : 'text.primary'
                        }}>
                          {asset.performance}
                        </TableCell>
                        <TableCell>
                          <IconButton size="small" sx={{ mr: 1 }}>
                            <EditIcon fontSize="small" />
                          </IconButton>
                          <IconButton size="small" color="error">
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Portfolio Rebalancing */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader 
              title="Portfolio Rebalancing" 
              action={
                <IconButton>
                  <MoreVertIcon />
                </IconButton>
              }
            />
            <Divider />
            <CardContent>
              <Typography variant="body2" paragraph>
                Your portfolio is currently 8.5% away from your target allocation. We recommend rebalancing to maintain your risk profile.
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Rebalancing Strategy
                </Typography>
                <FormControl fullWidth size="small">
                  <Select
                    defaultValue="threshold"
                  >
                    <MenuItem value="threshold">Threshold-based (5%)</MenuItem>
                    <MenuItem value="periodic">Periodic (Quarterly)</MenuItem>
                    <MenuItem value="calendar">Calendar-based</MenuItem>
                  </Select>
                </FormControl>
              </Box>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Tax Optimization
                </Typography>
                <FormControl fullWidth size="small">
                  <Select
                    defaultValue="minimize"
                  >
                    <MenuItem value="minimize">Minimize Tax Impact</MenuItem>
                    <MenuItem value="ignore">Ignore Tax Considerations</MenuItem>
                    <MenuItem value="harvest">Tax-Loss Harvesting</MenuItem>
                  </Select>
                </FormControl>
              </Box>
              
              <Button 
                variant="contained" 
                fullWidth
              >
                Generate Rebalancing Plan
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Transaction History */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader 
              title="Transaction History" 
              action={
                <IconButton>
                  <MoreVertIcon />
                </IconButton>
              }
            />
            <Divider />
            <CardContent>
              <TableContainer sx={{ maxHeight: 300 }}>
                <Table stickyHeader size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Date</TableCell>
                      <TableCell>Asset</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Amount</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {[
                      { date: '2025-04-05', asset: 'AAPL', type: 'Buy', amount: '$2,500.00' },
                      { date: '2025-04-01', asset: 'TSLA', type: 'Sell', amount: '$1,800.00' },
                      { date: '2025-03-28', asset: 'BTC', type: 'Buy', amount: '$1,000.00' },
                      { date: '2025-03-15', asset: 'MSFT', type: 'Buy', amount: '$3,200.00' },
                      { date: '2025-03-10', asset: 'GLD', type: 'Sell', amount: '$2,100.00' },
                      { date: '2025-03-01', asset: 'SPY', type: 'Buy', amount: '$5,000.00' },
                      { date: '2025-02-22', asset: 'AMZN', type: 'Buy', amount: '$2,800.00' },
                      { date: '2025-02-15', asset: 'GOOGL', type: 'Sell', amount: '$1,500.00' },
                    ].map((transaction, index) => (
                      <TableRow key={index}>
                        <TableCell>{transaction.date}</TableCell>
                        <TableCell>{transaction.asset}</TableCell>
                        <TableCell sx={{ 
                          color: transaction.type === 'Buy' ? 'success.main' : 'error.main'
                        }}>
                          {transaction.type}
                        </TableCell>
                        <TableCell>{transaction.amount}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
                <Button variant="text">View All Transactions</Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default PortfolioManagement;
