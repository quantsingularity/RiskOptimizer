import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, Alert } from 'react-native';
import { Card, Button, Slider, CheckBox, Input } from '@rneui/themed';
import RNPickerSelect from 'react-native-picker-select'; // Need to install this
import apiService from '../services/apiService';

// Placeholder for Efficient Frontier Chart
const EfficientFrontierChart = () => (
  <View style={styles.chartPlaceholder}>
    <Text>Efficient Frontier Chart Placeholder</Text>
  </View>
);

const OptimizationScreen = ({ navigation }) => {
  const [portfolios, setPortfolios] = useState([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState(null);
  const [riskTolerance, setRiskTolerance] = useState('moderate'); // low, moderate, high
  const [investmentHorizon, setInvestmentHorizon] = useState('long_term'); // short_term, medium_term, long_term
  const [maxAllocation, setMaxAllocation] = useState(0.20);
  const [minAllocation, setMinAllocation] = useState(0.05);
  const [excludedSectors, setExcludedSectors] = useState([]); // Example: ['Energy', 'Tobacco']
  const [loadingPortfolios, setLoadingPortfolios] = useState(true);
  const [loadingOptimization, setLoadingOptimization] = useState(false);
  const [optimizationResult, setOptimizationResult] = useState(null);
  const [error, setError] = useState('');

  // Fetch portfolios for selection
  useEffect(() => {
    const fetchPortfolios = async () => {
      setLoadingPortfolios(true);
      setError('');
      try {
        const response = await apiService.getPortfolios();
        const portfolioItems = (response.data.portfolios || []).map(p => ({ label: p.name, value: p.id }));
        setPortfolios(portfolioItems);
        if (portfolioItems.length > 0) {
          // Optionally pre-select the first portfolio
          // setSelectedPortfolio(portfolioItems[0].value);
        }
      } catch (err) {
        console.error('Failed to fetch portfolios for optimization:', err);
        setError('Could not load portfolios.');
      } finally {
        setLoadingPortfolios(false);
      }
    };
    fetchPortfolios();
  }, []);

  const handleRunOptimization = async () => {
    if (!selectedPortfolio) {
      Alert.alert('Selection Required', 'Please select a portfolio to optimize.');
      return;
    }
    setLoadingOptimization(true);
    setError('');
    setOptimizationResult(null);

    const params = {
      portfolio_id: selectedPortfolio,
      risk_tolerance: riskTolerance,
      investment_horizon: investmentHorizon,
      constraints: {
        max_allocation_per_asset: maxAllocation,
        min_allocation_per_asset: minAllocation,
        excluded_sectors: excludedSectors,
      },
    };

    try {
      const response = await apiService.getOptimizationRecommendations(params);
      setOptimizationResult(response.data);
    } catch (err) {
      console.error('Optimization failed:', err);
      setError('Optimization failed. Please try again.');
      Alert.alert('Error', 'Optimization failed. Please check parameters or try again later.');
    } finally {
      setLoadingOptimization(false);
    }
  };

  // Example sector handling - replace with actual data/logic
  const availableSectors = ['Technology', 'Healthcare', 'Financials', 'Energy', 'Consumer Staples', 'Industrials', 'Utilities', 'Real Estate', 'Materials', 'Communication Services', 'Consumer Discretionary', 'Tobacco'];
  const toggleSectorExclusion = (sector) => {
    setExcludedSectors(prev =>
      prev.includes(sector) ? prev.filter(s => s !== sector) : [...prev, sector]
    );
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.header}>Portfolio Optimization</Text>

      <Card containerStyle={styles.card}>
        <Card.Title>Configuration</Card.Title>
        <Card.Divider />

        {loadingPortfolios ? (
          <ActivityIndicator />
        ) : portfolios.length > 0 ? (
          <RNPickerSelect
            placeholder={{ label: 'Select a portfolio...', value: null }}
            items={portfolios}
            onValueChange={(value) => setSelectedPortfolio(value)}
            style={pickerSelectStyles}
            value={selectedPortfolio}
            useNativeAndroidPickerStyle={false} // Recommended for styling consistency
          />
        ) : (
          <Text style={styles.infoText}>No portfolios available. Create one first.</Text>
        )}

        <Text style={styles.label}>Risk Tolerance</Text>
        <RNPickerSelect
          placeholder={{}}
          items={[
            { label: 'Low', value: 'low' },
            { label: 'Moderate', value: 'moderate' },
            { label: 'High', value: 'high' },
          ]}
          onValueChange={(value) => setRiskTolerance(value)}
          style={pickerSelectStyles}
          value={riskTolerance}
          useNativeAndroidPickerStyle={false}
        />

        <Text style={styles.label}>Investment Horizon</Text>
        <RNPickerSelect
          placeholder={{}}
          items={[
            { label: 'Short Term', value: 'short_term' },
            { label: 'Medium Term', value: 'medium_term' },
            { label: 'Long Term', value: 'long_term' },
          ]}
          onValueChange={(value) => setInvestmentHorizon(value)}
          style={pickerSelectStyles}
          value={investmentHorizon}
          useNativeAndroidPickerStyle={false}
        />

        <Text style={styles.label}>Max Allocation per Asset: {(maxAllocation * 100).toFixed(0)}%</Text>
        <Slider
          value={maxAllocation}
          onValueChange={setMaxAllocation}
          minimumValue={0.01}
          maximumValue={1.0}
          step={0.01}
          thumbStyle={styles.thumb}
          trackStyle={styles.track}
        />

        <Text style={styles.label}>Min Allocation per Asset: {(minAllocation * 100).toFixed(0)}%</Text>
        <Slider
          value={minAllocation}
          onValueChange={setMinAllocation}
          minimumValue={0.0}
          maximumValue={0.5} // Sensible max for min allocation
          step={0.01}
          thumbStyle={styles.thumb}
          trackStyle={styles.track}
        />

        <Text style={styles.label}>Exclude Sectors:</Text>
        <View style={styles.checkboxContainer}>
          {availableSectors.map(sector => (
            <CheckBox
              key={sector}
              title={sector}
              checked={excludedSectors.includes(sector)}
              onPress={() => toggleSectorExclusion(sector)}
              containerStyle={styles.checkbox}
              textStyle={styles.checkboxText}
              size={18}
            />
          ))}
        </View>

        <Button
          title="Run Optimization"
          onPress={handleRunOptimization}
          buttonStyle={styles.runButton}
          disabled={loadingOptimization || !selectedPortfolio}
          loading={loadingOptimization}
        />
        {error ? <Text style={styles.errorText}>{error}</Text> : null}
      </Card>

      {optimizationResult && (
        <Card containerStyle={styles.card}>
          <Card.Title>Optimization Results</Card.Title>
          <Card.Divider />
          <Text style={styles.resultText}>Optimized Risk Score: {optimizationResult.optimized_risk_score?.toFixed(2)} (Current: {optimizationResult.current_risk_score?.toFixed(2)})</Text>
          <Text style={styles.resultText}>Expected Return: {(optimizationResult.expected_return * 100)?.toFixed(2)}%</Text>
          <Text style={styles.resultText}>Sharpe Ratio: {optimizationResult.sharpe_ratio?.toFixed(2)}</Text>

          <Text style={styles.subHeader}>Recommendations:</Text>
          {optimizationResult.recommendations?.map((rec, index) => (
            <View key={index} style={styles.recommendationItem}>
              <Text style={styles.recSymbol}>{rec.symbol}: <Text style={styles.recAction}>{rec.action.toUpperCase()}</Text></Text>
              <Text>New Allocation: {(rec.recommended_allocation * 100).toFixed(2)}% (Current: {(rec.current_allocation * 100).toFixed(2)}%)</Text>
              {/* Optionally show quantity change */}
            </View>
          ))}

          <Text style={styles.subHeader}>Efficient Frontier:</Text>
          <EfficientFrontierChart data={optimizationResult.efficient_frontier} />
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
  header: {
    fontSize: 24,
    fontWeight: 'bold',
    margin: 20,
    color: '#333',
    textAlign: 'center',
  },
  card: {
    borderRadius: 10,
    marginBottom: 15,
  },
  label: {
    fontSize: 16,
    color: '#555',
    marginTop: 15,
    marginBottom: 5,
    marginLeft: 10,
  },
  thumb: {
    height: 20,
    width: 20,
    backgroundColor: '#007AFF',
  },
  track: {
    height: 4,
    borderRadius: 2,
  },
  checkboxContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 5,
  },
  checkbox: {
    backgroundColor: 'transparent',
    borderWidth: 0,
    padding: 2,
    margin: 0,
    marginLeft: 0,
    marginRight: 5,
  },
  checkboxText: {
    fontSize: 12,
    fontWeight: 'normal',
  },
  runButton: {
    backgroundColor: '#34C759',
    marginTop: 20,
    borderRadius: 8,
  },
  resultText: {
    fontSize: 16,
    marginBottom: 8,
  },
  subHeader: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 15,
    marginBottom: 10,
  },
  recommendationItem: {
    marginBottom: 10,
    paddingLeft: 10,
    borderLeftWidth: 3,
    borderLeftColor: '#007AFF',
  },
  recSymbol: {
    fontWeight: 'bold',
  },
  recAction: {
    fontStyle: 'italic',
  },
  chartPlaceholder: {
    height: 200,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#eee',
    borderRadius: 8,
    marginTop: 10,
  },
  errorText: {
    color: 'red',
    textAlign: 'center',
    marginTop: 10,
  },
  infoText: {
    textAlign: 'center',
    color: 'gray',
    marginVertical: 10,
  },
});

const pickerSelectStyles = StyleSheet.create({
  inputIOS: {
    fontSize: 16,
    paddingVertical: 12,
    paddingHorizontal: 10,
    borderWidth: 1,
    borderColor: 'gray',
    borderRadius: 4,
    color: 'black',
    paddingRight: 30, // to ensure the text is never behind the icon
    marginTop: 5,
    marginBottom: 15,
  },
  inputAndroid: {
    fontSize: 16,
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderWidth: 0.5,
    borderColor: 'gray',
    borderRadius: 8,
    color: 'black',
    paddingRight: 30, // to ensure the text is never behind the icon
    marginTop: 5,
    marginBottom: 15,
  },
});

export default OptimizationScreen;

