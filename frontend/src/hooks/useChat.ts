/**
 * useChat Hook
 * 
 * Custom hook for managing chat state and interactions
 */

import { useState, useCallback, useEffect } from 'react';
import type { ChatState, ChatSession, Message, Product } from '../types/chat.types';
import { sendChatMessage } from '../services/chatService';
import { getOrCreateSessionId, saveToStorage, loadFromStorage } from '../utils/storage';
import { STORAGE_KEYS, UI_CONFIG } from '../constants/config';

/**
 * Hook for chat functionality
 */
export function useChat() {
  // Initialize state
  const [state, setState] = useState<ChatState>({
    session: null,
    isLoading: false,
    isTyping: false,
    error: null,
  });

  /**
   * Initialize or load existing chat session
   */
  useEffect(() => {
    const sessionId = getOrCreateSessionId();
    
    // Try to load existing chat history from storage
    const savedHistory = loadFromStorage<Message[]>(STORAGE_KEYS.CHAT_HISTORY);
    
    const session: ChatSession = {
      sessionId,
      messages: savedHistory || [],
      recommendedProducts: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    
    setState((prev) => ({ ...prev, session }));
  }, []);

  /**
   * Save messages to storage whenever they change
   */
  useEffect(() => {
    if (state.session) {
      saveToStorage(STORAGE_KEYS.CHAT_HISTORY, state.session.messages);
    }
  }, [state.session?.messages]);

  /**
   * Add a message to the chat
   */
  const addMessage = useCallback((role: 'user' | 'assistant', content: string) => {
    setState((prev) => {
      if (!prev.session) return prev;

      const newMessage: Message = {
        role,
        content,
        timestamp: new Date(),
      };

      return {
        ...prev,
        session: {
          ...prev.session,
          messages: [...prev.session.messages, newMessage],
          updatedAt: new Date(),
        },
      };
    });
  }, []);

  /**
   * Update recommended products
   */
  const updateRecommendedProducts = useCallback((products: Product[], upsell?: Product | null) => {
    setState((prev) => {
      if (!prev.session) return prev;

      return {
        ...prev,
        session: {
          ...prev.session,
          recommendedProducts: products,
          upsellProduct: upsell,
          updatedAt: new Date(),
        },
      };
    });
  }, []);

  /**
   * Send a message to the API
   */
  const sendMessage = useCallback(async (message: string) => {
    if (!state.session) {
      setState((prev) => ({ ...prev, error: 'Session not initialized' }));
      return;
    }

    // Add user message immediately
    addMessage('user', message);

    // Set loading state
    setState((prev) => ({ ...prev, isLoading: true, isTyping: true, error: null }));

    try {
      // Call API
      const response = await sendChatMessage(state.session.sessionId, message);

      // Simulate typing delay for better UX
      await new Promise((resolve) => setTimeout(resolve, UI_CONFIG.CHAT.TYPING_DELAY_MS));

      // Add assistant response
      addMessage('assistant', response.assistant_message);

      // Update customer type if identified
      if (response.customer_type) {
        setState((prev) => {
          if (!prev.session) return prev;
          return {
            ...prev,
            session: {
              ...prev.session,
              customerType: response.customer_type,
            },
          };
        });
      }

      // Update recommended products
      updateRecommendedProducts(
        response.recommended_items,
        response.upsell_item
      );

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to send message';
      setState((prev) => ({ ...prev, error: errorMessage }));
    } finally {
      setState((prev) => ({ ...prev, isLoading: false, isTyping: false }));
    }
  }, [state.session, addMessage, updateRecommendedProducts]);

  /**
   * Clear the chat session
   */
  const clearChat = useCallback(() => {
    const sessionId = getOrCreateSessionId();
    
    const newSession: ChatSession = {
      sessionId,
      messages: [],
      recommendedProducts: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    setState({
      session: newSession,
      isLoading: false,
      isTyping: false,
      error: null,
    });

    // Clear storage
    saveToStorage(STORAGE_KEYS.CHAT_HISTORY, []);
  }, []);

  /**
   * Clear error
   */
  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  return {
    // State
    session: state.session,
    messages: state.session?.messages || [],
    recommendedProducts: state.session?.recommendedProducts || [],
    upsellProduct: state.session?.upsellProduct,
    customerType: state.session?.customerType,
    isLoading: state.isLoading,
    isTyping: state.isTyping,
    error: state.error,

    // Actions
    sendMessage,
    clearChat,
    clearError,
  };
}