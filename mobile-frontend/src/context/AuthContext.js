import * as SecureStore from "expo-secure-store";
import { createContext, useContext, useEffect, useState } from "react";
import apiService from "../services/apiService";

const AuthContext = createContext();

// The backend wraps responses as { status, message, data: { user, tokens } }.
// axios puts the HTTP body on response.data, so the envelope is response.data
// and the useful payload is response.data.data.
function unwrap(response) {
  const body = response?.data ?? {};
  const data = body.data ?? body;
  const tokens = data.tokens ?? data;
  return {
    user: data.user ?? null,
    accessToken: tokens.access_token ?? null,
    refreshToken: tokens.refresh_token ?? null,
  };
}

export const AuthProvider = ({ children }) => {
  const [authState, setAuthState] = useState({
    accessToken: null,
    refreshToken: null,
    authenticated: false,
    user: null,
    loading: true,
  });
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadTokens = async () => {
      try {
        const accessToken = await SecureStore.getItemAsync("accessToken");
        const refreshToken = await SecureStore.getItemAsync("refreshToken");
        const userString = await SecureStore.getItemAsync("user");
        const user = userString ? JSON.parse(userString) : null;

        if (accessToken) {
          apiService.setAuthHeader(accessToken);
          setAuthState({
            accessToken,
            refreshToken,
            authenticated: true,
            user,
            loading: false,
          });
        } else {
          setAuthState((prev) => ({ ...prev, loading: false }));
        }
      } catch (e) {
        console.error("Failed to load auth tokens:", e);
        setAuthState((prev) => ({ ...prev, loading: false }));
      }
    };
    loadTokens();
  }, []);

  // Persist a session from a parsed { user, accessToken, refreshToken }.
  const establishSession = async ({ user, accessToken, refreshToken }) => {
    await SecureStore.setItemAsync("accessToken", accessToken);
    if (refreshToken) {
      await SecureStore.setItemAsync("refreshToken", refreshToken);
    }
    apiService.setAuthHeader(accessToken);

    // Profile enrichment is best effort: the login response already carries the
    // user, and a dedicated profile endpoint may not be available.
    let resolvedUser = user;
    try {
      const profile = await apiService.getUserProfile();
      resolvedUser = profile?.data?.data ?? profile?.data ?? user;
    } catch {
      // Keep the user from the auth response.
    }
    if (resolvedUser) {
      await SecureStore.setItemAsync("user", JSON.stringify(resolvedUser));
    }

    setAuthState({
      accessToken,
      refreshToken,
      authenticated: true,
      user: resolvedUser,
      loading: false,
    });
  };

  const login = async (email, password) => {
    setError(null);
    try {
      const response = await apiService.login(email, password);
      const session = unwrap(response);
      if (!session.accessToken) {
        setError("Login failed. Please check your credentials.");
        return false;
      }
      await establishSession(session);
      return true;
    } catch (err) {
      const msg =
        err.response?.data?.error?.message ||
        err.response?.data?.message ||
        "Login failed. Please check your credentials.";
      setError(msg);
      return false;
    }
  };

  const register = async (email, username, password) => {
    setError(null);
    try {
      const response = await apiService.register({ email, username, password });
      const session = unwrap(response);
      if (session.accessToken) {
        await establishSession(session);
        return true;
      }
      // If the backend does not return tokens on register, sign in explicitly.
      return await login(email, password);
    } catch (err) {
      const msg =
        err.response?.data?.error?.message ||
        err.response?.data?.message ||
        "Could not create your account.";
      setError(msg);
      return false;
    }
  };

  const logout = async () => {
    try {
      await SecureStore.deleteItemAsync("accessToken");
      await SecureStore.deleteItemAsync("refreshToken");
      await SecureStore.deleteItemAsync("user");
      apiService.setAuthHeader(null);
      setAuthState({
        accessToken: null,
        refreshToken: null,
        authenticated: false,
        user: null,
        loading: false,
      });
    } catch (e) {
      console.error("Logout failed:", e);
    }
  };

  const refreshTokens = async () => {
    try {
      if (!authState.refreshToken)
        throw new Error("No refresh token available");
      const response = await apiService.refreshToken(authState.refreshToken);
      const session = unwrap(response);
      if (!session.accessToken) throw new Error("No access token in refresh");

      await SecureStore.setItemAsync("accessToken", session.accessToken);
      if (session.refreshToken) {
        await SecureStore.setItemAsync("refreshToken", session.refreshToken);
      }
      apiService.setAuthHeader(session.accessToken);
      setAuthState((prev) => ({
        ...prev,
        accessToken: session.accessToken,
        refreshToken: session.refreshToken || prev.refreshToken,
      }));
      return session.accessToken;
    } catch (err) {
      console.error("Token refresh failed:", err.message);
      await logout();
      return null;
    }
  };

  useEffect(() => {
    if (authState.authenticated) {
      apiService.setupTokenRefreshInterceptor(
        () => authState.accessToken,
        refreshTokens,
      );
    }
    return () => {
      apiService.removeTokenRefreshInterceptor();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authState.authenticated, authState.accessToken]);

  const clearError = () => setError(null);

  const value = {
    ...authState,
    error,
    login,
    register,
    logout,
    refreshTokens,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => useContext(AuthContext);
