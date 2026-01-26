/**
 * Base API Service
 * 
 * Axios instance with configuration for all API calls
 */

import axios, { type AxiosInstance, AxiosError, type InternalAxiosRequestConfig } from 'axios';
import { API_CONFIG, ERROR_MESSAGES } from '../constants/config';
import { getAuthToken } from '../utils/storage.ts';
/**
 * Create axios instance with base configuration
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor - Add auth token to requests if available
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getAuthToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor - Handle common errors
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // Network error
    if (!error.response) {
      throw new Error(ERROR_MESSAGES.NETWORK_ERROR);
    }

    // HTTP error codes
    const status = error.response.status;
    
    switch (status) {
      case 401:
        // Unauthorized - clear token and redirect to login
        // This will be handled by the auth hook
        throw new Error(ERROR_MESSAGES.UNAUTHORIZED);
      
      case 403:
        throw new Error(ERROR_MESSAGES.UNAUTHORIZED);
      
      case 404:
        throw new Error('הנתיב המבוקש לא נמצא.');
      
      case 500:
      case 502:
      case 503:
        throw new Error(ERROR_MESSAGES.SERVER_ERROR);
      
      default:
        // Try to extract error message from response
        const message = (error.response.data as any)?.message || 
                       (error.response.data as any)?.detail ||
                       ERROR_MESSAGES.SERVER_ERROR;
        throw new Error(message);
    }
  }
);

/**
 * Export configured axios instance
 */
export default apiClient;

/**
 * Helper function to handle API errors consistently
 */
export function handleApiError(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return ERROR_MESSAGES.SERVER_ERROR;
}