import { useState, useEffect, useCallback } from 'react';

/**
 * Custom hook for localStorage with state sync
 * 
 * Features:
 * - Automatic JSON serialization
 * - SSR-safe
 * - Event-based sync across tabs
 * - Error handling
 * 
 * @param {string} key - localStorage key
 * @param {any} initialValue - Initial value
 * @returns {Array} [value, setValue, removeValue]
 */
export const useLocalStorage = (key, initialValue) => {
  // Get initial value from localStorage
  const readValue = useCallback(() => {
    // SSR guard
    if (typeof window === 'undefined') {
      return initialValue;
    }

    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  }, [initialValue, key]);

  const [storedValue, setStoredValue] = useState(readValue);

  /**
   * Set value in localStorage and state
   * @param {any} value - Value to store
   */
  const setValue = useCallback(
    (value) => {
      // SSR guard
      if (typeof window === 'undefined') {
        console.warn(`Tried setting localStorage key "${key}" even though environment is not a client`);
        return;
      }

      try {
        // Allow value to be a function like useState
        const newValue = value instanceof Function ? value(storedValue) : value;

        // Save to localStorage
        window.localStorage.setItem(key, JSON.stringify(newValue));

        // Update state
        setStoredValue(newValue);

        // Dispatch custom event for sync across tabs
        window.dispatchEvent(
          new CustomEvent('local-storage', {
            detail: { key, newValue },
          })
        );
      } catch (error) {
        console.warn(`Error setting localStorage key "${key}":`, error);
      }
    },
    [key, storedValue]
  );

  /**
   * Remove value from localStorage
   */
  const removeValue = useCallback(() => {
    // SSR guard
    if (typeof window === 'undefined') {
      console.warn(`Tried removing localStorage key "${key}" even though environment is not a client`);
      return;
    }

    try {
      window.localStorage.removeItem(key);
      setStoredValue(initialValue);

      // Dispatch custom event
      window.dispatchEvent(
        new CustomEvent('local-storage', {
          detail: { key, newValue: null },
        })
      );
    } catch (error) {
      console.warn(`Error removing localStorage key "${key}":`, error);
    }
  }, [key, initialValue]);

  // Sync state with localStorage changes (including from other tabs)
  useEffect(() => {
    const handleStorageChange = (e) => {
      if (e.key === key || e.detail?.key === key) {
        setStoredValue(readValue());
      }
    };

    // Listen for changes from other tabs
    window.addEventListener('storage', handleStorageChange);
    
    // Listen for changes from same tab
    window.addEventListener('local-storage', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('local-storage', handleStorageChange);
    };
  }, [key, readValue]);

  return [storedValue, setValue, removeValue];
};

export default useLocalStorage;
