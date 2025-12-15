import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { ThemeProvider } from '@rneui/themed';
import { AuthProvider } from './src/context/AuthContext';
import { ThemeProvider as CustomThemeProvider } from './src/context/ThemeContext';
import AppNavigator from './src/navigation/AppNavigator';
import theme from './src/styles/theme';

export default function App() {
    return (
        <SafeAreaProvider>
            <ThemeProvider theme={theme}>
                <CustomThemeProvider>
                    <AuthProvider>
                        <StatusBar style="auto" />
                        <AppNavigator />
                    </AuthProvider>
                </CustomThemeProvider>
            </ThemeProvider>
        </SafeAreaProvider>
    );
}
