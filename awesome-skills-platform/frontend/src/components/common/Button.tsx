import type { ButtonHTMLAttributes, ReactNode } from 'react';
import clsx from 'clsx';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  icon?: ReactNode;
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  icon,
  className,
  disabled,
  ...props
}: ButtonProps) {
  return (
    <button
      className={clsx(
        'inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-all',
        'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-bg-dark',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        {
          // Primary variant
          'bg-primary text-white hover:bg-blue-600 active:bg-blue-700':
            variant === 'primary' && !disabled,

          // Secondary variant
          'bg-gray-700 text-white hover:bg-gray-600 active:bg-gray-800':
            variant === 'secondary' && !disabled,

          // Ghost variant
          'bg-transparent text-gray-300 hover:bg-gray-800 active:bg-gray-700':
            variant === 'ghost' && !disabled,

          // Danger variant
          'bg-red-600 text-white hover:bg-red-700 active:bg-red-800':
            variant === 'danger' && !disabled,

          // Sizes
          'px-3 py-1.5 text-sm': size === 'sm',
          'px-4 py-2 text-base': size === 'md',
          'px-6 py-3 text-lg': size === 'lg',
        },
        className
      )}
      disabled={disabled}
      {...props}
    >
      {icon && <span className="flex-shrink-0">{icon}</span>}
      {children}
    </button>
  );
}
