import React from "react";
import { Box, Typography, Card, CardContent } from "@mui/material";

const PortfolioSummary = ({ portfolioData }) => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Portfolio Summary
        </Typography>
        <Box sx={{ mt: 2 }}>
          {portfolioData ? (
            <Box>
              <Typography variant="body2" color="text.secondary">
                Total Assets: {portfolioData.assets?.length || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Value: ${portfolioData.totalValue || "0.00"}
              </Typography>
            </Box>
          ) : (
            <Typography variant="body2" color="text.secondary">
              No portfolio data available
            </Typography>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default PortfolioSummary;
