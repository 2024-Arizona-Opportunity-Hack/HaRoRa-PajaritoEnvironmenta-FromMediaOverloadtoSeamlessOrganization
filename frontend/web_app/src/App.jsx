// src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import AuthPage from './pages/AuthPage';
import UploadPage from './pages/UploadPage';
import SearchPage from './pages/SearchPage';
import ProtectedRoute from './components/ProtectedRoute';
function App() {
  return (
    <div className='bg-base-100 p-6'>
    <Router className='font-inter text-base'>
      <Navbar />
      <Routes>
        {/* Public Route */}
        <Route path="/" element={<AuthPage />} />

        {/* Protected Routes */}
        <Route path="/upload" element={<ProtectedRoute component={UploadPage} />} />
        <Route path="/search" element={<ProtectedRoute component={SearchPage} />} />

        {/* Redirect unknown routes to home */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
    </div>
  );
}

export default App;
