/**
 * Chat Types
 *
 * All TypeScript interfaces and types related to the chat functionality
 */

import type { Product, CustomerType } from './common.types';

/**
 * Message role - who sent the message
 */
export type MessageRole = 'user' | 'assistant';

/**
 * Single chat message
 */
export interface Message {
  role: MessageRole;
  content: string;
  timestamp: Date;
}

/**
 * API request to send a message
 */
export interface SendMessageRequest {
  session_id: string;
  message: string;
}

/**
 * API response from sending a message
 */
export interface SendMessageResponse {
  assistant_message: string;
  customer_type?: CustomerType;
  recommended_items: Product[];
  upsell_item?: Product | null;
}

/**
 * Complete chat session data
 */
export interface ChatSession {
  sessionId: string;
  messages: Message[];
  customerType?: CustomerType;
  recommendedProducts: Product[];
  upsellProduct?: Product | null;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Chat state for UI
 */
export interface ChatState {
  session: ChatSession | null;
  isLoading: boolean;
  isTyping: boolean;
  error: string | null;
}