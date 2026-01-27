/**
 * Admin Service
 * 
 * All API calls related to admin dashboard functionality
 */

import apiClient, { handleApiError } from './api';
import { API_CONFIG } from '../constants/config';
import type {
  LoginRequest,
  LoginResponse,
  DashboardStats,
  DailyConsultation,
  ProductStats,
  CustomerSegment,
  SessionFilters,
  PaginatedSessions,
} from '../types/admin.types';

/**
 * Login to admin dashboard
 * 
 * @param request - Login credentials
 * @returns Promise with auth token
 * @throws Error if login fails
 */
export async function adminLogin(request: LoginRequest): Promise<LoginResponse> {
  try {
    const response = await apiClient.post<LoginResponse>(
      API_CONFIG.ENDPOINTS.ADMIN_LOGIN,
      request
    );
    
    return response.data;
  } catch (error) {
    const errorMessage = handleApiError(error);
    throw new Error(errorMessage);
  }
}

/**
 * Get dashboard statistics summary
 *
 * @returns Promise with dashboard stats
 * @throws Error if request fails
 */
export async function getDashboardStats(): Promise<DashboardStats> {
  try {
    const response = await apiClient.get<DashboardStats>(
      API_CONFIG.ENDPOINTS.ADMIN_METRICS
    );

    return response.data;
  } catch (error) {
    const errorMessage = handleApiError(error);
    throw new Error(errorMessage);
  }
}

/**
 * Get daily consultations data for line chart
 *
 * @returns Promise with daily consultation data (last 30 days)
 * @throws Error if request fails
 */
export async function getDailyConsultations(): Promise<DailyConsultation[]> {
  try {
    // Backend returns all metrics in one endpoint
    const stats = await getDashboardStats();
    return stats.daily_consultations;
  } catch (error) {
    const errorMessage = handleApiError(error);
    throw new Error(errorMessage);
  }
}

/**
 * Get product recommendation statistics for bar chart
 *
 * @returns Promise with product stats (top 10 products)
 * @throws Error if request fails
 */
export async function getProductStats(): Promise<ProductStats[]> {
  try {
    // Backend returns all metrics in one endpoint
    const stats = await getDashboardStats();
    return stats.top_recommended_products;
  } catch (error) {
    const errorMessage = handleApiError(error);
    throw new Error(errorMessage);
  }
}

/**
 * Get customer segmentation data for pie chart
 * 
 * @returns Promise with customer segments
 * @throws Error if request fails
 */
export async function getCustomerSegments(): Promise<CustomerSegment[]> {
  try {
    // Backend returns all metrics in one endpoint
    const stats = await getDashboardStats();
    return stats.customer_segmentation;
  } catch (error) {
    const errorMessage = handleApiError(error);
    throw new Error(errorMessage);
  }
}

/**
 * Get session history with filters and pagination
 * 
 * @param filters - Filters and pagination options
 * @returns Promise with paginated sessions
 * @throws Error if request fails
 */
export async function getSessionHistory(
  filters: SessionFilters
): Promise<PaginatedSessions> {
  try {
    const response = await apiClient.get<PaginatedSessions>(
      API_CONFIG.ENDPOINTS.ADMIN_SESSIONS,
      { params: filters }
    );
    
    return response.data;
  } catch (error) {
    const errorMessage = handleApiError(error);
    throw new Error(errorMessage);
  }
}

/**
 * Get single session details
 * 
 * @param sessionId - Session ID to fetch
 * @returns Promise with session details
 * @throws Error if request fails
 */
export async function getSessionDetails(sessionId: string): Promise<any> {
  try {
    const response = await apiClient.get(
      `${API_CONFIG.ENDPOINTS.ADMIN_SESSIONS}/${sessionId}`
    );
    
    return response.data;
  } catch (error) {
    const errorMessage = handleApiError(error);
    throw new Error(errorMessage);
  }
}

/**
 * Test admin API connection
 * 
 * @returns Promise with boolean indicating if admin API is reachable
 */
export async function testAdminConnection(): Promise<boolean> {
  try {
    await apiClient.get(API_CONFIG.ENDPOINTS.ADMIN_METRICS);
    return true;
  } catch {
    return false;
  }
}