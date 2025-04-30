import React from 'react';
import { AuthProvider } from './src/context/AuthContext';
import AppNavigator from './src/navigation/AppNavigator';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { AppThemeProvider } from './src/context/ThemeContext'; // Import the custom theme provider
import { StatusBar } from 'react-native'; // Import StatusBar

export default function App() {
  return (
    <SafeAreaProvider>
      <AppThemeProvider> {/* Use the custom AppThemeProvider */}
        {/* StatusBar can be managed here or within AppThemeProvider/AppNavigator */}
        {/* Let AppThemeProvider manage it based on the current theme */}
        <AuthProvider>
          <AppNavigator />
        </AuthProvider>
      </AppThemeProvider>
    </SafeAreaProvider>
  );
}
