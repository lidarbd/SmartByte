/**
 * Application Constants
 * 
 * All configuration values, API endpoints, and constants
 */

/**
 * API Configuration
 */
export const API_CONFIG = {
  // Base URL for the backend API
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  
  // API endpoints
  ENDPOINTS: {
    // Chat endpoints
    SEND_MESSAGE: '/api/conversation/message',
    
    // Admin endpoints
    ADMIN_LOGIN: '/api/admin/login',
    ADMIN_METRICS: '/api/admin/metrics',
    ADMIN_SESSIONS: '/api/admin/sessions',
    ADMIN_PRODUCTS: '/api/admin/products',
  },
  
  // Request timeout in milliseconds
  TIMEOUT: 30000,
} as const;

/**
 * Local Storage Keys
 */
export const STORAGE_KEYS = {
  SESSION_ID: 'smartbyte_session_id',
  CHAT_HISTORY: 'smartbyte_chat_history',
  AUTH_TOKEN: 'smartbyte_auth_token',
  USER_PREFERENCES: 'smartbyte_preferences',
} as const;

/**
 * UI Configuration
 */
export const UI_CONFIG = {
  // Chat configuration
  CHAT: {
    MAX_MESSAGE_LENGTH: 500,
    TYPING_DELAY_MS: 1000,
    AUTO_SCROLL_DELAY_MS: 100,
  },
  
  // Admin dashboard configuration
  ADMIN: {
    DEFAULT_PAGE_SIZE: 20,
    CHART_COLORS: {
      PRIMARY: '#4F46E5',     // Indigo
      SECONDARY: '#7C3AED',   // Purple
      SUCCESS: '#10B981',     // Green
      WARNING: '#F59E0B',     // Amber
      DANGER: '#EF4444',      // Red
      INFO: '#3B82F6',        // Blue
    },
    REFRESH_INTERVAL_MS: 60000, // Refresh dashboard every minute
  },
} as const;

/**
 * Application Routes
 */
export const ROUTES = {
  HOME: '/',
  CHAT: '/chat',
  ADMIN: '/admin',
  ADMIN_LOGIN: '/admin/login',
} as const;

/**
 * Customer Type Display Names (Hebrew)
 */
export const CUSTOMER_TYPE_NAMES: Record<string, string> = {
  Student: 'סטודנט',
  Engineer: 'מהנדס',
  Gamer: 'גיימר',
  Business: 'עסקי',
  'Home User': 'שימוש ביתי',
  Other: 'אחר',
} as const;

/**
 * Customer Type Colors for charts
 */
export const CUSTOMER_TYPE_COLORS: Record<string, string> = {
  Student: '#10B981',    // Green
  Engineer: '#3B82F6',   // Blue
  Gamer: '#EF4444',      // Red
  Business: '#F59E0B',   // Amber
  'Home User': '#8B5CF6', // Purple
  Other: '#6B7280',      // Gray
} as const;

/**
 * Error Messages
 */
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'שגיאת רשת. אנא בדוק את החיבור לאינטרנט.',
  SERVER_ERROR: 'שגיאת שרת. אנא נסה שוב מאוחר יותר.',
  UNAUTHORIZED: 'אין לך הרשאה לצפות בדף זה.',
  SESSION_EXPIRED: 'פג תוקף ההתחברות. אנא התחבר שוב.',
  INVALID_MESSAGE: 'ההודעה שהזנת לא תקינה.',
  CHAT_ERROR: 'אירעה שגיאה בשליחת ההודעה. אנא נסה שוב.',
  LOGIN_FAILED: 'התחברות נכשלה. אנא בדוק את הסיסמה.',
} as const;

/**
 * Success Messages
 */
export const SUCCESS_MESSAGES = {
  LOGIN_SUCCESS: 'התחברת בהצלחה!',
  MESSAGE_SENT: 'ההודעה נשלחה בהצלחה.',
} as const;

/**
 * Validation Rules
 */
export const VALIDATION = {
  MESSAGE: {
    MIN_LENGTH: 1,
    MAX_LENGTH: 500,
  },
  PASSWORD: {
    MIN_LENGTH: 4,
  },
} as const;

/**
 * Date Format Options
 */
export const DATE_FORMAT = {
  FULL: {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  } as Intl.DateTimeFormatOptions,
  
  SHORT: {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  } as Intl.DateTimeFormatOptions,
  
  TIME_ONLY: {
    hour: '2-digit',
    minute: '2-digit',
  } as Intl.DateTimeFormatOptions,
} as const;