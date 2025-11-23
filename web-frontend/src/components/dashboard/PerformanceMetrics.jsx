import React from 'react';
import { Box, Typography, Card, CardContent, Grid } from '@mui/material';

const PerformanceMetrics = ({ metrics }) => {
    // Default values if metrics aren't provided
    const defaultMetrics = {
        dailyReturn: '+1.2%',
        weeklyReturn: '+3.5%',
        monthlyReturn: '+8.7%',
        yearlyReturn: '+24.3%',
        sharpeRatio: '1.87',
        volatility: '14.2%',
    };

    const data = metrics || defaultMetrics;

    return (
        <Card>
            <CardContent>
                <Typography variant="h6" gutterBottom>
                    Performance Metrics
                </Typography>

                <Grid container spacing={2} sx={{ mt: 1 }}>
                    <Grid item xs={6} sm={4}>
                        <Typography variant="body2" color="text.secondary">
                            Daily Return
                        </Typography>
                        <Typography variant="body1" color="success.main" sx={{ fontWeight: 500 }}>
                            {data.dailyReturn}
                        </Typography>
                    </Grid>

                    <Grid item xs={6} sm={4}>
                        <Typography variant="body2" color="text.secondary">
                            Weekly Return
                        </Typography>
                        <Typography variant="body1" color="success.main" sx={{ fontWeight: 500 }}>
                            {data.weeklyReturn}
                        </Typography>
                    </Grid>

                    <Grid item xs={6} sm={4}>
                        <Typography variant="body2" color="text.secondary">
                            Monthly Return
                        </Typography>
                        <Typography variant="body1" color="success.main" sx={{ fontWeight: 500 }}>
                            {data.monthlyReturn}
                        </Typography>
                    </Grid>

                    <Grid item xs={6} sm={4}>
                        <Typography variant="body2" color="text.secondary">
                            Yearly Return
                        </Typography>
                        <Typography variant="body1" color="success.main" sx={{ fontWeight: 500 }}>
                            {data.yearlyReturn}
                        </Typography>
                    </Grid>

                    <Grid item xs={6} sm={4}>
                        <Typography variant="body2" color="text.secondary">
                            Sharpe Ratio
                        </Typography>
                        <Typography variant="body1" sx={{ fontWeight: 500 }}>
                            {data.sharpeRatio}
                        </Typography>
                    </Grid>

                    <Grid item xs={6} sm={4}>
                        <Typography variant="body2" color="text.secondary">
                            Volatility
                        </Typography>
                        <Typography variant="body1" sx={{ fontWeight: 500 }}>
                            {data.volatility}
                        </Typography>
                    </Grid>
                </Grid>
            </CardContent>
        </Card>
    );
};

export default PerformanceMetrics;
