// src/components/ProtectedRoute.jsx
import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { getProfileInfo } from '../api/api'; // Adjust the import path as needed

function ProtectedRoute({ component: Component }) {
  const [isAuthenticated, setIsAuthenticated] = useState(null); // null means not checked yet

  useEffect(() => {
    const checkAuth = async () => {
      const { response, err } = await getProfileInfo();
      if (err) {
        setIsAuthenticated(false);
      } else {
        setIsAuthenticated(true);
      }
    };

    checkAuth();
  }, []);

  if (isAuthenticated === null) {
    // Authentication is still being checked
    return (
      <div className="flex justify-center items-center h-screen">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Not authenticated, redirect to AuthPage
    return <Navigate to="/" replace />;
  }

  // Authenticated, render the component
  return <Component />;
}

export default ProtectedRoute;
