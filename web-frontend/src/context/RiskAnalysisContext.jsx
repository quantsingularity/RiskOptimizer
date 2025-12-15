import React, { createContext, useContext, useState } from 'react';
import apiService from '../services/apiService';

// Create context
const RiskAnalysisContext = createContext();

// Provider component
export const RiskAnalysisProvider = ({ children }) => {
    const [riskMetrics, setRiskMetrics] = useState(null);
    const [varData, setVarData] = useState(null);
    const [stressTestResults, setStressTestResults] = useState(null);
    const [correlationData, setCorrelationData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Calculate Value at Risk
    const calculateVaR = async (params) => {
        setLoading(true);
        setError(null);
        try {
            const response = await apiService.risk.calculateVaR(params);
            if (response.status === 'success') {
                setVarData(response.data);
                return response.data;
            } else {
                setError(response.message || 'Failed to calculate VaR');
                return null;
            }
        } catch (err) {
            setError(err.message || 'An error occurred while calculating VaR');
            console.error('VaR calculation error:', err);
            return null;
        } finally {
            setLoading(false);
        }
    };

    // Run stress test
    const runStressTest = async (params) => {
        setLoading(true);
        setError(null);
        try {
            const response = await apiService.risk.stressTest(params);
            if (response.status === 'success') {
                setStressTestResults(response.data);
                return response.data;
            } else {
                setError(response.message || 'Failed to run stress test');
                return null;
            }
        } catch (err) {
            setError(err.message || 'An error occurred while running stress test');
            console.error('Stress test error:', err);
            return null;
        } finally {
            setLoading(false);
        }
    };

    // Analyze correlation
    const analyzeCorrelation = async (params) => {
        setLoading(true);
        setError(null);
        try {
            const response = await apiService.risk.correlationAnalysis(params);
            if (response.status === 'success') {
                setCorrelationData(response.data);
                return response.data;
            } else {
                setError(response.message || 'Failed to analyze correlation');
                return null;
            }
        } catch (err) {
            setError(err.message || 'An error occurred while analyzing correlation');
            console.error('Correlation analysis error:', err);
            return null;
        } finally {
            setLoading(false);
        }
    };

    // Fetch risk metrics for a portfolio
    const fetchRiskMetrics = async (portfolioId) => {
        setLoading(true);
        setError(null);
        try {
            const response = await apiService.risk.getMetrics(portfolioId);
            if (response.status === 'success') {
                setRiskMetrics(response.data);
                return response.data;
            } else {
                setError(response.message || 'Failed to fetch risk metrics');
                return null;
            }
        } catch (err) {
            setError(err.message || 'An error occurred while fetching risk metrics');
            console.error('Risk metrics fetch error:', err);
            return null;
        } finally {
            setLoading(false);
        }
    };

    // Clear all risk data
    const clearRiskData = () => {
        setRiskMetrics(null);
        setVarData(null);
        setStressTestResults(null);
        setCorrelationData(null);
        setError(null);
    };

    // Context value
    const value = {
        riskMetrics,
        varData,
        stressTestResults,
        correlationData,
        loading,
        error,
        calculateVaR,
        runStressTest,
        analyzeCorrelation,
        fetchRiskMetrics,
        clearRiskData,
    };

    return <RiskAnalysisContext.Provider value={value}>{children}</RiskAnalysisContext.Provider>;
};

// Custom hook to use the risk analysis context
export const useRiskAnalysis = () => {
    const context = useContext(RiskAnalysisContext);
    if (context === undefined) {
        throw new Error('useRiskAnalysis must be used within a RiskAnalysisProvider');
    }
    return context;
};

export default RiskAnalysisContext;
