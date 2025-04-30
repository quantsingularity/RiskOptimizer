import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, FlatList, ActivityIndicator, RefreshControl, TouchableOpacity } from 'react-native';
import { Card, Button, Icon, ListItem, Divider } from '@rneui/themed';
import { useFocusEffect } from '@react-navigation/native';
import apiService from '../services/apiService';

const PortfolioDetailScreen = ({ route, navigation }) => {
  const { portfolioId, portfolioName } = route.params;
  const [portfolioDetails, setPortfolioDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');

  // Update header title
  useEffect(() => {
    navigation.setOptions({ title: portfolioName || 'Portfolio Details' });
  }, [portfolioName, navigation]);

  const fetchPortfolioDetails = async () => {
    setError('');
    try {
      const response = await apiService.getPortfolioDetails(portfolioId);
      setPortfolioDetails(response.data);
    } catch (err) {
      console.error('Failed to fetch portfolio details:', err);
      setError('Could not load portfolio details.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // Fetch data when the screen comes into focus or portfolioId changes
  useFocusEffect(
    useCallback(() => {
      setLoading(true);
      fetchPortfolioDetails();
    }, [portfolioId])
  );

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchPortfolioDetails();
  }, [portfolioId]);

  const renderAssetItem = ({ item }) => (
    <ListItem
      bottomDivider
      onPress={() => navigation.navigate('AssetDetailPortfolio', { symbol: item.symbol })}
      containerStyle={styles.assetItem}
    >
      <ListItem.Content>
        <ListItem.Title style={styles.assetSymbol}>{item.symbol} <Text style={styles.assetName}>({item.name})</Text></ListItem.Title>
        <ListItem.Subtitle style={styles.assetDetails}>
          Qty: {item.quantity} | Value: {portfolioDetails?.currency} {item.value?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </ListItem.Subtitle>
        <ListItem.Subtitle style={styles.assetDetails}>
          Allocation: {item.allocation_percentage?.toFixed(2)}% | Perf: {item.performance?.toFixed(2)}%
        </ListItem.Subtitle>
      </ListItem.Content>
      <ListItem.Chevron />
    </ListItem>
  );

  if (loading) {
    return <View style={styles.centered}><ActivityIndicator size="large" color="#007AFF" /></View>;
  }

  if (error) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>{error}</Text>
        <Button title="Retry" onPress={fetchPortfolioDetails} />
      </View>
    );
  }

  if (!portfolioDetails) {
    return <View style={styles.centered}><Text>No portfolio data found.</Text></View>;
  }

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <Card containerStyle={styles.summaryCard}>
        <Text style={styles.summaryLabel}>Total Value</Text>
        <Text style={styles.summaryValue}>
          {portfolioDetails.currency} {portfolioDetails.total_value?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </Text>
        <Text style={styles.summaryRisk}>Risk Score: {portfolioDetails.risk_score?.toFixed(2) || 'N/A'}</Text>
        {portfolioDetails.description ? <Text style={styles.description}>{portfolioDetails.description}</Text> : null}
      </Card>

      {/* Performance Section (Placeholder/Link) */}
      <TouchableOpacity onPress={() => alert('Navigate to Performance Chart')} style={styles.sectionLink}>
        <Icon name="chart-timeline-variant" type="material-community" color="#007AFF" />
        <Text style={styles.sectionLinkText}>View Performance Details</Text>
        <Icon name="chevron-right" type="material-community" color="#C7C7CC" />
      </TouchableOpacity>
      <Divider style={styles.divider} />

      {/* Risk Analysis Section (Placeholder/Link) */}
      <TouchableOpacity onPress={() => navigation.navigate('RiskAnalysis', { portfolioId: portfolioId })} style={styles.sectionLink}>
        <Icon name="shield-half-full" type="material-community" color="#007AFF" />
        <Text style={styles.sectionLinkText}>View Risk Analysis</Text>
        <Icon name="chevron-right" type="material-community" color="#C7C7CC" />
      </TouchableOpacity>
      <Divider style={styles.divider} />

      {/* Transaction History Section (Placeholder/Link) */}
      <TouchableOpacity onPress={() => navigation.navigate('TransactionHistory', { portfolioId: portfolioId })} style={styles.sectionLink}>
        <Icon name="receipt" type="material-community" color="#007AFF" />
        <Text style={styles.sectionLinkText}>View Transaction History</Text>
        <Icon name="chevron-right" type="material-community" color="#C7C7CC" />
      </TouchableOpacity>
      <Divider style={styles.divider} />

      <Card containerStyle={styles.assetsCard}>
        <Card.Title>Assets</Card.Title>
        <Card.Divider />
        {portfolioDetails.assets && portfolioDetails.assets.length > 0 ? (
          <FlatList
            data={portfolioDetails.assets}
            renderItem={renderAssetItem}
            keyExtractor={(item) => item.id}
            scrollEnabled={false} // Disable scrolling within the card if ScrollView is parent
          />
        ) : (
          <Text style={styles.noAssetsText}>No assets in this portfolio yet.</Text>
        )}
        <Button
          icon={<Icon name="plus" type="material-community" color="white" />}
          title="Add Asset"
          buttonStyle={styles.addAssetButton}
          onPress={() => navigation.navigate('AddAsset', { portfolioId: portfolioId })}
        />
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
  summaryCard: {
    borderRadius: 10,
    marginBottom: 10,
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
  summaryRisk: {
    fontSize: 16,
    color: 'gray',
    marginTop: 5,
  },
  description: {
    fontSize: 14,
    color: '#555',
    marginTop: 10,
    textAlign: 'center',
  },
  assetsCard: {
    borderRadius: 10,
    marginBottom: 15,
  },
  assetItem: {
    paddingVertical: 10,
  },
  assetSymbol: {
    fontWeight: 'bold',
    fontSize: 16,
  },
  assetName: {
    fontWeight: 'normal',
    color: 'gray',
    fontSize: 14,
  },
  assetDetails: {
    color: '#555',
    fontSize: 14,
    marginTop: 2,
  },
  addAssetButton: {
    backgroundColor: '#34C759', // Green
    marginTop: 15,
    borderRadius: 8,
  },
  noAssetsText: {
    textAlign: 'center',
    paddingVertical: 20,
    color: 'gray',
  },
  sectionLink: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'white',
    paddingVertical: 15,
    paddingHorizontal: 15,
  },
  sectionLinkText: {
    flex: 1,
    marginLeft: 15,
    fontSize: 16,
    color: '#333',
  },
  divider: {
    backgroundColor: '#EFEFF4',
  },
  errorText: {
    color: 'red',
    textAlign: 'center',
    marginBottom: 10,
  },
});

export default PortfolioDetailScreen;

