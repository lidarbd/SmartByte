/**
 * Admin Dashboard Types
 *
 * All TypeScript interfaces and types related to the admin dashboard
 */

import type { CustomerType } from './common.types';

/**
 * Statistics summary for the dashboard
 */
export interface DashboardStats {
  total_sessions: number;
  total_recommendations: number;
  avg_messages_per_session: number;
  conversion_rate: number; // Percentage of sessions that got recommendations
}

/**
 * Daily consultation data for line chart
 */
export interface DailyConsultation {
  date: string; // ISO date string (YYYY-MM-DD)
  count: number;
}

/**
 * Product recommendation statistics for bar chart
 */
export interface ProductStats {
  product_id: number;
  product_name: string;
  recommendation_count: number;
}

/**
 * Customer segmentation data for pie chart
 */
export interface CustomerSegment {
  customer_type: CustomerType;
  count: number;
  percentage: number;
}

/**
 * Single session in the history table
 */
export interface SessionHistory {
  session_id: string;
  customer_type: CustomerType;
  message_count: number;
  recommended_products: number;
  created_at: string; // ISO datetime string
  duration_seconds?: number;
}

/**
 * Filters for session history table
 */
export interface SessionFilters {
  search?: string;
  customer_type?: CustomerType | 'all';
  date_from?: string;
  date_to?: string;
  page: number;
  per_page: number;
}

/**
 * Paginated response for session history
 */
export interface PaginatedSessions {
  sessions: SessionHistory[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

/**
 * Authentication state
 */
export interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

/**
 * Login request
 */
export interface LoginRequest {
  password: string;
}

/**
 * Login response
 */
export interface LoginResponse {
  token: string;
  expires_at: string;
}

/**
 * Admin dashboard complete state
 */
export interface AdminDashboardState {
  stats: DashboardStats | null;
  dailyConsultations: DailyConsultation[];
  productStats: ProductStats[];
  customerSegments: CustomerSegment[];
  sessionHistory: PaginatedSessions | null;
  isLoading: boolean;
  error: string | null;
}