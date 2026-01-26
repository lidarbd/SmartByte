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
      API_CONFIG.ENDPOINTS.ADMIN_STATS
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
 * @param days - Number of days to fetch (default: 30)
 * @returns Promise with daily consultation data
 * @throws Error if request fails
 */
export async function getDailyConsultations(
  days: number = 30
): Promise<DailyConsultation[]> {
  try {
    const response = await apiClient.get<DailyConsultation[]>(
      `${API_CONFIG.ENDPOINTS.ADMIN_STATS}/daily`,
      { params: { days } }
    );
    
    return response.data;
  } catch (error) {
    const errorMessage = handleApiError(error);
    throw new Error(errorMessage);
  }
}

/**
 * Get product recommendation statistics for bar chart
 * 
 * @param limit - Number of top products to fetch (default: 10)
 * @returns Promise with product stats
 * @throws Error if request fails
 */
export async function getProductStats(limit: number = 10): Promise<ProductStats[]> {
  try {
    const response = await apiClient.get<ProductStats[]>(
      `${API_CONFIG.ENDPOINTS.ADMIN_PRODUCTS}/stats`,
      { params: { limit } }
    );
    
    return response.data;
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
    const response = await apiClient.get<CustomerSegment[]>(
      `${API_CONFIG.ENDPOINTS.ADMIN_STATS}/segments`
    );
    
    return response.data;
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
    await apiClient.get(API_CONFIG.ENDPOINTS.ADMIN_STATS);
    return true;
  } catch {
    return false;
  }
}