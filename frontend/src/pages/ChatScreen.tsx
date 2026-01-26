/**
 * ChatScreen Component
 * 
 * Main chat interface with real API connection
 * Includes messages, typing indicator, product recommendations
 */

import { useEffect, useRef } from 'react';
import { useChat } from '../hooks/useChat';
import Button from '../components/common/Button';
import ChatMessage from '../components/chat/Chatmessage';
import ChatInput from '../components/chat/ChatInput';
import TypingIndicator from '../components/chat/TypingIndicator';
import ProductCard from '../components/chat/ProductCard';
import EmptyState from '../components/chat/EmptyState';

export default function ChatScreen() {
  const {
    messages,
    recommendedProducts,
    upsellProduct,
    customerType,
    isTyping,
    error,
    sendMessage,
    clearChat,
    clearError,
  } = useChat();
  
  // Ref for auto-scrolling to bottom
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);
  
  // Handle sending a message
  const handleSend = async (message: string) => {
    await sendMessage(message);
  };
  
  const hasMessages = messages.length > 0;

  return (
    <div className="flex flex-col h-screen bg-gray-50" dir="rtl">
      
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-indigo-600 rounded-full flex items-center justify-center text-white font-bold">
            SB
          </div>
          <div>
            <h1 className="font-semibold text-gray-900">SmartByte Assistant</h1>
            <p className="text-xs text-gray-500">
              {customerType ? `${customerType} • ` : ''}מחובר
            </p>
          </div>
        </div>
        
        {/* Clear chat button */}
        {hasMessages && (
          <Button
            variant="secondary"
            size="sm"
            onClick={clearChat}
          >
            שיחה חדשה
          </Button>
        )}
      </div>
      
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-6">
          
          {/* Empty state */}
          {!hasMessages && (
            <EmptyState onSuggestionClick={handleSend} />
          )}
          
          {/* Messages */}
          {hasMessages && (
            <div className="space-y-1">
              {messages.map((message, index) => (
                <ChatMessage key={index} message={message} />
              ))}
              
              {/* Typing indicator */}
              {isTyping && <TypingIndicator />}
              
              {/* Auto-scroll anchor */}
              <div ref={messagesEndRef} />
            </div>
          )}
          
          {/* Error message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mt-4">
              <div className="flex items-start gap-2">
                <span className="text-red-600">⚠️</span>
                <div className="flex-1">
                  <p className="text-red-800 text-sm">{error}</p>
                  <button
                    onClick={clearError}
                    className="text-red-600 text-sm underline mt-1"
                  >
                    סגור
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {/* Product recommendations */}
          {recommendedProducts.length > 0 && (
            <div className="mt-6">
              <h3 className="font-semibold text-gray-900 mb-3">
                💡 המלצות מוצרים:
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {recommendedProducts.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            </div>
          )}
          
          {/* Upsell product */}
          {upsellProduct && (
            <div className="mt-6">
              <h3 className="font-semibold text-gray-900 mb-3">
                ✨ מוצר משלים מומלץ:
              </h3>
              <ProductCard product={upsellProduct} isUpsell />
            </div>
          )}
        </div>
      </div>
      
      {/* Input area */}
      <ChatInput
        onSend={handleSend}
        disabled={isTyping}
        placeholder={isTyping ? 'ממתין לתשובה...' : 'הקלד הודעה...'}
      />
    </div>
  );
}