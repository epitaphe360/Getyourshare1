import { useEffect, useRef, useCallback, useState } from 'react';

/**
 * WebSocket connection states
 */
export const WS_STATES = {
  CONNECTING: 0,
  OPEN: 1,
  CLOSING: 2,
  CLOSED: 3,
};

/**
 * Event types
 */
export const EVENT_TYPES = {
  COMMISSION_CREATED: 'commission_created',
  COMMISSION_UPDATED: 'commission_updated',
  PAYMENT_CREATED: 'payment_created',
  PAYMENT_STATUS_CHANGED: 'payment_status_changed',
  SALE_CREATED: 'sale_created',
  DASHBOARD_UPDATE: 'dashboard_update',
};

/**
 * Custom hook for WebSocket connection
 * 
 * Features:
 * - Auto-reconnect on disconnect
 * - Event listeners
 * - Heartbeat/ping-pong
 * - Connection state management
 * 
 * @param {string} url - WebSocket URL
 * @param {Object} options - Configuration options
 * @returns {Object} WebSocket state and methods
 */
export const useWebSocket = (url, options = {}) => {
  const {
    onOpen,
    onClose,
    onError,
    onMessage,
    reconnectInterval = 3000,
    reconnectAttempts = 5,
    heartbeatInterval = 30000,
  } = options;

  const [readyState, setReadyState] = useState(WS_STATES.CLOSED);
  const [lastMessage, setLastMessage] = useState(null);
  const wsRef = useRef(null);
  const reconnectCountRef = useRef(0);
  const reconnectTimeoutRef = useRef(null);
  const heartbeatIntervalRef = useRef(null);
  const eventListenersRef = useRef({});

  /**
   * Send message through WebSocket
   * @param {Object} data - Data to send
   */
  const sendMessage = useCallback((data) => {
    if (wsRef.current && wsRef.current.readyState === WS_STATES.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  /**
   * Start heartbeat
   */
  const startHeartbeat = useCallback(() => {
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
    }

    heartbeatIntervalRef.current = setInterval(() => {
      sendMessage({ type: 'ping' });
    }, heartbeatInterval);
  }, [heartbeatInterval, sendMessage]);

  /**
   * Stop heartbeat
   */
  const stopHeartbeat = useCallback(() => {
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
      heartbeatIntervalRef.current = null;
    }
  }, []);

  /**
   * Connect to WebSocket
   */
  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(url);

      ws.onopen = (event) => {
        console.log('WebSocket connected');
        setReadyState(WS_STATES.OPEN);
        reconnectCountRef.current = 0;
        startHeartbeat();
        onOpen?.(event);
      };

      ws.onclose = (event) => {
        console.log('WebSocket disconnected');
        setReadyState(WS_STATES.CLOSED);
        stopHeartbeat();
        onClose?.(event);

        // Auto-reconnect
        if (reconnectCountRef.current < reconnectAttempts) {
          reconnectCountRef.current += 1;
          console.log(`Reconnecting... Attempt ${reconnectCountRef.current}`);
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        onError?.(event);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
          onMessage?.(data);

          // Trigger event-specific listeners
          const eventType = data.type;
          if (eventType && eventListenersRef.current[eventType]) {
            eventListenersRef.current[eventType].forEach((listener) => {
              listener(data.data);
            });
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      wsRef.current = ws;
      setReadyState(WS_STATES.CONNECTING);
    } catch (error) {
      console.error('Error creating WebSocket:', error);
    }
  }, [url, onOpen, onClose, onError, onMessage, reconnectAttempts, reconnectInterval, startHeartbeat, stopHeartbeat]);

  /**
   * Disconnect from WebSocket
   */
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    stopHeartbeat();

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, [stopHeartbeat]);

  /**
   * Subscribe to specific event type
   * @param {string} eventType - Event type to listen for
   * @param {Function} listener - Callback function
   * @returns {Function} Unsubscribe function
   */
  const on = useCallback((eventType, listener) => {
    if (!eventListenersRef.current[eventType]) {
      eventListenersRef.current[eventType] = [];
    }

    eventListenersRef.current[eventType].push(listener);

    // Return unsubscribe function
    return () => {
      eventListenersRef.current[eventType] = eventListenersRef.current[eventType].filter(
        (l) => l !== listener
      );
    };
  }, []);

  /**
   * Authenticate with server
   * @param {string} userId - User ID
   */
  const authenticate = useCallback(
    (userId) => {
      sendMessage({
        type: 'auth',
        user_id: userId,
      });
    },
    [sendMessage]
  );

  // Connect on mount
  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    readyState,
    lastMessage,
    sendMessage,
    connect,
    disconnect,
    on,
    authenticate,
    isConnected: readyState === WS_STATES.OPEN,
  };
};

export default useWebSocket;
