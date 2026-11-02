// src/components/common/ProtectedRoute.jsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function ProtectedRoute({ roles, children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-background text-primary font-mono text-sm">
        <span className="material-symbols-outlined animate-spin text-2xl mr-2">radar</span>
        AUTHENTICATING TACTICAL ENCLAVE...
      </div>
    );
  }

  // If user not authenticated, redirect to login
  if (!user && !sessionStorage.getItem('sd_token')) {
    return <Navigate to="/login" replace />;
  }

  // RBAC validation
  if (roles && user && !roles.includes(user.role) && user.role !== 'admin') {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

