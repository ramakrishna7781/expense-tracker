import React, { createContext, useState, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('authToken'));

  const login = (newToken) => {
    localStorage.setItem('authToken', newToken);
    setToken(newToken);
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    setToken(null);
  };

  const isTokenValid = () => {
    if (!token) return false;
    try {
      const decoded = jwtDecode(token);
      return decoded.exp * 1000 > Date.now();
    } catch (error) {
      return false;
    }
  };
  
  useEffect(() => {
    if (!isTokenValid()) {
        logout();
    }
  }, []);

  return (
    <AuthContext.Provider value={{ token, login, logout, isAuthenticated: !!token && isTokenValid() }}>
      {children}
    </AuthContext.Provider>
  );
};