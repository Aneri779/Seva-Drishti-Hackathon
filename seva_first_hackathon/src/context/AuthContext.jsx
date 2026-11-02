// src/context/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const saved = sessionStorage.getItem('sd_user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [loading, setLoading] = useState(false);

  const login = (token, userData) => {
    sessionStorage.setItem('sd_token', token);
    sessionStorage.setItem('sd_user', JSON.stringify(userData));
    setUser(userData);
  };

  const loginWithOtp = async (mobile, otp) => {
    const data = await api('/auth/otp/verify', {
      method: 'POST',
      body: { mobile, otp }
    });
    sessionStorage.setItem('sd_token', data.tokens?.access_token || data.token);
    sessionStorage.setItem('sd_user', JSON.stringify(data.user));
    setUser(data.user);
    return data;
  };

  const logout = () => {
    sessionStorage.removeItem('sd_token');
    sessionStorage.removeItem('sd_user');
    setUser(null);
    window.location.href = '/login';
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, loginWithOtp, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  return ctx || { user: null, loading: false };
}

