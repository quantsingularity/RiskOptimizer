import React from 'react';
import { Box, Typography, Card, CardContent, Grid } from '@mui/material';
import { PieChart } from '@mui/x-charts/PieChart';

const AssetAllocation = ({ allocation }) => {
  // Default values if allocation isn't provided
  const defaultAllocation = [
    { name: 'Stocks', value: 60, color: '#2196f3' },
    { name: 'Bonds', value: 20, color: '#4caf50' },
    { name: 'Crypto', value: 10, color: '#ff9800' },
    { name: 'Cash', value: 5, color: '#9e9e9e' },
    { name: 'Gold', value: 5, color: '#ffc107' }
  ];

  const data = allocation || defaultAllocation;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Asset Allocation
        </Typography>
        
        <Box sx={{ height: 300, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <PieChart
            series={[
              {
                data,
                highlightScope: { faded: 'global', highlighted: 'item' },
                faded: { innerRadius: 30, additionalRadius: -30, color: 'gray' },
                innerRadius: 30,
                paddingAngle: 2,
                cornerRadius: 4,
              },
            ]}
            height={250}
            margin={{ top: 0, bottom: 0, left: 0, right: 0 }}
            slotProps={{
              legend: { hidden: true },
            }}
          />
        </Box>
        
        <Grid container spacing={1} sx={{ mt: 1 }}>
          {data.map((item, index) => (
            <Grid item xs={6} sm={4} key={index}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Box
                  sx={{
                    width: 12,
                    height: 12,
                    borderRadius: '50%',
                    backgroundColor: item.color,
                    mr: 1
                  }}
                />
                <Typography variant="body2">
                  {item.name}: {item.value}%
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
      </CardContent>
    </Card>
  );
};

export default AssetAllocation;
