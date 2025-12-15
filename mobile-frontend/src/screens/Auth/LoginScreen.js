import React, { useState } from 'react';
import { View, StyleSheet, ActivityIndicator, KeyboardAvoidingView, Platform } from 'react-native';
import { Input, Button, Text, Card, useTheme } from '@rneui/themed'; // Import useTheme
import { useAuth } from '../../context/AuthContext';

const LoginScreen = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const { login } = useAuth();
    const { theme } = useTheme(); // Access the theme

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
        }
    };

    // Define styles using the theme
    const styles = StyleSheet.create({
        container: {
            flex: 1,
            justifyContent: 'center',
            alignItems: 'center',
            backgroundColor: theme.colors.background, // Use theme background color
            padding: 20,
        },
        card: {
            width: '100%',
            maxWidth: 400,
            // Theme handles card styling (borderRadius, padding, shadow)
        },
        title: {
            textAlign: 'center',
            marginBottom: 20,
            // Theme handles h3 styling
        },
        inputContainer: {
            // Theme handles Input container styling
            marginBottom: 15, // Keep custom margin if needed
        },
        button: {
            // Theme handles Button styling (backgroundColor, borderRadius, padding)
            marginTop: 10,
        },
        buttonTitle: {
            // Theme handles Button title styling (fontWeight, fontSize)
        },
        errorText: {
            color: theme.colors.error, // Use theme error color
            textAlign: 'center',
            marginBottom: 10,
            fontSize: 15,
        },
        loader: {
            marginTop: 20,
        },
    });

    return (
        <KeyboardAvoidingView
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
            style={styles.container}
        >
            <Card containerStyle={styles.card}>
                <Card.Title h3 style={styles.title}>
                    RiskOptimizer Login
                </Card.Title>
                <Card.Divider />
                <Input
                    placeholder="Email"
                    leftIcon={{
                        type: 'material-community',
                        name: 'email-outline',
                        color: theme.colors.grey0,
                    }} // Use theme color for icon
                    onChangeText={setEmail}
                    value={email}
                    keyboardType="email-address"
                    autoCapitalize="none"
                    containerStyle={styles.inputContainer}
                    disabled={loading}
                    // Theme handles input styling (border, background, text color, placeholder color)
                />
                <Input
                    placeholder="Password"
                    leftIcon={{
                        type: 'material-community',
                        name: 'lock-outline',
                        color: theme.colors.grey0,
                    }} // Use theme color for icon
                    onChangeText={setPassword}
                    value={password}
                    secureTextEntry
                    containerStyle={styles.inputContainer}
                    disabled={loading}
                    // Theme handles input styling
                />
                {error ? <Text style={styles.errorText}>{error}</Text> : null}
                {loading ? (
                    <ActivityIndicator
                        size="large"
                        color={theme.colors.primary}
                        style={styles.loader}
                    /> // Use theme primary color
                ) : (
                    <Button
                        title="Login"
                        onPress={handleLogin}
                        buttonStyle={styles.button} // Apply minor custom styles if needed
                        // Theme handles most button styling
                    />
                )}
                {/* Add links for registration or password recovery if needed */}
            </Card>
        </KeyboardAvoidingView>
    );
};

export default LoginScreen;
