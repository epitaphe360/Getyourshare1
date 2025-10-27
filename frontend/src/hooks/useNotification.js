import { useState, useCallback } from 'react';

/**
 * Custom hook for notification management
 * 
 * Features:
 * - Success/Error/Info/Warning notifications
 * - Auto-dismiss
 * - Stack management
 * - Custom duration
 * 
 * @returns {Object} Notification state and methods
 */
export const useNotification = () => {
  const [notifications, setNotifications] = useState([]);

  /**
   * Add notification
   * @param {Object} notification - Notification config
   * @returns {string} Notification ID
   */
  const addNotification = useCallback((notification) => {
    const id = Date.now().toString() + Math.random().toString(36).substr(2, 9);
    const newNotification = {
      id,
      type: 'info',
      duration: 5000,
      ...notification,
    };

    setNotifications((prev) => [...prev, newNotification]);

    // Auto-dismiss
    if (newNotification.duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, newNotification.duration);
    }

    return id;
  }, []);

  /**
   * Remove notification
   * @param {string} id - Notification ID
   */
  const removeNotification = useCallback((id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  /**
   * Clear all notifications
   */
  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  /**
   * Show success notification
   * @param {string} message - Message
   * @param {Object} options - Options
   * @returns {string} Notification ID
   */
  const success = useCallback(
    (message, options = {}) => {
      return addNotification({
        type: 'success',
        message,
        ...options,
      });
    },
    [addNotification]
  );

  /**
   * Show error notification
   * @param {string} message - Message
   * @param {Object} options - Options
   * @returns {string} Notification ID
   */
  const error = useCallback(
    (message, options = {}) => {
      return addNotification({
        type: 'error',
        message,
        duration: 7000, // Longer duration for errors
        ...options,
      });
    },
    [addNotification]
  );

  /**
   * Show info notification
   * @param {string} message - Message
   * @param {Object} options - Options
   * @returns {string} Notification ID
   */
  const info = useCallback(
    (message, options = {}) => {
      return addNotification({
        type: 'info',
        message,
        ...options,
      });
    },
    [addNotification]
  );

  /**
   * Show warning notification
   * @param {string} message - Message
   * @param {Object} options - Options
   * @returns {string} Notification ID
   */
  const warning = useCallback(
    (message, options = {}) => {
      return addNotification({
        type: 'warning',
        message,
        ...options,
      });
    },
    [addNotification]
  );

  return {
    notifications,
    addNotification,
    removeNotification,
    clearNotifications,
    success,
    error,
    info,
    warning,
  };
};

export default useNotification;
