/**
 * Formatter Utilities
 * 
 * Helper functions for formatting dates, prices, numbers, and text
 */

import { DATE_FORMAT } from '../constants/config';

/**
 * Format price in Israeli Shekels
 * @param price - Price in ILS
 * @returns Formatted string like "4,999 ₪"
 */
export function formatPrice(price: number): string {
  return `${price.toLocaleString('he-IL')} ₪`;
}

/**
 * Format date to Hebrew locale
 * @param date - Date object or ISO string
 * @param format - Format options (FULL, SHORT, or TIME_ONLY)
 * @returns Formatted date string
 */
export function formatDate(
  date: Date | string,
  format: 'FULL' | 'SHORT' | 'TIME_ONLY' = 'FULL'
): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const options = DATE_FORMAT[format];
  return dateObj.toLocaleDateString('he-IL', options);
}

/**
 * Format duration in seconds to human-readable format
 * @param seconds - Duration in seconds
 * @returns Formatted string like "2 דקות 30 שניות"
 */
export function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${seconds} שניות`;
  }
  
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  
  if (remainingSeconds === 0) {
    return `${minutes} דקות`;
  }
  
  return `${minutes} דקות ${remainingSeconds} שניות`;
}

/**
 * Format relative time (e.g., "לפני 5 דקות")
 * @param date - Date object or ISO string
 * @returns Relative time string
 */
export function formatRelativeTime(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffMs = now.getTime() - dateObj.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);
  
  if (diffSec < 60) {
    return 'עכשיו';
  } else if (diffMin < 60) {
    return `לפני ${diffMin} דקות`;
  } else if (diffHour < 24) {
    return `לפני ${diffHour} שעות`;
  } else if (diffDay < 7) {
    return `לפני ${diffDay} ימים`;
  } else {
    return formatDate(dateObj, 'SHORT');
  }
}

/**
 * Truncate text to a maximum length
 * @param text - Text to truncate
 * @param maxLength - Maximum length
 * @param suffix - Suffix to add if truncated (default: "...")
 * @returns Truncated text
 */
export function truncateText(
  text: string,
  maxLength: number,
  suffix: string = '...'
): string {
  if (text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength - suffix.length) + suffix;
}

/**
 * Capitalize first letter of a string
 * @param text - Text to capitalize
 * @returns Capitalized text
 */
export function capitalizeFirst(text: string): string {
  if (!text) return '';
  return text.charAt(0).toUpperCase() + text.slice(1);
}

/**
 * Format percentage
 * @param value - Value between 0 and 1, or between 0 and 100
 * @param decimals - Number of decimal places (default: 0)
 * @returns Formatted percentage string like "45%"
 */
export function formatPercentage(value: number, decimals: number = 0): string {
  // If value is between 0 and 1, assume it's already a ratio
  const percentage = value > 1 ? value : value * 100;
  return `${percentage.toFixed(decimals)}%`;
}

/**
 * Format number with thousands separator
 * @param num - Number to format
 * @returns Formatted string like "1,234,567"
 */
export function formatNumber(num: number): string {
  return num.toLocaleString('he-IL');
}

/**
 * Parse ISO date string to Date object safely
 * @param dateString - ISO date string
 * @returns Date object or null if invalid
 */
export function parseDate(dateString: string): Date | null {
  try {
    const date = new Date(dateString);
    return isNaN(date.getTime()) ? null : date;
  } catch {
    return null;
  }
}

/**
 * Check if date is today
 * @param date - Date to check
 * @returns True if date is today
 */
export function isToday(date: Date | string): boolean {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const today = new Date();
  
  return (
    dateObj.getDate() === today.getDate() &&
    dateObj.getMonth() === today.getMonth() &&
    dateObj.getFullYear() === today.getFullYear()
  );
}

/**
 * Get greeting based on time of day
 * @returns Greeting string in Hebrew
 */
export function getTimeBasedGreeting(): string {
  const hour = new Date().getHours();
  
  if (hour < 12) {
    return 'בוקר טוב';
  } else if (hour < 18) {
    return 'צהריים טובים';
  } else {
    return 'ערב טוב';
  }
}