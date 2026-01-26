/**
 * Button Component
 * 
 * A styled button using Tailwind CSS
 * Supports different variants (primary, secondary) and sizes (sm, md, lg)
 */

import React from 'react';

// Props that the button can receive
interface ButtonProps {
  children: React.ReactNode;           // Content inside the button
  onClick?: () => void;                // Click handler
  variant?: 'primary' | 'secondary';   // Button style variant
  size?: 'sm' | 'md' | 'lg';          // Button size
  disabled?: boolean;                  // Whether button is disabled
  fullWidth?: boolean;                 // Whether button takes full width
  type?: 'button' | 'submit' | 'reset'; // HTML button type (for forms)
}

export default function Button({
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  disabled = false,
  fullWidth = false,
  type = 'button',
}: ButtonProps) {
  
  // Base styles - common to all buttons
  const baseStyles = 'font-medium rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed';
  
  // Styles per variant
  const variantStyles = {
    primary: 'bg-indigo-600 text-white hover:bg-indigo-700 active:bg-indigo-800',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300 active:bg-gray-400',
  };
  
  // Styles per size
  const sizeStyles = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };
  
  // Full width if requested
  const widthStyle = fullWidth ? 'w-full' : '';
  
  // Combine all styles
  const className = `${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${widthStyle}`;

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={className}
    >
      {children}
    </button>
  );
}