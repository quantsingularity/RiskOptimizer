import React, { useState } from 'react';
import { Button, Slider, Box, Typography } from '@material-ui/core';

export default function OptimizationTool() {
    const [riskTolerance, setRiskTolerance] = useState(5);
    const [result, setResult] = useState(null);

    const optimize = async () => {
        const response = await fetch('/api/optimize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                historical_data: {
                    /* market data */
                },
            }),
        });
        setResult(await response.json());
    };

    return (
        <Box p={3}>
            <Typography variant="h6">Portfolio Optimization</Typography>
            <Typography>Risk Tolerance Level</Typography>
            <Slider
                value={riskTolerance}
                onChange={(e, v) => setRiskTolerance(v)}
                min={1}
                max={10}
                step={1}
                marks
            />
            <Button variant="contained" color="primary" onClick={optimize}>
                Optimize Portfolio
            </Button>

            {result && (
                <Box mt={3}>
                    <Typography variant="h6">Optimized Allocation</Typography>
                    <pre>{JSON.stringify(result.optimized_allocation, null, 2)}</pre>
                    <Typography>Expected Return: {result.performance_metrics[0]}</Typography>
                    <Typography>Volatility: {result.performance_metrics[1]}</Typography>
                    <Typography>Sharpe Ratio: {result.performance_metrics[2]}</Typography>
                </Box>
            )}
        </Box>
    );
}
