/**
 * ChatInput Component
 * 
 * Input field for typing and sending chat messages
 */

import { useState } from 'react';
import type { KeyboardEvent } from 'react';
import Button from '../common/Button';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export default function ChatInput({ 
  onSend, 
  disabled = false,
  placeholder = 'הקלד הודעה...'
}: ChatInputProps) {
  const [message, setMessage] = useState('');
  
  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage(''); // Clear input after sending
    }
  };
  
  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Send on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      <div className="flex gap-2 items-end">
        
        {/* Text input */}
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          className="flex-1 resize-none border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
          style={{
            minHeight: '44px',
            maxHeight: '120px',
          }}
        />
        
        {/* Send button */}
        <Button
          onClick={handleSend}
          disabled={disabled || !message.trim()}
          size="lg"
        >
          שלח
        </Button>
      </div>
      
      {/* Helper text */}
      <div className="text-xs text-gray-500 mt-2">
        <kbd className="px-2 py-1 bg-gray-100 rounded">Enter</kbd> לשליחה | 
        <kbd className="px-2 py-1 bg-gray-100 rounded ml-1">Shift+Enter</kbd> לשורה חדשה
      </div>
    </div>
  );
}