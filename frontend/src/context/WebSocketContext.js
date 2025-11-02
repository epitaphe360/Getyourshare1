import React, { createContext, useContext, useEffect, useCallback } from 'react';
import { useWebSocket, EVENT_TYPES } from '../hooks/useWebSocket';
import { useNotification } from '../hooks/useNotification';
import { useAuth } from '../hooks/useAuth';
import { queryClient } from '../config/queryClient';
import { QUERY_KEYS } from '../hooks/useQueries';

/**
 * WebSocket Context
 */
const WebSocketContext = createContext(null);

/**
 * WebSocket Provider Component
 * 
 * Manages global WebSocket connection and event handlers
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components
 * @returns {JSX.Element}
 */
export const WebSocketProvider = ({ children }) => {
  const { user } = useAuth();
  const { success, info, warning } = useNotification();

  // Construire l'URL WebSocket à partir de l'URL backend
  const getWebSocketUrl = () => {
    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
    // Convertir http(s) en ws(s)
    const wsProtocol = backendUrl.startsWith('https') ? 'wss' : 'ws';
    const wsBase = backendUrl.replace(/^https?:\/\//, '');
    return `${wsProtocol}://${wsBase}/ws`;
  };

  const wsUrl = getWebSocketUrl();

  const ws = useWebSocket(wsUrl, {
    onOpen: () => {
      console.log('Connected to notification server');
      info('Connecté au serveur de notifications');
    },
    onClose: () => {
      console.log('Disconnected from notification server');
      warning('Déconnecté du serveur de notifications');
    },
    onError: (error) => {
      console.error('WebSocket error:', error);
    },
  });

  // Authenticate when user is available
  useEffect(() => {
    if (user && ws.isConnected) {
      ws.authenticate(user.id);
    }
  }, [user, ws.isConnected, ws]);

  /**
   * Handle commission created
   */
  useEffect(() => {
    const unsubscribe = ws.on(EVENT_TYPES.COMMISSION_CREATED, (data) => {
      console.log('Commission created:', data);
      
      success(`Nouvelle commission de ${data.amount}€ !`, {
        duration: 10000,
      });

      // Invalidate queries to refresh data
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.commissions });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.dashboardStats(user?.role) });
    });

    return unsubscribe;
  }, [ws, success, user]);

  /**
   * Handle commission updated
   */
  useEffect(() => {
    const unsubscribe = ws.on(EVENT_TYPES.COMMISSION_UPDATED, (data) => {
      console.log('Commission updated:', data);
      
      info(`Commission ${data.commission_id} mise à jour`);

      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.commissions });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.commission(data.commission_id) });
    });

    return unsubscribe;
  }, [ws, info]);

  /**
   * Handle payment created
   */
  useEffect(() => {
    const unsubscribe = ws.on(EVENT_TYPES.PAYMENT_CREATED, (data) => {
      console.log('Payment created:', data);
      
      success(`Nouveau paiement de ${data.amount}€ créé !`);

      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.payments });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.affiliateBalance(user?.id) });
    });

    return unsubscribe;
  }, [ws, success, user]);

  /**
   * Handle payment status changed
   */
  useEffect(() => {
    const unsubscribe = ws.on(EVENT_TYPES.PAYMENT_STATUS_CHANGED, (data) => {
      console.log('Payment status changed:', data);
      
      const statusMessages = {
        pending: 'en attente',
        processing: 'en cours de traitement',
        completed: 'complété',
        failed: 'échoué',
      };

      const message = `Paiement ${data.payment_id} ${statusMessages[data.status] || data.status}`;
      
      if (data.status === 'completed') {
        success(message);
      } else if (data.status === 'failed') {
        warning(message);
      } else {
        info(message);
      }

      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.payments });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.payment(data.payment_id) });
    });

    return unsubscribe;
  }, [ws, success, info, warning]);

  /**
   * Handle sale created
   */
  useEffect(() => {
    const unsubscribe = ws.on(EVENT_TYPES.SALE_CREATED, (data) => {
      console.log('Sale created:', data);
      
      info(`Nouvelle vente enregistrée : ${data.amount}€`);

      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.sales });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.dashboardStats(user?.role) });
    });

    return unsubscribe;
  }, [ws, info, user]);

  /**
   * Handle dashboard update
   */
  useEffect(() => {
    const unsubscribe = ws.on(EVENT_TYPES.DASHBOARD_UPDATE, (data) => {
      console.log('Dashboard update:', data);
      
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.dashboard });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.dashboardStats(user?.role) });
    });

    return unsubscribe;
  }, [ws, user]);

  return (
    <WebSocketContext.Provider value={ws}>
      {children}
    </WebSocketContext.Provider>
  );
};

/**
 * Hook to access WebSocket context
 * 
 * @returns {Object} WebSocket instance
 */
export const useWebSocketContext = () => {
  const context = useContext(WebSocketContext);
  
  if (!context) {
    throw new Error('useWebSocketContext must be used within WebSocketProvider');
  }
  
  return context;
};

export default WebSocketProvider;
