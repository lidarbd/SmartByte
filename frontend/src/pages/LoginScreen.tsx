/**
 * LoginScreen Component
 * 
 * Admin login page with password authentication
 */

import { useState } from 'react';
import type { FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import Input from '../components/common/Input';
import Button from '../components/common/Button';

export default function LoginScreen() {
  const [password, setPassword] = useState('');
  const { login, isLoading, error, clearError } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    const success = await login(password);
    if (success) {
      navigate('/admin/dashboard');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
        
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-3xl font-bold">SB</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">SmartByte Admin</h1>
          <p className="text-gray-600 mt-2">התחבר לפאנל הניהול</p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          
          {/* Password Input */}
          <Input
            label="סיסמה"
            type="password"
            value={password}
            onChange={setPassword}
            placeholder="הכנס סיסמת מנהל"
            error={error || undefined}
            disabled={isLoading}
            fullWidth
          />

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-red-800 text-sm">{error}</p>
              <button
                type="button"
                onClick={clearError}
                className="text-red-600 text-xs underline mt-1"
              >
                סגור
              </button>
            </div>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            disabled={isLoading || !password}
            fullWidth
            size="lg"
          >
            {isLoading ? 'מתחבר...' : 'התחבר'}
          </Button>
        </form>

        {/* Footer */}
        <div className="mt-6 text-center text-sm text-gray-500">
          <p>מערכת ניהול SmartByte</p>
          <p className="mt-1">גרסה 1.0</p>
        </div>
      </div>
    </div>
  );
}