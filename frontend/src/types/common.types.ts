/**
 * Common Types
 *
 * Shared types used across multiple modules (chat and admin).
 * These types represent core business entities.
 */

// ============================================
// Product Types
// ============================================

/**
 * Product technical specifications
 */
export interface ProductSpecs {
  cpu?: string;
  gpu?: string;
  ram_gb?: number;
  storage_gb?: number;
  os?: string;
  warranty_years?: number;
}

/**
 * Product model from database
 */
export interface Product {
  id: number;
  sku: string;
  name: string;
  brand: string;
  product_type: string;
  category: string;
  price: number;
  stock: number;
  specs?: ProductSpecs;
  description?: string;
}

// ============================================
// Customer Types
// ============================================

/**
 * Customer type classification
 * Identified by the system based on conversation
 */
export type CustomerType =
  | 'Student'
  | 'Engineer'
  | 'Gamer'
  | 'Business'
  | 'Home User'
  | 'Other';

// ============================================
// Common API Types
// ============================================

/**
 * Generic API error response
 */
export interface ApiError {
  detail: string;
  status?: number;
}

/**
 * Health check response
 */
export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  service: string;
}
