import React, { createContext, useState, useEffect, useCallback, useMemo } from 'react';
import { Appearance, useColorScheme } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { ThemeProvider as RNEThemeProvider, createTheme } from '@rneui/themed';
import themeConfig from '../styles/theme'; // Import the base theme configuration

const THEME_PREFERENCE_KEY = '@RiskOptimizer:themePreference'; // light | dark | system

export const ThemeContext = createContext({
  themeMode: 'system', // 'light', 'dark', or 'system'
  setThemeMode: (mode) => {},
  isDarkMode: false,
});

export const AppThemeProvider = ({ children }) => {
  const systemColorScheme = useColorScheme(); // 'light' or 'dark'
  const [themePreference, setThemePreference] = useState('system'); // User's preference

  // Load theme preference from storage on mount
  useEffect(() => {
    const loadThemePreference = async () => {
      try {
        const storedPreference = await AsyncStorage.getItem(THEME_PREFERENCE_KEY);
        if (storedPreference !== null) {
          setThemePreference(storedPreference);
        }
      } catch (e) {
        console.error('Failed to load theme preference.', e);
      }
    };
    loadThemePreference();
  }, []);

  // Determine the actual mode to use (light or dark)
  const actualMode = useMemo(() => {
    if (themePreference === 'system') {
      return systemColorScheme || 'light'; // Default to light if system preference is null
    } else {
      return themePreference;
    }
  }, [themePreference, systemColorScheme]);

  // Save theme preference to storage when it changes
  const handleSetThemeMode = useCallback(async (mode) => {
    if (['light', 'dark', 'system'].includes(mode)) {
      try {
        await AsyncStorage.setItem(THEME_PREFERENCE_KEY, mode);
        setThemePreference(mode);
      } catch (e) {
        console.error('Failed to save theme preference.', e);
      }
    }
  }, []);

  // Listen for system theme changes if preference is 'system'
  useEffect(() => {
    const subscription = Appearance.addChangeListener(({ colorScheme }) => {
      if (themePreference === 'system') {
        // No need to update state here, actualMode recalculates based on systemColorScheme
        console.log('System color scheme changed:', colorScheme);
      }
    });
    return () => subscription.remove();
  }, [themePreference]);

  // Create the RNE theme object based on the actual mode
  const rneTheme = useMemo(() => createTheme({
    ...themeConfig,
    mode: actualMode,
  }), [actualMode]);

  const contextValue = useMemo(() => ({
    themeMode: themePreference,
    setThemeMode: handleSetThemeMode,
    isDarkMode: actualMode === 'dark',
  }), [themePreference, handleSetThemeMode, actualMode]);

  return (
    <ThemeContext.Provider value={contextValue}>
      <RNEThemeProvider theme={rneTheme}>
        {children}
      </RNEThemeProvider>
    </ThemeContext.Provider>
  );
};

