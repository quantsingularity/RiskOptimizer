import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, RefreshControl, Button } from 'react-native';
import { Card, Divider } from '@rneui/themed';
import { useFocusEffect } from '@react-navigation/native';
import apiService from '../services/apiService';
// Import chart component later if needed for risk contribution visualization

const RiskAnalysisScreen = ({ route, navigation }) => {
  const { portfolioId } = route.params;
  const [riskMetrics, setRiskMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');

  // Update header title (optional, could be set in PortfolioStack)
  useEffect(() => {
    navigation.setOptions({ title: 'Risk Analysis' });
  }, [navigation]);

  const fetchRiskMetrics = async () => {
    setError('');
    try {
      const response = await apiService.getRiskMetrics(portfolioId);
      setRiskMetrics(response.data);
    } catch (err) {
      console.error('Failed to fetch risk metrics:', err);
      setError('Could not load risk metrics.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      setLoading(true);
      fetchRiskMetrics();
    }, [portfolioId])
  );

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchRiskMetrics();
  }, [portfolioId]);

  const renderMetric = (label, value, precision = 2) => {
    const displayValue = typeof value === 'number' ? value.toFixed(precision) : (value || 'N/A');
    return (
      <View style={styles.metricRow} key={label}>
        <Text style={styles.metricLabel}>{label}:</Text>
        <Text style={styles.metricValue}>{displayValue}</Text>
      </View>
    );
  };

  if (loading) {
    return <View style={styles.centered}><ActivityIndicator size="large" color="#007AFF" /></View>;
  }

  if (error) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>{error}</Text>
        <Button title="Retry" onPress={onRefresh} />
      </View>
    );
  }

  if (!riskMetrics) {
    return <View style={styles.centered}><Text>No risk metrics available.</Text></View>;
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <Card containerStyle={styles.card}>
        <Card.Title>Key Risk Metrics</Card.Title>
        <Card.Divider />
        {renderMetric('Volatility', riskMetrics.volatility)}
        {renderMetric('Sharpe Ratio', riskMetrics.sharpe_ratio)}
        {renderMetric('Sortino Ratio', riskMetrics.sortino_ratio)}
        {renderMetric('Max Drawdown', riskMetrics.max_drawdown)}
        {renderMetric('Value at Risk (95%)', riskMetrics.var_95)}
        {renderMetric('Value at Risk (99%)', riskMetrics.var_99)}
        {renderMetric('Beta', riskMetrics.beta)}
        {renderMetric('Alpha', riskMetrics.alpha)}
        {renderMetric('R-Squared', riskMetrics.r_squared)}
      </Card>

      {riskMetrics.risk_contribution && riskMetrics.risk_contribution.length > 0 && (
        <Card containerStyle={styles.card}>
          <Card.Title>Risk Contribution by Asset</Card.Title>
          <Card.Divider />
          {/* Consider adding a Pie chart here */}
          {riskMetrics.risk_contribution.map((item, index) => (
            <View style={styles.metricRow} key={index}>
              <Text style={styles.metricLabel}>{item.symbol}:</Text>
              <Text style={styles.metricValue}>{(item.contribution * 100).toFixed(2)}%</Text>
            </View>
          ))}
        </Card>
      )}

    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  card: {
    borderRadius: 10,
    marginBottom: 15,
  },
  metricRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    marginHorizontal: 10, // Add some horizontal margin within the card
  },
  metricLabel: {
    fontSize: 16,
    color: '#555',
  },
  metricValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  errorText: {
    color: 'red',
    textAlign: 'center',
    marginBottom: 10,
  },
});

export default RiskAnalysisScreen;
