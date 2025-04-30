import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator, TextInput, RefreshControl } from 'react-native';
import { Card, ListItem, Icon } from '@rneui/themed';
import { useFocusEffect } from '@react-navigation/native';
import apiService from '../services/apiService';

const MarketScreen = ({ navigation }) => {
  const [marketData, setMarketData] = useState([]); // Example: [{ symbol: 'AAPL', name: 'Apple Inc.', price: 175.50, change: 1.2 }, ...]
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredData, setFilteredData] = useState([]);

  // TODO: Replace with actual market data fetching logic
  const fetchMarketData = async () => {
    setError('');
    try {
      // This is a placeholder. The API spec doesn't have a general market overview endpoint.
      // We might need to fetch a predefined list or implement search differently.
      // For now, let's simulate fetching a few popular assets.
      const symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'BTC-USD', 'ETH-USD'];
      const promises = symbols.map(symbol => 
        apiService.getAssetPriceHistory(symbol, '1d', '1d') // Fetch minimal history to get latest price
          .then(res => {
            const latestData = res.data?.data?.[res.data.data.length - 1];
            const previousData = res.data?.data?.[res.data.data.length - 2];
            const change = previousData && latestData ? ((latestData.close - previousData.close) / previousData.close) * 100 : 0;
            return {
              symbol: res.data.symbol,
              name: res.data.name || symbol, // Use symbol if name is missing
              price: latestData?.close || 0,
              change: change,
              currency: res.data.currency || 'USD',
            };
          })
          .catch(err => {
            console.warn(`Failed to fetch market data for ${symbol}:`, err.message);
            return null; // Return null for failed requests
          })
      );
      const results = (await Promise.all(promises)).filter(data => data !== null);
      setMarketData(results);
      setFilteredData(results); // Initialize filtered data

    } catch (err) {
      console.error('Failed to fetch market data:', err);
      setError('Could not load market data.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      setLoading(true);
      fetchMarketData();
    }, [])
  );

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    setSearchQuery(''); // Reset search on refresh
    fetchMarketData();
  }, []);

  // Filter data based on search query
  useEffect(() => {
    if (searchQuery === '') {
      setFilteredData(marketData);
    } else {
      const lowerCaseQuery = searchQuery.toLowerCase();
      const filtered = marketData.filter(item => 
        item.symbol.toLowerCase().includes(lowerCaseQuery) || 
        item.name.toLowerCase().includes(lowerCaseQuery)
      );
      setFilteredData(filtered);
    }
  }, [searchQuery, marketData]);

  const renderItem = ({ item }) => (
    <ListItem
      bottomDivider
      onPress={() => navigation.navigate('AssetDetailMarket', { symbol: item.symbol })}
      containerStyle={styles.listItem}
    >
      <ListItem.Content>
        <ListItem.Title style={styles.itemSymbol}>{item.symbol} <Text style={styles.itemName}>({item.name})</Text></ListItem.Title>
        <ListItem.Subtitle style={styles.itemPrice}>
          {item.currency} {item.price?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </ListItem.Subtitle>
      </ListItem.Content>
      <View style={styles.changeContainer}>
        <Text style={[styles.itemChange, item.change >= 0 ? styles.positiveChange : styles.negativeChange]}>
          {item.change >= 0 ? '+' : ''}{item.change?.toFixed(2)}%
        </Text>
      </View>
      <ListItem.Chevron />
    </ListItem>
  );

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.searchInput}
        placeholder="Search assets (e.g., AAPL, Bitcoin)..."
        value={searchQuery}
        onChangeText={setSearchQuery}
        clearButtonMode="while-editing"
      />
      {loading ? (
        <View style={styles.centered}><ActivityIndicator size="large" color="#007AFF" /></View>
      ) : error && filteredData.length === 0 ? (
        <View style={styles.centered}>
          <Text style={styles.errorText}>{error}</Text>
          <Button title="Retry" onPress={fetchMarketData} />
        </View>
      ) : (
        <FlatList
          data={filteredData}
          renderItem={renderItem}
          keyExtractor={(item) => item.symbol}
          ListEmptyComponent={<View style={styles.centered}><Text>No assets found matching your search.</Text></View>}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
        />
      )}
    </View>
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
  searchInput: {
    height: 40,
    borderColor: 'gray',
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 10,
    margin: 10,
    backgroundColor: 'white',
  },
  listItem: {
    backgroundColor: 'white',
  },
  itemSymbol: {
    fontWeight: 'bold',
    fontSize: 16,
  },
  itemName: {
    fontWeight: 'normal',
    color: 'gray',
    fontSize: 14,
  },
  itemPrice: {
    color: '#333',
    fontSize: 14,
    marginTop: 2,
  },
  changeContainer: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 5,
    minWidth: 70, // Ensure minimum width for alignment
    alignItems: 'flex-end',
  },
  itemChange: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  positiveChange: {
    color: '#34C759', // Green
  },
  negativeChange: {
    color: '#FF3B30', // Red
  },
  errorText: {
    color: 'red',
    textAlign: 'center',
    marginBottom: 10,
  },
});

export default MarketScreen;

