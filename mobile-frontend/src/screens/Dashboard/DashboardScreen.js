import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import { Card, Button, Icon } from '@rneui/themed';
import { useAuth } from '../context/AuthContext';
import apiService from '../services/apiService';
// Import chart component later
// import PerformanceChart from '../components/dashboard/PerformanceChart';

const DashboardScreen = ({ navigation }) => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError('');
      try {
        // Fetch necessary data for dashboard - API might need a dedicated dashboard endpoint
        // For now, let's assume we fetch portfolios and calculate total value
        const portfolioResponse = await apiService.getPortfolios();
        const portfolios = portfolioResponse.data.portfolios || [];
        
        let totalValue = 0;
        portfolios.forEach(p => {
          totalValue += p.total_value || 0;
        });

        // Placeholder for other dashboard metrics
        setDashboardData({
          totalPortfolioValue: totalValue,
          currency: portfolios.length > 0 ? portfolios[0].currency : 'USD',
          overallChange: 1.5, // Placeholder
          topPerformer: { symbol: 'AAPL', change: 5.2 }, // Placeholder
          riskScore: 0.7, // Placeholder
        });

      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setError('Could not load dashboard data.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <View style={styles.centered}><ActivityIndicator size="large" color="#007AFF" /></View>;
  }

  if (error) {
    return <View style={styles.centered}><Text style={styles.errorText}>{error}</Text></View>;
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.welcomeText}>Welcome, {user?.name || 'User'}!</Text>

      <Card containerStyle={styles.summaryCard}>
        <Text style={styles.summaryLabel}>Total Portfolio Value</Text>
        <Text style={styles.summaryValue}>
          {dashboardData?.currency} {dashboardData?.totalPortfolioValue?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}
        </Text>
        {/* Add overall change indicator here */}
      </Card>

      {/* Placeholder for Performance Chart */}
      {/* <Card containerStyle={styles.chartCard}>
        <Card.Title>Overall Performance</Card.Title>
        <Card.Divider />
        <PerformanceChart /> 
      </Card> */}

      <View style={styles.quickActionsContainer}>
        <Button 
          title="View Portfolios" 
          icon={<Icon name="briefcase-outline" type="material-community" color="white" />} 
          buttonStyle={styles.actionButton}
          onPress={() => navigation.navigate('Portfolios')}
        />
        <Button 
          title="Optimize" 
          icon={<Icon name="chart-line" type="material-community" color="white" />} 
          buttonStyle={[styles.actionButton, styles.optimizeButton]}
          onPress={() => navigation.navigate('Optimize')}
        />
      </View>

      <Card containerStyle={styles.metricCard}>
        <Card.Title>Quick Metrics</Card.Title>
        <Card.Divider />
        <View style={styles.metricRow}>
          <Text style={styles.metricLabel}>Overall Risk Score:</Text>
          <Text style={styles.metricValue}>{dashboardData?.riskScore?.toFixed(2) || 'N/A'}</Text>
        </View>
        <View style={styles.metricRow}>
          <Text style={styles.metricLabel}>Top Performer (24h):</Text>
          <Text style={styles.metricValue}>{dashboardData?.topPerformer?.symbol || 'N/A'} (+{dashboardData?.topPerformer?.change || 0}%)</Text>
        </View>
        {/* Add more metrics as needed */}
      </Card>

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
    backgroundColor: '#f5f5f5',
  },
  welcomeText: {
    fontSize: 24,
    fontWeight: 'bold',
    margin: 20,
    color: '#333',
  },
  summaryCard: {
    borderRadius: 10,
    marginBottom: 15,
    alignItems: 'center',
  },
  summaryLabel: {
    fontSize: 16,
    color: 'gray',
    marginBottom: 5,
  },
  summaryValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
  },
  chartCard: {
    borderRadius: 10,
    marginBottom: 15,
  },
  quickActionsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginHorizontal: 15,
    marginBottom: 15,
  },
  actionButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingVertical: 10,
    paddingHorizontal: 15,
    flex: 1,
    marginHorizontal: 5,
  },
  optimizeButton: {
    backgroundColor: '#34C759', // Green color for optimize
  },
  metricCard: {
    borderRadius: 10,
    marginBottom: 15,
  },
  metricRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
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
    fontSize: 16,
  },
});

export default DashboardScreen;

