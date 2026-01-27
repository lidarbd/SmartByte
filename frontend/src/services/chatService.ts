/**
 * Chat Service
 * 
 * All API calls related to chat functionality
 */

import apiClient, { handleApiError } from './api';
import { API_CONFIG } from '../constants/config';
import type { SendMessageRequest, SendMessageResponse } from '../types/chat.types';

/**
 * Send a message to the chat API
 * 
 * @param request - Message request with session_id and message
 * @returns Promise with assistant response
 * @throws Error if request fails
 */
export async function sendMessage(
  request: SendMessageRequest
): Promise<SendMessageResponse> {
  try {
    console.log(`Sending message to API: ${request.message}`);
    const response = await apiClient.post<SendMessageResponse>(
      API_CONFIG.ENDPOINTS.SEND_MESSAGE,
      request
    );
    console.log(`Received response from API: ${response.data.assistant_message}`);
    
    return response.data;
  } catch (error) {
    const errorMessage = handleApiError(error);
    throw new Error(errorMessage);
  }
}

/**
 * Quick helper to send a message with just session ID and text
 * 
 * @param sessionId - Current session ID
 * @param message - User message text
 * @returns Promise with assistant response
 */
export async function sendChatMessage(
  sessionId: string,
  message: string
): Promise<SendMessageResponse> {
  return sendMessage({ session_id: sessionId, message });
}

/**
 * Test connection to chat API
 * 
 * @returns Promise with boolean indicating if API is reachable
 */
export async function testChatConnection(): Promise<boolean> {
  try {
    // Try to ping the API base URL
    await apiClient.get('/');
    return true;
  } catch {
    return false;
  }
}