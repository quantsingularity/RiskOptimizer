import React, { createContext, useContext, useState } from 'react';
import apiService from '../services/apiService';

// Create context
const RiskAnalysisContext = createContext();

// Provider component
export const RiskAnalysisProvider = ({ children }) => {
  const [riskMetrics, setRiskMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Calculate Value at Risk
  const calculateVaR = async (returns, confidence = 0.95) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiService.calculateVaR(returns, confidence);
      if (response.status === 'success') {
        const updatedMetrics = {
          ...riskMetrics,
          valueAtRisk: response.value_at_risk
        };
        setRiskMetrics(updatedMetrics);
        return response;
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
  const runStressTest = async (portfolioData, scenario) => {
    setLoading(true);
    setError(null);
    try {
      // This would be connected to a real API endpoint in a production app
      // For now, we'll simulate a response
      const simulatedResponse = {
        status: 'success',
        stress_test_results: {
          scenario: scenario,
          estimated_loss: -32.8,
          impact_by_asset_class: {
            equities: -42.5,
            bonds: 5.2,
            crypto: -60.8,
            gold: 12.3
          }
        }
      };
      
      // Update risk metrics with stress test results
      const updatedMetrics = {
        ...riskMetrics,
        stressTest: simulatedResponse.stress_test_results
      };
      setRiskMetrics(updatedMetrics);
      
      return simulatedResponse;
    } catch (err) {
      setError(err.message || 'An error occurred while running stress test');
      console.error('Stress test error:', err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Context value
  const value = {
    riskMetrics,
    loading,
    error,
    calculateVaR,
    runStressTest,
  };

  return (
    <RiskAnalysisContext.Provider value={value}>
      {children}
    </RiskAnalysisContext.Provider>
  );
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
