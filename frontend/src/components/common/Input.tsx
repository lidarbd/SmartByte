/**
 * Input Component
 * 
 * A styled text input using Tailwind CSS
 * Supports labels, error states, placeholders, and different sizes
 */

import React from 'react';

// Props that the input can receive
interface InputProps {
  label?: string;                      // Label text above the input
  placeholder?: string;                // Placeholder text inside input
  value: string;                       // Current value
  onChange: (value: string) => void;   // Handler when value changes
  error?: string;                      // Error message to display
  disabled?: boolean;                  // Whether input is disabled
  size?: 'sm' | 'md' | 'lg';          // Input size
  fullWidth?: boolean;                 // Whether input takes full width
  type?: 'text' | 'email' | 'password' | 'number'; // HTML input type
  maxLength?: number;                  // Maximum character length
  rows?: number;                       // Number of rows (for textarea mode)
  multiline?: boolean;                 // Whether to use textarea instead of input
}

export default function Input({
  label,
  placeholder,
  value,
  onChange,
  error,
  disabled = false,
  size = 'md',
  fullWidth = false,
  type = 'text',
  maxLength,
  rows = 3,
  multiline = false,
}: InputProps) {
  
  // Base styles - common to all inputs
  const baseStyles = 'border rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 disabled:opacity-50 disabled:cursor-not-allowed';
  
  // Border color based on error state
  const borderStyles = error 
    ? 'border-red-500 focus:border-red-500 focus:ring-red-200'
    : 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-200';
  
  // Styles per size
  const sizeStyles = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-5 py-3 text-lg',
  };
  
  // Full width if requested
  const widthStyle = fullWidth ? 'w-full' : '';
  
  // Combine all styles
  const inputClassName = `${baseStyles} ${borderStyles} ${sizeStyles[size]} ${widthStyle}`;
  
  // Handler for input changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    onChange(e.target.value);
  };

  return (
    <div className={`flex flex-col gap-1 ${fullWidth ? 'w-full' : ''}`}>
      
      {/* Label (if provided) */}
      {label && (
        <label className="text-sm font-medium text-gray-700">
          {label}
        </label>
      )}
      
      {/* Input or Textarea */}
      {multiline ? (
        <textarea
          value={value}
          onChange={handleChange}
          placeholder={placeholder}
          disabled={disabled}
          maxLength={maxLength}
          rows={rows}
          className={inputClassName}
        />
      ) : (
        <input
          type={type}
          value={value}
          onChange={handleChange}
          placeholder={placeholder}
          disabled={disabled}
          maxLength={maxLength}
          className={inputClassName}
        />
      )}
      
      {/* Character count (if maxLength is set) */}
      {maxLength && (
        <div className="text-xs text-gray-500 text-right">
          {value.length} / {maxLength}
        </div>
      )}
      
      {/* Error message (if provided) */}
      {error && (
        <span className="text-sm text-red-600">
          {error}
        </span>
      )}
    </div>
  );
}