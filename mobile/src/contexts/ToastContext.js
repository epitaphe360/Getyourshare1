/**
 * Toast Context
 * Shows toast notifications across the app
 */

import React, {createContext, useContext, useState} from 'react';
import {Snackbar} from 'react-native-paper';

const ToastContext = createContext();

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

export const ToastProvider = ({children}) => {
  const [visible, setVisible] = useState(false);
  const [message, setMessage] = useState('');
  const [type, setType] = useState('info'); // success, error, info, warning

  const showToast = (msg, toastType = 'info') => {
    setMessage(msg);
    setType(toastType);
    setVisible(true);
  };

  const hideToast = () => {
    setVisible(false);
  };

  const success = (msg) => showToast(msg, 'success');
  const error = (msg) => showToast(msg, 'error');
  const info = (msg) => showToast(msg, 'info');
  const warning = (msg) => showToast(msg, 'warning');

  const getBackgroundColor = () => {
    switch (type) {
      case 'success':
        return '#4caf50';
      case 'error':
        return '#f44336';
      case 'warning':
        return '#ff9800';
      default:
        return '#2196f3';
    }
  };

  const value = {
    showToast,
    success,
    error,
    info,
    warning,
  };

  return (
    <ToastContext.Provider value={value}>
      {children}
      <Snackbar
        visible={visible}
        onDismiss={hideToast}
        duration={3000}
        style={{backgroundColor: getBackgroundColor()}}
        action={{
          label: 'OK',
          onPress: hideToast,
        }}>
        {message}
      </Snackbar>
    </ToastContext.Provider>
  );
};

export default ToastContext;
