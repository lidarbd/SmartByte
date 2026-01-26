/**
 * Services Index
 *
 * Central export point for all API services.
 * Organized by functionality for easy imports.
 *
 * @example
 * // Import individual functions
 * import { sendMessage, getAdminMetrics } from '@/services';
 *
 * // Or import grouped services
 * import { conversationApi, adminApi } from '@/services';
 */

// Export API client and utilities
export { default as apiClient, handleApiError } from './api.ts';
// Export Chat Service functions
export {
  sendMessage,
  sendChatMessage,
  testChatConnection
} from './chatService';

// Export Admin Service functions
export {
  adminLogin,
  getDashboardStats,
  getDailyConsultations,
  getProductStats,
  getCustomerSegments,
  getSessionHistory,
  getSessionDetails,
  testAdminConnection,
} from './adminService';

// Export grouped services for organized imports
import * as chatService from './chatService';
import * as adminService from './adminService';

export { chatService, adminService };
