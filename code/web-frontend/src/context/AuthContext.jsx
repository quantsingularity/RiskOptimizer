import React, { createContext, useContext, useState } from "react";

// Create context
const AuthContext = createContext();

// Provider component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Login function
  const login = async (address) => {
    setLoading(true);
    setError(null);
    try {
      // In a real app, this would connect to a backend authentication endpoint
      // For now, we'll simulate a successful login
      const userData = {
        address,
        name: "Demo User",
        isAuthenticated: true,
        profileImage: null,
      };

      setUser(userData);
      localStorage.setItem("user", JSON.stringify(userData));
      return true;
    } catch (err) {
      setError(err.message || "An error occurred during login");
      console.error("Login error:", err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    setUser(null);
    localStorage.removeItem("user");
  };

  // Check if user is already logged in from localStorage on app initialization
  const checkAuthState = () => {
    const savedUser = localStorage.getItem("user");
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  };

  // Context value
  const value = {
    user,
    loading,
    error,
    login,
    logout,
    checkAuthState,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export default AuthContext;
