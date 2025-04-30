import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, RefreshControl } from 'react-native';
import { Card, Divider } from '@rneui/themed';
import { useFocusEffect } from '@react-navigation/native';
import apiService from '../services/apiService';
import { LineChart } from 'react-native-chart-kit';
import { Dimensions } from 'react-native';

const screenWidth = Dimensions.get('window').width;

const AssetDetailScreen = ({ route, navigation }) => {
  const { symbol } = route.params;
  const [assetData, setAssetData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [chartPeriod, setChartPeriod] = useState('1y'); // Default period
  const [chartInterval, setChartInterval] = useState('1d'); // Default interval

  // Update header title
  useEffect(() => {
    navigation.setOptions({ title: symbol || 'Asset Details' });
  }, [symbol, navigation]);

  const fetchAssetDetails = async (period = chartPeriod, interval = chartInterval) => {
    setError('');
    try {
      // Fetch price history which includes basic info
      const response = await apiService.getAssetPriceHistory(symbol, period, interval);
      const historyData = response.data;
      
      if (!historyData || !historyData.data || historyData.data.length === 0) {
        setError('No data available for this asset.');
        setAssetData(null);
        return;
      }

      // Prepare chart data
      const chartLabels = historyData.data.map(d => {
        // Basic label formatting, might need refinement based on interval
        const date = new Date(d.timestamp);
        if (interval.includes('m') || interval.includes('h')) return date.toLocaleTimeString();
        return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
      });
      const chartDataset = historyData.data.map(d => d.close);

      // Reduce labels if too many for the chart
      const maxLabels = 6;
      let simplifiedLabels = chartLabels;
      if (chartLabels.length > maxLabels) {
        simplifiedLabels = chartLabels.filter((_, index) => index % Math.ceil(chartLabels.length / maxLabels) === 0);
      }

      setAssetData({
        ...historyData,
        chartData: {
          labels: simplifiedLabels,
          datasets: [
            {
              data: chartDataset,
              color: (opacity = 1) => `rgba(0, 122, 255, ${opacity})`, // Blue color
              strokeWidth: 2,
            },
          ],
          legend: [`${symbol} Price (${historyData.currency})`],
        },
        latestPrice: chartDataset[chartDataset.length - 1],
      });

    } catch (err) {
      console.error(`Failed to fetch asset details for ${symbol}:`, err);
      setError(`Could not load data for ${symbol}.`);
      setAssetData(null);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      setLoading(true);
      fetchAssetDetails();
    }, [symbol]) // Refetch if symbol changes
  );

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchAssetDetails();
  }, [symbol, chartPeriod, chartInterval]);

  // TODO: Add buttons/logic to change chartPeriod and chartInterval

  const chartConfig = {
    backgroundGradientFrom: '#ffffff',
    backgroundGradientTo: '#ffffff',
    decimalPlaces: 2,
    color: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
    style: {
      borderRadius: 16,
    },
    propsForDots: {
      r: '3',
      strokeWidth: '1',
      stroke: '#007AFF',
    },
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

  if (!assetData) {
    return <View style={styles.centered}><Text>No data available.</Text></View>;
  }

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <Card containerStyle={styles.card}>
        <View style={styles.headerRow}>
            <Text style={styles.assetName}>{assetData.name || symbol}</Text>
            <Text style={styles.assetSymbol}>({symbol})</Text>
        </View>
        <Text style={styles.currentPrice}>
            {assetData.currency} {assetData.latestPrice?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </Text>
        {/* Add 24h change if available from API */}
      </Card>

      <Card containerStyle={styles.card}>
        <Card.Title>Price Chart ({chartPeriod})</Card.Title>
        <Card.Divider />
        {assetData.chartData && assetData.chartData.datasets[0].data.length > 0 ? (
            <LineChart
                data={assetData.chartData}
                width={screenWidth - 40} // Adjust width based on card padding
                height={220}
                chartConfig={chartConfig}
                bezier // Optional: makes the line smooth
                style={styles.chart}
            />
        ) : (
            <Text style={styles.infoText}>Chart data not available.</Text>
        )}
        {/* Add period selector buttons here */}
      </Card>

      <Card containerStyle={styles.card}>
        <Card.Title>Statistics ({chartPeriod})</Card.Title>
        <Card.Divider />
        <View style={styles.statsRow}>
            <Text style={styles.statsLabel}>High:</Text>
            <Text style={styles.statsValue}>{assetData.summary?.high?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</Text>
        </View>
        <View style={styles.statsRow}>
            <Text style={styles.statsLabel}>Low:</Text>
            <Text style={styles.statsValue}>{assetData.summary?.low?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</Text>
        </View>
        <View style={styles.statsRow}>
            <Text style={styles.statsLabel}>Average:</Text>
            <Text style={styles.statsValue}>{assetData.summary?.average?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</Text>
        </View>
        <View style={styles.statsRow}>
            <Text style={styles.statsLabel}>Change:</Text>
            <Text style={[styles.statsValue, assetData.summary?.change_percentage >= 0 ? styles.positive : styles.negative]}>
                {assetData.summary?.change_percentage?.toFixed(2)}%
            </Text>
        </View>
        {/* Add Volume if available */}
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
    padding: 20,
  },
  card: {
    borderRadius: 10,
    marginBottom: 15,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
    justifyContent: 'center',
    marginBottom: 5,
  },
  assetName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginRight: 5,
  },
  assetSymbol: {
    fontSize: 18,
    color: 'gray',
  },
  currentPrice: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 10,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 5,
  },
  statsLabel: {
    fontSize: 16,
    color: '#555',
  },
  statsValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  positive: {
    color: '#34C759',
  },
  negative: {
    color: '#FF3B30',
  },
  errorText: {
    color: 'red',
    textAlign: 'center',
    marginBottom: 10,
  },
  infoText: {
      textAlign: 'center',
      color: 'gray',
      paddingVertical: 20,
  }
});

export default AssetDetailScreen;

