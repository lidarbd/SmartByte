/**
 * Storage Utilities
 * 
 * Helper functions for working with localStorage
 */

import { STORAGE_KEYS } from '../constants/config';

/**
 * Generic function to save data to localStorage
 */
export function saveToStorage<T>(key: string, data: T): void {
  try {
    const serialized = JSON.stringify(data);
    localStorage.setItem(key, serialized);
  } catch (error) {
    console.error(`Failed to save to localStorage (key: ${key}):`, error);
  }
}

/**
 * Generic function to load data from localStorage
 */
export function loadFromStorage<T>(key: string): T | null {
  try {
    const serialized = localStorage.getItem(key);
    if (serialized === null) {
      return null;
    }
    return JSON.parse(serialized) as T;
  } catch (error) {
    console.error(`Failed to load from localStorage (key: ${key}):`, error);
    return null;
  }
}

/**
 * Remove data from localStorage
 */
export function removeFromStorage(key: string): void {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.error(`Failed to remove from localStorage (key: ${key}):`, error);
  }
}

/**
 * Clear all app data from localStorage
 */
export function clearAllStorage(): void {
  Object.values(STORAGE_KEYS).forEach((key) => {
    removeFromStorage(key);
  });
}

/**
 * Generate a unique session ID
 */
export function generateSessionId(): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 11);
  return `session_${timestamp}_${random}`;
}

/**
 * Get or create session ID
 * If a session ID exists in storage, return it. Otherwise, create a new one.
 */
export function getOrCreateSessionId(): string {
  let sessionId = loadFromStorage<string>(STORAGE_KEYS.SESSION_ID);
  
  if (!sessionId) {
    sessionId = generateSessionId();
    saveToStorage(STORAGE_KEYS.SESSION_ID, sessionId);
  }
  
  return sessionId;
}

/**
 * Save auth token
 */
export function saveAuthToken(token: string): void {
  saveToStorage(STORAGE_KEYS.AUTH_TOKEN, token);
}

/**
 * Get auth token
 */
export function getAuthToken(): string | null {
  return loadFromStorage<string>(STORAGE_KEYS.AUTH_TOKEN);
}

/**
 * Remove auth token (logout)
 */
export function clearAuthToken(): void {
  removeFromStorage(STORAGE_KEYS.AUTH_TOKEN);
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  const token = getAuthToken();
  return token !== null && token.length > 0;
}