import React, { useState } from "react";
import { View, StyleSheet, ActivityIndicator, Alert } from "react-native";
import { Input, Button, Text, Card } from "@rneui/themed";
import apiService from "../services/apiService";
// Consider adding a date picker component

const AddAssetScreen = ({ route, navigation }) => {
  const { portfolioId } = route.params;
  const [symbol, setSymbol] = useState("");
  const [quantity, setQuantity] = useState("");
  const [purchasePrice, setPurchasePrice] = useState("");
  const [purchaseDate, setPurchaseDate] = useState(
    new Date().toISOString().split("T")[0],
  ); // Default to today, YYYY-MM-DD
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAddAsset = async () => {
    if (!symbol || !quantity || !purchasePrice || !purchaseDate) {
      setError("All fields are required.");
      return;
    }
    const qty = parseFloat(quantity);
    const price = parseFloat(purchasePrice);
    if (isNaN(qty) || qty <= 0 || isNaN(price) || price < 0) {
      setError("Please enter valid quantity and purchase price.");
      return;
    }

    // Basic date validation (YYYY-MM-DD)
    if (!/^\d{4}-\d{2}-\d{2}$/.test(purchaseDate)) {
      setError("Please enter date in YYYY-MM-DD format.");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const assetData = {
        symbol: symbol.toUpperCase(),
        quantity: qty,
        purchase_price: price,
        purchase_date: `${purchaseDate}T00:00:00Z`, // Append time and Z for UTC
      };
      await apiService.addAssetToPortfolio(portfolioId, assetData);
      // Navigate back - PortfolioDetailScreen should refresh on focus
      navigation.goBack();
    } catch (err) {
      console.error("Failed to add asset:", err);
      const apiError =
        err.response?.data?.error?.message ||
        "Could not add asset. Please try again.";
      setError(apiError);
      Alert.alert("Error", apiError);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Card containerStyle={styles.card}>
        {/* Card.Title is set in navigation options */}
        <Input
          placeholder="Asset Symbol (e.g., AAPL, BTC-USD)"
          label="Symbol *"
          onChangeText={setSymbol}
          value={symbol}
          autoCapitalize="characters"
          containerStyle={styles.inputContainer}
          disabled={loading}
        />
        <Input
          placeholder="Quantity"
          label="Quantity *"
          onChangeText={setQuantity}
          value={quantity}
          keyboardType="numeric"
          containerStyle={styles.inputContainer}
          disabled={loading}
        />
        <Input
          placeholder="Purchase Price per Unit"
          label="Purchase Price *"
          onChangeText={setPurchasePrice}
          value={purchasePrice}
          keyboardType="numeric"
          containerStyle={styles.inputContainer}
          disabled={loading}
        />
        <Input
          placeholder="YYYY-MM-DD"
          label="Purchase Date *"
          onChangeText={setPurchaseDate}
          value={purchaseDate}
          // Consider replacing with a DatePicker component for better UX
          containerStyle={styles.inputContainer}
          disabled={loading}
        />
        {error ? <Text style={styles.errorText}>{error}</Text> : null}
        {loading ? (
          <ActivityIndicator
            size="large"
            color="#007AFF"
            style={styles.loader}
          />
        ) : (
          <Button
            title="Add Asset"
            onPress={handleAddAsset}
            buttonStyle={styles.button}
            disabled={!symbol || !quantity || !purchasePrice || !purchaseDate}
          />
        )}
      </Card>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f5f5f5",
    paddingTop: 20,
  },
  card: {
    borderRadius: 10,
  },
  inputContainer: {
    marginBottom: 15,
  },
  button: {
    backgroundColor: "#007AFF",
    borderRadius: 8,
    marginTop: 10,
    paddingVertical: 12,
  },
  errorText: {
    color: "red",
    textAlign: "center",
    marginBottom: 10,
  },
  loader: {
    marginTop: 10,
  },
});

export default AddAssetScreen;
