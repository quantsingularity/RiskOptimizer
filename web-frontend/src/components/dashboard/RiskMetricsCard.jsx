import React from 'react';
import { Box, Typography, Card, CardContent, Grid } from '@mui/material';

const RiskMetricsCard = ({ riskMetrics }) => {
    // Default values if risk metrics aren't provided
    const defaultMetrics = {
        valueAtRisk: '$4,532.12',
        maxDrawdown: '-12.4%',
        volatility: '14.2%',
        beta: '0.85',
    };

    const data = riskMetrics || defaultMetrics;

    return (
        <Card>
            <CardContent>
                <Typography variant="h6" gutterBottom>
                    Risk Metrics
                </Typography>

                <Grid container spacing={2} sx={{ mt: 1 }}>
                    <Grid item xs={6} sm={3}>
                        <Typography variant="body2" color="text.secondary">
                            Value at Risk (95%)
                        </Typography>
                        <Typography variant="body1" color="error.main" sx={{ fontWeight: 500 }}>
                            {data.valueAtRisk}
                        </Typography>
                    </Grid>

                    <Grid item xs={6} sm={3}>
                        <Typography variant="body2" color="text.secondary">
                            Max Drawdown
                        </Typography>
                        <Typography variant="body1" color="error.main" sx={{ fontWeight: 500 }}>
                            {data.maxDrawdown}
                        </Typography>
                    </Grid>

                    <Grid item xs={6} sm={3}>
                        <Typography variant="body2" color="text.secondary">
                            Volatility
                        </Typography>
                        <Typography variant="body1" sx={{ fontWeight: 500 }}>
                            {data.volatility}
                        </Typography>
                    </Grid>

                    <Grid item xs={6} sm={3}>
                        <Typography variant="body2" color="text.secondary">
                            Beta
                        </Typography>
                        <Typography variant="body1" sx={{ fontWeight: 500 }}>
                            {data.beta}
                        </Typography>
                    </Grid>
                </Grid>
            </CardContent>
        </Card>
    );
};

export default RiskMetricsCard;
