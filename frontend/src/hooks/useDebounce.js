import { useState, useEffect } from 'react';

/**
 * Custom hook for debouncing values
 * 
 * Delays updating the value until after the specified delay
 * Useful for search inputs, resize handlers, etc.
 * 
 * @param {any} value - Value to debounce
 * @param {number} delay - Delay in milliseconds
 * @returns {any} Debounced value
 */
export const useDebounce = (value, delay = 500) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    // Set up timeout
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // Clean up timeout on value change or unmount
    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

/**
 * Custom hook for debounced callback
 * 
 * Returns a memoized callback that is debounced
 * 
 * @param {Function} callback - Callback to debounce
 * @param {number} delay - Delay in milliseconds
 * @param {Array} dependencies - Dependency array
 * @returns {Function} Debounced callback
 */
export const useDebouncedCallback = (callback, delay = 500, dependencies = []) => {
  const [timeoutId, setTimeoutId] = useState(null);

  useEffect(() => {
    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [timeoutId]);

  const debouncedCallback = (...args) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    const id = setTimeout(() => {
      callback(...args);
    }, delay);

    setTimeoutId(id);
  };

  return debouncedCallback;
};

export default useDebounce;
