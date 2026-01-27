/**
 * App Component
 * 
 * Main application with routing for Chat and Admin
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ChatScreen from './pages/ChatScreen';
import LoginScreen from './pages/LoginScreen';
import DashboardScreen from './pages/DashboardScreen';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<ChatScreen />} />
        <Route path="/chat" element={<ChatScreen />} />
        
        {/* Admin Routes */}
        <Route path="/admin/login" element={<LoginScreen />} />
        <Route 
          path="/admin/dashboard" 
          element={
            <ProtectedRoute>
              <DashboardScreen />
            </ProtectedRoute>
          } 
        />
        
        {/* Redirect /admin to dashboard */}
        <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />
        
        {/* 404 - Redirect to home */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;