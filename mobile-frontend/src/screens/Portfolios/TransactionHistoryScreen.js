import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator, RefreshControl, Linking, Alert, Button } from 'react-native';
import { Card, ListItem, Icon } from '@rneui/themed';
import { useFocusEffect } from '@react-navigation/native';
import apiService from '../services/apiService';

const TransactionHistoryScreen = ({ route, navigation }) => {
  const { portfolioId } = route.params;
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [verificationStatus, setVerificationStatus] = useState(null);

  // Update header title (optional)
  useEffect(() => {
    navigation.setOptions({ title: 'Transaction History' });
  }, [navigation]);

  const fetchHistory = async () => {
    setError('');
    try {
      const [historyResponse, verificationResponse] = await Promise.all([
        apiService.getTransactionHistory(portfolioId),
        apiService.verifyPortfolioIntegrity(portfolioId), // Fetch verification status too
      ]);
      setTransactions(historyResponse.data.transactions || []);
      setVerificationStatus(verificationResponse.data);
    } catch (err) {
      console.error('Failed to fetch transaction history or verification:', err);
      setError('Could not load transaction history.');
      // Don't clear verification status on history error
      if (!verificationStatus) {
          try {
              const verificationResponse = await apiService.verifyPortfolioIntegrity(portfolioId);
              setVerificationStatus(verificationResponse.data);
          } catch (verifyErr) {
              console.error('Failed to fetch verification status:', verifyErr);
              // Keep verificationStatus as null or previous state
          }
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      setLoading(true);
      fetchHistory();
    }, [portfolioId])
  );

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchHistory();
  }, [portfolioId]);

  const openTxInExplorer = (txHash) => {
    // Basic example for Etherscan - adapt based on actual blockchain used
    if (!verificationStatus?.blockchain) {
        Alert.alert('Cannot Open', 'Blockchain information not available.');
        return;
    }
    let explorerUrl;
    if (verificationStatus.blockchain.toLowerCase() === 'ethereum') {
        explorerUrl = `https://etherscan.io/tx/${txHash}`;
    } else if (verificationStatus.blockchain.toLowerCase() === 'solana') {
        explorerUrl = `https://explorer.solana.com/tx/${txHash}`;
    } else {
        Alert.alert('Unsupported Blockchain', `Cannot open explorer for ${verificationStatus.blockchain}.`);
        return;
    }

    Linking.canOpenURL(explorerUrl).then(supported => {
      if (supported) {
        Linking.openURL(explorerUrl);
      } else {
        Alert.alert('Cannot Open URL', `Don't know how to open this URL: ${explorerUrl}`);
      }
    });
  };

  const renderItem = ({ item }) => (
    <ListItem
      bottomDivider
      onPress={() => item.tx_hash && openTxInExplorer(item.tx_hash)}
      containerStyle={styles.listItem}
    >
      <Icon
        name={item.action === 'buy' ? 'arrow-bottom-left-thick' : 'arrow-top-right-thick'}
        type="material-community"
        color={item.action === 'buy' ? '#34C759' : '#FF3B30'}
      />
      <ListItem.Content>
        <ListItem.Title style={styles.itemTitle}>
          {item.action.toUpperCase()} {item.symbol} ({item.quantity})
        </ListItem.Title>
        <ListItem.Subtitle style={styles.itemSubtitle}>
          {new Date(item.timestamp).toLocaleString()} | Value: {item.value?.toFixed(2)}
        </ListItem.Subtitle>
        {item.tx_hash && <ListItem.Subtitle style={styles.txHash}>Hash: {item.tx_hash.substring(0, 10)}...</ListItem.Subtitle>}
      </ListItem.Content>
      <Text style={[styles.status, item.status === 'confirmed' ? styles.confirmed : styles.pending]}>
        {item.status}
      </Text>
      {item.tx_hash && <ListItem.Chevron />}
    </ListItem>
  );

  const renderHeader = () => (
    verificationStatus ? (
        <Card containerStyle={styles.verificationCard}>
            <View style={styles.verificationRow}>
                <Icon name={verificationStatus.verified ? 'check-circle-outline' : 'alert-circle-outline'} type="material-community" color={verificationStatus.verified ? '#34C759' : '#FF9500'} size={20}/>
                <Text style={[styles.verificationText, verificationStatus.verified ? styles.verified : styles.notVerified]}>
                    Portfolio Integrity: {verificationStatus.verified ? 'Verified' : 'Verification Failed or Pending'}
                </Text>
            </View>
            <Text style={styles.verificationDetails}>Blockchain: {verificationStatus.blockchain || 'N/A'} | Last Check: {verificationStatus.last_verification ? new Date(verificationStatus.last_verification).toLocaleTimeString() : 'N/A'}</Text>
        </Card>
    ) : null
  );

  if (loading) {
    return <View style={styles.centered}><ActivityIndicator size="large" color="#007AFF" /></View>;
  }

  return (
    <View style={styles.container}>
      {error && transactions.length === 0 ? (
        <View style={styles.centered}>
          <Text style={styles.errorText}>{error}</Text>
          <Button title="Retry" onPress={onRefresh} />
        </View>
      ) : (
        <FlatList
          data={transactions}
          renderItem={renderItem}
          keyExtractor={(item, index) => item.tx_hash || `tx-${index}`}
          ListHeaderComponent={renderHeader}
          ListEmptyComponent={<View style={styles.centered}><Text>No transactions found for this portfolio.</Text></View>}
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
  listItem: {
    backgroundColor: 'white',
  },
  itemTitle: {
    fontWeight: 'bold',
    fontSize: 16,
  },
  itemSubtitle: {
    color: 'gray',
    fontSize: 13,
    marginTop: 2,
  },
  txHash: {
      color: '#007AFF',
      fontSize: 12,
      marginTop: 3,
  },
  status: {
    fontSize: 12,
    fontWeight: 'bold',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
    overflow: 'hidden', // Needed for borderRadius on Text on Android
    alignSelf: 'flex-start',
  },
  confirmed: {
    color: '#34C759',
    backgroundColor: '#E5F9E7',
  },
  pending: {
    color: '#FF9500',
    backgroundColor: '#FFF6E5',
  },
  verificationCard: {
      borderRadius: 10,
      marginTop: 10,
      marginBottom: 5,
      paddingVertical: 10,
  },
  verificationRow: {
      flexDirection: 'row',
      alignItems: 'center',
      marginBottom: 5,
  },
  verificationText: {
      marginLeft: 8,
      fontSize: 15,
      fontWeight: 'bold',
  },
  verified: {
      color: '#34C759',
  },
  notVerified: {
      color: '#FF9500',
  },
  verificationDetails: {
      fontSize: 12,
      color: 'gray',
      textAlign: 'center',
  },
  errorText: {
    color: 'red',
    textAlign: 'center',
    marginBottom: 10,
  },
});

export default TransactionHistoryScreen;

