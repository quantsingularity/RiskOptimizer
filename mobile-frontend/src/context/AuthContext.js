import React, { createContext, useState, useEffect, useContext } from 'react';
import * as SecureStore from 'expo-secure-store';
import apiService from '../services/apiService'; // Assuming apiService is set up later

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [authState, setAuthState] = useState({
    accessToken: null,
    refreshToken: null,
    authenticated: false,
    user: null,
    loading: true,
  });

  useEffect(() => {
    const loadTokens = async () => {
      try {
        const accessToken = await SecureStore.getItemAsync('accessToken');
        const refreshToken = await SecureStore.getItemAsync('refreshToken');
        const userString = await SecureStore.getItemAsync('user');
        const user = userString ? JSON.parse(userString) : null;

        if (accessToken) {
          // TODO: Optionally validate token here or fetch profile
          apiService.setAuthHeader(accessToken); // Configure apiService header
          setAuthState({
            accessToken,
            refreshToken,
            authenticated: true,
            user,
            loading: false,
          });
        } else {
          setAuthState((prevState) => ({ ...prevState, loading: false }));
        }
      } catch (e) {
        console.error('Failed to load auth tokens:', e);
        setAuthState((prevState) => ({ ...prevState, loading: false }));
      }
    };
    loadTokens();
  }, []);

  const login = async (email, password) => {
    try {
      const response = await apiService.login(email, password);
      const { access_token, refresh_token } = response.data;

      await SecureStore.setItemAsync('accessToken', access_token);
      await SecureStore.setItemAsync('refreshToken', refresh_token);
      apiService.setAuthHeader(access_token); // Update header in apiService

      // Fetch user profile after login
      const profileResponse = await apiService.getUserProfile();
      const user = profileResponse.data;
      await SecureStore.setItemAsync('user', JSON.stringify(user));

      setAuthState({
        accessToken: access_token,
        refreshToken: refresh_token,
        authenticated: true,
        user,
        loading: false,
      });
      return true;
    } catch (error) {
      console.error('Login failed:', error.response ? error.response.data : error.message);
      // Handle specific error messages if needed
      return false;
    }
  };

  const logout = async () => {
    try {
      await SecureStore.deleteItemAsync('accessToken');
      await SecureStore.deleteItemAsync('refreshToken');
      await SecureStore.deleteItemAsync('user');
      apiService.setAuthHeader(null); // Clear header in apiService
      setAuthState({
        accessToken: null,
        refreshToken: null,
        authenticated: false,
        user: null,
        loading: false,
      });
    } catch (e) {
      console.error('Logout failed:', e);
    }
  };

  // TODO: Implement token refresh logic using refreshToken

  const value = {
    ...authState,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  return useContext(AuthContext);
};

