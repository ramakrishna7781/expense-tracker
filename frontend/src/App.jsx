import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import AuthPage from './pages/AuthPage';
import ChatPage from './pages/ChatPage';
import { useAuth } from './hooks/useAuth';

function App() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route
        path="/auth"
        element={!isAuthenticated ? <AuthPage /> : <Navigate to="/" />}
      />
      <Route
        path="/"
        element={isAuthenticated ? <ChatPage /> : <Navigate to="/auth" />}
      />

      {/* Wildcard fallback route */}
      <Route path="*" element={<Navigate to="/" />} />

    </Routes>
  );
}

export default App;
