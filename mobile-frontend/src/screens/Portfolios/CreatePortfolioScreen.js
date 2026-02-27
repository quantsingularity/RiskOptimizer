import React, { useState } from "react";
import { View, StyleSheet, ActivityIndicator, Alert } from "react-native";
import { Input, Button, Text, Card } from "@rneui/themed";
import apiService from "../../services/apiService";

const CreatePortfolioScreen = ({ navigation }) => {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [currency, setCurrency] = useState("USD"); // Default or allow selection
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCreate = async () => {
    if (!name) {
      setError("Portfolio name is required.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const response = await apiService.createPortfolio({
        name,
        description,
        currency,
      });
      // Navigate back to portfolio list or to the new portfolio's detail screen
      // PortfolioListScreen should refresh on focus to show the new portfolio
      navigation.goBack();
    } catch (err) {
      console.error("Failed to create portfolio:", err);
      setError("Could not create portfolio. Please try again.");
      Alert.alert(
        "Error",
        "Could not create portfolio. Please try again later.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Card containerStyle={styles.card}>
        {/* Card.Title is set in navigation options */}
        <Input
          placeholder="Portfolio Name (e.g., Growth Fund)"
          label="Name *"
          onChangeText={setName}
          value={name}
          containerStyle={styles.inputContainer}
          disabled={loading}
        />
        <Input
          placeholder="Optional description"
          label="Description"
          onChangeText={setDescription}
          value={description}
          containerStyle={styles.inputContainer}
          multiline
          numberOfLines={3}
          disabled={loading}
        />
        <Input
          placeholder="Currency Code (e.g., USD)"
          label="Currency"
          onChangeText={setCurrency} // Consider a picker for common currencies
          value={currency}
          containerStyle={styles.inputContainer}
          disabled={loading}
          autoCapitalize="characters"
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
            title="Create Portfolio"
            onPress={handleCreate}
            buttonStyle={styles.button}
            disabled={!name}
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
    paddingTop: 20, // Add padding if header is not shown or for spacing
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

export default CreatePortfolioScreen;
