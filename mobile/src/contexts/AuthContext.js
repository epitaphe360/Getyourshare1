/**
 * Authentication Context
 * Manages user authentication state across the app
 */

import React, {createContext, useState, useContext, useEffect} from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {authAPI} from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({children}) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authToken, setAuthToken] = useState(null);

  // Load user from storage on app start
  useEffect(() => {
    loadUserFromStorage();
  }, []);

  const loadUserFromStorage = async () => {
    try {
      const storedUser = await AsyncStorage.getItem('user');
      const storedToken = await AsyncStorage.getItem('authToken');

      if (storedUser && storedToken) {
        setUser(JSON.parse(storedUser));
        setAuthToken(storedToken);
      }
    } catch (error) {
      console.error('Error loading user from storage:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const data = await authAPI.login(email, password);
      setUser(data.user);
      setAuthToken(data.token);
      return {success: true, user: data.user};
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      };
    }
  };

  const register = async (userData) => {
    try {
      const data = await authAPI.register(userData);
      return {success: true, message: data.message};
    } catch (error) {
      console.error('Register error:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed',
      };
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
      setUser(null);
      setAuthToken(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const updateUser = async (updatedData) => {
    try {
      const data = await authAPI.updateProfile(updatedData);
      const updatedUser = {...user, ...data.user};
      setUser(updatedUser);
      await AsyncStorage.setItem('user', JSON.stringify(updatedUser));
      return {success: true, user: updatedUser};
    } catch (error) {
      console.error('Update user error:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Update failed',
      };
    }
  };

  const refreshUser = async () => {
    try {
      const data = await authAPI.getCurrentUser();
      setUser(data.user);
      await AsyncStorage.setItem('user', JSON.stringify(data.user));
    } catch (error) {
      console.error('Refresh user error:', error);
    }
  };

  const value = {
    user,
    authToken,
    loading,
    login,
    register,
    logout,
    updateUser,
    refreshUser,
    isAuthenticated: !!user,
    userRole: user?.role || null,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
