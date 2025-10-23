import { useState, useCallback } from 'react';

export const useToast = () => {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'success', options = {}) => {
    const id = Date.now();
    const toast = {
      id,
      message,
      type,
      duration: options.duration !== undefined ? options.duration : 3000,
      action: options.action
    };

    setToasts(prev => [...prev, toast]);
    return id;
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  const success = useCallback((message, options) => {
    return addToast(message, 'success', options);
  }, [addToast]);

  const error = useCallback((message, options) => {
    return addToast(message, 'error', options);
  }, [addToast]);

  const info = useCallback((message, options) => {
    return addToast(message, 'info', options);
  }, [addToast]);

  const warning = useCallback((message, options) => {
    return addToast(message, 'warning', options);
  }, [addToast]);

  return {
    toasts,
    addToast,
    removeToast,
    success,
    error,
    info,
    warning
  };
};
