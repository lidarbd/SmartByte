/**
 * ChatMessage Component
 * 
 * Displays a single chat message from either user or assistant
 */

import type { Message } from '../../types/chat.types';
import { formatDate } from '../../utils/formatters';

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[70%] ${isUser ? 'order-2' : 'order-1'}`}>
        
        {/* Message bubble */}
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? 'bg-indigo-600 text-white rounded-br-none'
              : 'bg-gray-100 text-gray-800 rounded-bl-none'
          }`}
        >
          <p className="text-sm md:text-base whitespace-pre-wrap break-words">
            {message.content}
          </p>
        </div>
        
        {/* Timestamp */}
        <div
          className={`text-xs text-gray-500 mt-1 px-2 ${
            isUser ? 'text-right' : 'text-left'
          }`}
        >
          {formatDate(message.timestamp, 'TIME_ONLY')}
        </div>
      </div>
    </div>
  );
}