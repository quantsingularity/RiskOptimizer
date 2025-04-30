import React from 'react';
import { Box, Typography, Link } from '@mui/material';

const Footer = () => {
  return (
    <Box
      component="footer"
      sx={{
        py: 3,
        px: 2,
        mt: 'auto',
        backgroundColor: 'background.paper',
        borderTop: '1px solid rgba(255, 255, 255, 0.1)',
      }}
    >
      <Typography variant="body2" color="text.secondary" align="center">
        {'© '}
        <Link color="inherit" href="#">
          RiskOptimizer
        </Link>{' '}
        {new Date().getFullYear()}
        {' | AI-Powered Portfolio Optimization Tool'}
      </Typography>
    </Box>
  );
};

export default Footer;
