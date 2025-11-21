import React from "react";
import { Box, Typography, Card, CardContent, Grid } from "@mui/material";
import { LineChart } from "@mui/x-charts/LineChart";

const PerformanceChart = ({ performanceData }) => {
  // Default values if performance data isn't provided
  const defaultData = Array.from({ length: 30 }, (_, i) => ({
    date: `2025-${String((i % 12) + 1).padStart(2, "0")}-${String((i % 28) + 1).padStart(2, "0")}`,
    value: 100000 + Math.random() * 30000,
  }));

  const data = performanceData || defaultData;

  // Format data for chart
  const xLabels = data.slice(-30).map((item) => item.date);
  const yValues = data.slice(-30).map((item) => item.value);

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Portfolio Performance
        </Typography>

        <Box sx={{ height: 300, mt: 2 }}>
          <LineChart
            series={[
              {
                data: yValues,
                area: true,
                showMark: false,
                color: "#2196f3",
              },
            ]}
            xAxis={[
              {
                data: xLabels,
                scaleType: "point",
                tickLabelStyle: {
                  fontSize: 10,
                  angle: -45,
                  textAnchor: "end",
                },
                tickNumber: 5,
              },
            ]}
            height={280}
            margin={{ top: 10, bottom: 60, left: 40, right: 10 }}
          />
        </Box>
      </CardContent>
    </Card>
  );
};

export default PerformanceChart;
