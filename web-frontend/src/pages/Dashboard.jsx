import React from 'react';
import {
    Box,
    Grid,
    Paper,
    Typography,
    Card,
    CardContent,
    CardHeader,
    Divider,
    Button,
    IconButton,
    Tooltip,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import PortfolioSummary from '../components/dashboard/PortfolioSummary';
import PerformanceChart from '../components/dashboard/PerformanceChart';
import AssetAllocation from '../components/dashboard/AssetAllocation';
import RiskMetricsCard from '../components/dashboard/RiskMetricsCard';
import RecentTransactions from '../components/dashboard/RecentTransactions';

const Dashboard = () => {
    return (
        <Box className="fade-in">
            <Box
                sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    mb: 3,
                }}
            >
                <Typography variant="h4" component="h1" gutterBottom>
                    Dashboard
                </Typography>
                <Button variant="contained" startIcon={<RefreshIcon />} size="small">
                    Refresh Data
                </Button>
            </Box>

            {/* Portfolio Summary Cards */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ height: '100%' }}>
                        <CardContent sx={{ p: 2 }}>
                            <Box
                                sx={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                }}
                            >
                                <Typography variant="subtitle2" color="text.secondary">
                                    Total Portfolio Value
                                </Typography>
                                <IconButton size="small">
                                    <MoreVertIcon fontSize="small" />
                                </IconButton>
                            </Box>
                            <Typography variant="h4" sx={{ my: 1, fontWeight: 600 }}>
                                $124,532.89
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <TrendingUpIcon color="success" fontSize="small" sx={{ mr: 0.5 }} />
                                <Typography variant="body2" color="success.main">
                                    +2.45% ($3,012.34)
                                </Typography>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ height: '100%' }}>
                        <CardContent sx={{ p: 2 }}>
                            <Box
                                sx={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                }}
                            >
                                <Typography variant="subtitle2" color="text.secondary">
                                    Daily Change
                                </Typography>
                                <IconButton size="small">
                                    <MoreVertIcon fontSize="small" />
                                </IconButton>
                            </Box>
                            <Typography variant="h4" sx={{ my: 1, fontWeight: 600 }}>
                                +$1,245.67
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <TrendingUpIcon color="success" fontSize="small" sx={{ mr: 0.5 }} />
                                <Typography variant="body2" color="success.main">
                                    +1.02% today
                                </Typography>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ height: '100%' }}>
                        <CardContent sx={{ p: 2 }}>
                            <Box
                                sx={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                }}
                            >
                                <Typography variant="subtitle2" color="text.secondary">
                                    Risk Score
                                </Typography>
                                <IconButton size="small">
                                    <MoreVertIcon fontSize="small" />
                                </IconButton>
                            </Box>
                            <Typography variant="h4" sx={{ my: 1, fontWeight: 600 }}>
                                65/100
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <TrendingDownIcon
                                    color="warning"
                                    fontSize="small"
                                    sx={{ mr: 0.5 }}
                                />
                                <Typography variant="body2" color="warning.main">
                                    Moderate Risk
                                </Typography>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ height: '100%' }}>
                        <CardContent sx={{ p: 2 }}>
                            <Box
                                sx={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                }}
                            >
                                <Typography variant="subtitle2" color="text.secondary">
                                    Sharpe Ratio
                                </Typography>
                                <IconButton size="small">
                                    <MoreVertIcon fontSize="small" />
                                </IconButton>
                            </Box>
                            <Typography variant="h4" sx={{ my: 1, fontWeight: 600 }}>
                                1.87
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <TrendingUpIcon color="success" fontSize="small" sx={{ mr: 0.5 }} />
                                <Typography variant="body2" color="success.main">
                                    Good Performance
                                </Typography>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Main Content */}
            <Grid container spacing={3}>
                {/* Performance Chart */}
                <Grid item xs={12} lg={8}>
                    <Card sx={{ height: '100%' }}>
                        <CardHeader
                            title="Portfolio Performance"
                            action={
                                <Box sx={{ display: 'flex' }}>
                                    <Button size="small" sx={{ mr: 1 }}>
                                        1D
                                    </Button>
                                    <Button size="small" sx={{ mr: 1 }}>
                                        1W
                                    </Button>
                                    <Button size="small" sx={{ mr: 1 }}>
                                        1M
                                    </Button>
                                    <Button size="small" sx={{ mr: 1 }}>
                                        3M
                                    </Button>
                                    <Button size="small" variant="contained">
                                        1Y
                                    </Button>
                                    <Button size="small" sx={{ ml: 1 }}>
                                        All
                                    </Button>
                                </Box>
                            }
                        />
                        <Divider />
                        <CardContent sx={{ height: 300, p: 2 }}>
                            <Box
                                sx={{
                                    display: 'flex',
                                    justifyContent: 'center',
                                    alignItems: 'center',
                                    height: '100%',
                                }}
                            >
                                <Typography variant="body2" color="text.secondary">
                                    Performance chart will be implemented with real data integration
                                </Typography>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Asset Allocation */}
                <Grid item xs={12} md={6} lg={4}>
                    <Card sx={{ height: '100%' }}>
                        <CardHeader
                            title="Asset Allocation"
                            action={
                                <IconButton>
                                    <MoreVertIcon />
                                </IconButton>
                            }
                        />
                        <Divider />
                        <CardContent sx={{ height: 300, p: 2 }}>
                            <Box
                                sx={{
                                    display: 'flex',
                                    justifyContent: 'center',
                                    alignItems: 'center',
                                    height: '100%',
                                }}
                            >
                                <Typography variant="body2" color="text.secondary">
                                    Asset allocation chart will be implemented with real data
                                    integration
                                </Typography>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Risk Metrics */}
                <Grid item xs={12} md={6} lg={4}>
                    <Card sx={{ height: '100%' }}>
                        <CardHeader
                            title="Risk Metrics"
                            action={
                                <IconButton>
                                    <MoreVertIcon />
                                </IconButton>
                            }
                        />
                        <Divider />
                        <CardContent sx={{ p: 2 }}>
                            <Grid container spacing={2}>
                                <Grid item xs={6}>
                                    <Typography variant="subtitle2" color="text.secondary">
                                        Value at Risk (VaR)
                                    </Typography>
                                    <Typography variant="h6">$4,532.12</Typography>
                                </Grid>
                                <Grid item xs={6}>
                                    <Typography variant="subtitle2" color="text.secondary">
                                        Max Drawdown
                                    </Typography>
                                    <Typography variant="h6">-12.4%</Typography>
                                </Grid>
                                <Grid item xs={6}>
                                    <Typography variant="subtitle2" color="text.secondary">
                                        Volatility
                                    </Typography>
                                    <Typography variant="h6">14.2%</Typography>
                                </Grid>
                                <Grid item xs={6}>
                                    <Typography variant="subtitle2" color="text.secondary">
                                        Beta
                                    </Typography>
                                    <Typography variant="h6">0.85</Typography>
                                </Grid>
                            </Grid>
                            <Box sx={{ mt: 2 }}>
                                <Button
                                    variant="outlined"
                                    fullWidth
                                    size="small"
                                    href="/risk-analysis"
                                >
                                    View Detailed Analysis
                                </Button>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Recent Transactions */}
                <Grid item xs={12} lg={8}>
                    <Card>
                        <CardHeader
                            title="Recent Transactions"
                            action={
                                <Button
                                    variant="text"
                                    size="small"
                                    endIcon={<AccountBalanceWalletIcon />}
                                >
                                    View All
                                </Button>
                            }
                        />
                        <Divider />
                        <CardContent sx={{ p: 0 }}>
                            <Box
                                sx={{
                                    display: 'flex',
                                    justifyContent: 'center',
                                    alignItems: 'center',
                                    height: 200,
                                }}
                            >
                                <Typography variant="body2" color="text.secondary">
                                    Transaction history will be implemented with real data
                                    integration
                                </Typography>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Optimization Suggestions */}
                <Grid item xs={12} md={6} lg={4}>
                    <Card>
                        <CardHeader
                            title="Optimization Suggestions"
                            action={
                                <IconButton>
                                    <MoreVertIcon />
                                </IconButton>
                            }
                        />
                        <Divider />
                        <CardContent>
                            <Typography variant="body2" paragraph>
                                Based on our AI analysis, we recommend the following portfolio
                                adjustments:
                            </Typography>
                            <Box sx={{ mb: 2 }}>
                                <Typography variant="subtitle2" color="success.main">
                                    Increase:
                                </Typography>
                                <Typography variant="body2">• Technology sector (+2.5%)</Typography>
                                <Typography variant="body2">• Healthcare stocks (+1.8%)</Typography>
                            </Box>
                            <Box sx={{ mb: 2 }}>
                                <Typography variant="subtitle2" color="error.main">
                                    Decrease:
                                </Typography>
                                <Typography variant="body2">• Energy sector (-3.1%)</Typography>
                                <Typography variant="body2">
                                    • Consumer discretionary (-1.2%)
                                </Typography>
                            </Box>
                            <Button variant="contained" fullWidth size="small" href="/optimization">
                                Run Optimization
                            </Button>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
};

export default Dashboard;
