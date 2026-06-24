import { createContext, useCallback, useContext, useState } from "react";
import apiService from "../services/apiService";

const AuthContext = createContext();
const STORAGE_KEY = "riskoptimizer.auth";

function persist(session) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
}

function readSession() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    localStorage.removeItem(STORAGE_KEY);
    return null;
  }
}

// Normalize the backend envelope { data: { user, tokens } } into a session.
function toSession(payload) {
  const data = payload?.data || payload || {};
  const tokens = data.tokens || {};
  return {
    user: data.user || null,
    token: tokens.access_token || null,
    refresh_token: tokens.refresh_token || null,
    isAuthenticated: Boolean(tokens.access_token),
  };
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const login = useCallback(async (credentials) => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiService.auth.login({
        email: credentials.email,
        password: credentials.password,
      });
      const session = toSession(res);
      if (!session.isAuthenticated) {
        throw new Error("Login failed. Please check your credentials.");
      }
      persist(session);
      setUser(session.user);
      return true;
    } catch (err) {
      setError(err.message || "Unable to sign in. Please try again.");
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(
    async (userData) => {
      setLoading(true);
      setError(null);
      try {
        const res = await apiService.auth.register({
          email: userData.email,
          username: userData.username,
          password: userData.password,
          ...(userData.wallet_address
            ? { wallet_address: userData.wallet_address }
            : {}),
        });
        const session = toSession(res);
        // Registration returns tokens; if not, fall back to an explicit login.
        if (session.isAuthenticated) {
          persist(session);
          setUser(session.user);
          return true;
        }
        return await login({
          email: userData.email,
          password: userData.password,
        });
      } catch (err) {
        setError(err.message || "Unable to create your account.");
        return false;
      } finally {
        setLoading(false);
      }
    },
    [login],
  );

  const logout = useCallback(async () => {
    try {
      await apiService.auth.logout();
    } catch {
      // Logout is best-effort; clear local state regardless.
    }
    setUser(null);
    setError(null);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  const checkAuthState = useCallback(() => {
    const session = readSession();
    if (session?.isAuthenticated) {
      setUser(session.user);
    } else if (session) {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  const clearError = useCallback(() => setError(null), []);

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    checkAuthState,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export default AuthContext;
