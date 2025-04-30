import React, { useState } from 'react';
import { View, StyleSheet, ActivityIndicator } from 'react-native';
import { Input, Button, Text, Card } from '@rneui/themed';
import { useAuth } from '../context/AuthContext';

const LoginScreen = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleLogin = async () => {
    if (!email || !password) {
      setError('Please enter both email and password.');
      return;
    }
    setLoading(true);
    setError('');
    const success = await login(email, password);
    setLoading(false);
    if (!success) {
      setError('Login failed. Please check your credentials.');
      // Consider more specific error messages based on API response if available
    }
    // Navigation to AppTabs happens automatically via AppNavigator if login is successful
  };

  return (
    <View style={styles.container}>
      <Card containerStyle={styles.card}>
        <Card.Title h3 style={styles.title}>RiskOptimizer Login</Card.Title>
        <Card.Divider />
        <Input
          placeholder="Email"
          leftIcon={{ type: 'material-community', name: 'email-outline' }}
          onChangeText={setEmail}
          value={email}
          keyboardType="email-address"
          autoCapitalize="none"
          containerStyle={styles.inputContainer}
          disabled={loading}
        />
        <Input
          placeholder="Password"
          leftIcon={{ type: 'material-community', name: 'lock-outline' }}
          onChangeText={setPassword}
          value={password}
          secureTextEntry
          containerStyle={styles.inputContainer}
          disabled={loading}
        />
        {error ? <Text style={styles.errorText}>{error}</Text> : null}
        {loading ? (
          <ActivityIndicator size="large" color="#007AFF" style={styles.loader} />
        ) : (
          <Button
            title="Login"
            onPress={handleLogin}
            buttonStyle={styles.button}
            titleStyle={styles.buttonTitle}
          />
        )}
        {/* Add links for registration or password recovery if needed */}
      </Card>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5', // Light background
  },
  card: {
    width: '90%',
    maxWidth: 400,
    borderRadius: 10,
    padding: 20,
  },
  title: {
    textAlign: 'center',
    marginBottom: 20,
    color: '#333',
  },
  inputContainer: {
    marginBottom: 15,
  },
  button: {
    backgroundColor: '#007AFF', // iOS blue
    borderRadius: 8,
    marginTop: 10,
    paddingVertical: 12,
  },
  buttonTitle: {
    fontWeight: 'bold',
  },
  errorText: {
    color: 'red',
    textAlign: 'center',
    marginBottom: 10,
  },
  loader: {
    marginTop: 10,
  },
});

export default LoginScreen;

