import { forwardRef } from 'react';

const Input = forwardRef(
  (
    {
      label,
      error,
      helperText,
      fullWidth = false,
      className = '',
      ...props
    },
    ref
  ) => {
    const inputClasses = `
      block w-full px-3 py-2 border rounded-lg shadow-sm
      bg-white dark:bg-gray-800
      text-gray-900 dark:text-gray-100
      border-gray-300 dark:border-gray-600
      placeholder-gray-400 dark:placeholder-gray-500
      focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
      disabled:bg-gray-100 dark:disabled:bg-gray-700 disabled:cursor-not-allowed
      ${error ? 'border-red-500 focus:ring-red-500' : ''}
      ${className}
    `;

    return (
      <div className={fullWidth ? 'w-full' : ''}>
        {label && (
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {label}
            {props.required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}
        <input ref={ref} className={inputClasses} {...props} />
        {error && (
          <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>
        )}
        {helperText && !error && (
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;

