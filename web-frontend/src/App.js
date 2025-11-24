import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';

// Import the enhanced components
import MainLayout from './components/MainLayout';
import Dashboard from './pages/Dashboard';
import PortfolioOptimization from './pages/PortfolioOptimization';
import RiskAnalysis from './pages/RiskAnalysis';
import Settings from './pages/Settings';

// A simple 404 page
const NotFound = () => (
    <Box sx={{ p: 3 }}>
        <h1 style={{ color: 'red' }}>404 - Page Not Found</h1>
        <p>The page you are looking for does not exist.</p>
    </Box>
);

const App = () => {
    return (
        <MainLayout>
            <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/optimize" element={<PortfolioOptimization />} />
                <Route path="/risk" element={<RiskAnalysis />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="*" element={<NotFound />} />
            </Routes>
        </MainLayout>
    );
};

export default App;
