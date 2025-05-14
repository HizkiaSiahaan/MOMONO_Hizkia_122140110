import React, { createContext, useState, useEffect, useContext } from 'react';
import { authAPI } from '../api/api';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      setCurrentUser(JSON.parse(userData));
    }
    
    setLoading(false);
  }, []);

  const login = async (email, password) => {
  if (email === 'admin@example.com' && password === 'password123') {
    const user = { email: 'admin@example.com', name: 'Admin' };
    localStorage.setItem('token', 'dummy-token');
    localStorage.setItem('user', JSON.stringify(user));
    setCurrentUser(user);
    return user;
  } else {
    throw new Error('Email atau password salah');
  }
};



  const register = async (userData) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await authAPI.register(userData);
      
      const { token, user } = response.data;
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      
      setCurrentUser(user);
      return user;
    } catch (err) {
      setError(err.response?.data?.message || 'Registration failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      setCurrentUser(null);
    }
  };

  const value = {
    currentUser,
    loading,
    error,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;