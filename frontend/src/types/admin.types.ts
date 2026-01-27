/**
 * Admin Dashboard Types
 *
 * All TypeScript interfaces and types related to the admin dashboard
 */

import type { CustomerType } from './common.types';

/**
 * Statistics summary for the dashboard
 * Matches the backend MetricsResponse schema
 */
export interface DashboardStats {
  daily_consultations: DailyConsultation[];
  top_recommended_products: ProductStats[];
  customer_segmentation: CustomerSegment[];
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
 * Matches the backend TopProduct schema
 */
export interface ProductStats {
  product_name: string;
  brand: string;
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
 * Matches the backend SessionSummary schema
 */
export interface SessionHistory {
  session_id: string;
  customer_type: string | null;
  message_count: number;
  recommendation_count: number;
  started_at: string; // ISO datetime string
  ended_at: string | null; // ISO datetime string
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