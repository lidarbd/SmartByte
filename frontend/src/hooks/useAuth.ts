/**
 * useAuth Hook
 * 
 * Custom hook for managing authentication state
 */

import { useState, useCallback, useEffect } from 'react';
import type { AuthState } from '../types/admin.types';
import { adminLogin } from '../services/adminService';
import { 
  saveAuthToken, 
  clearAuthToken, 
  isAuthenticated as checkIsAuthenticated 
} from '../utils/storage';

/**
 * Hook for authentication functionality
 */
export function useAuth() {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    isLoading: true,
    error: null,
  });

  /**
   * Check authentication status on mount
   */
  useEffect(() => {
    const isAuth = checkIsAuthenticated();
    setState({
      isAuthenticated: isAuth,
      isLoading: false,
      error: null,
    });
  }, []);

  /**
   * Login function
   */
  const login = useCallback(async (password: string) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      // Call login API
      const response = await adminLogin({ password });

      // Save token
      saveAuthToken(response.token);

      // Update state
      setState({
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });

      return true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'התחברות נכשלה';
      
      setState({
        isAuthenticated: false,
        isLoading: false,
        error: errorMessage,
      });

      return false;
    }
  }, []);

  /**
   * Logout function
   */
  const logout = useCallback(() => {
    clearAuthToken();
    setState({
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  }, []);

  /**
   * Clear error
   */
  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  return {
    // State
    isAuthenticated: state.isAuthenticated,
    isLoading: state.isLoading,
    error: state.error,

    // Actions
    login,
    logout,
    clearError,
  };
}