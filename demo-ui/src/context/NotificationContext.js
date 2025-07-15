import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import { useUser } from './UserContext';

// Constants
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const NATS_WS_URL = process.env.REACT_APP_NATS_WS_URL || 'ws://localhost:9222';

// Create context
const NotificationContext = createContext();

export function NotificationProvider({ children }) {
  const { currentUser } = useUser();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState(null);
  const [toasts, setToasts] = useState([]);
  const [hasMore, setHasMore] = useState(true);
  const [currentOffset, setCurrentOffset] = useState(0);
  const [currentFilters, setCurrentFilters] = useState({});
  const [connectionState, setConnectionState] = useState('disconnected'); // disconnected, connecting, connected, error
  
  // Use refs to avoid closure issues
  const currentOffsetRef = useRef(0);
  const currentFiltersRef = useRef({});
  
  // Keep refs in sync with state
  useEffect(() => {
    currentOffsetRef.current = currentOffset;
  }, [currentOffset]);
  
  useEffect(() => {
    currentFiltersRef.current = currentFilters;
  }, [currentFilters]);
  
  const PAGE_SIZE = 50; // Default page size
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  
  // Simple, stable fetch function
  const fetchNotifications = useCallback(async (filters = {}, reset = true) => {
    console.log(`🔍 fetchNotifications called for ${currentUser.name}, reset: ${reset}, filters:`, filters);
    
    try {
      if (reset) {
        setLoading(true);
        setCurrentFilters(filters);
        setCurrentOffset(0);
        currentOffsetRef.current = 0;
        currentFiltersRef.current = filters;
      } else {
        setLoadingMore(true);
      }
      
      const offset = reset ? 0 : currentOffsetRef.current;
      
      const params = new URLSearchParams({
        user_id: currentUser.id,
        limit: PAGE_SIZE.toString(),
        offset: offset.toString()
      });
      
      // Add filters to params
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          params.append(key, value.toString());
        }
      });
      
      console.log(`📡 API Call: GET ${API_URL}/notifications?${params.toString()}`);
      const response = await axios.get(`${API_URL}/notifications?${params}`, {
        timeout: 10000
      });
      
      if (reset) {
        setNotifications(response.data);
        setCurrentOffset(response.data.length);
        currentOffsetRef.current = response.data.length;
      } else {
        setNotifications(prev => [...prev, ...response.data]);
        const newOffset = currentOffsetRef.current + response.data.length;
        setCurrentOffset(newOffset);
        currentOffsetRef.current = newOffset;
      }
      
      setHasMore(response.data.length === PAGE_SIZE);
      
      if (reset) {
        const unread = response.data.filter(n => !n.is_read).length;
        setUnreadCount(unread);
      }
      
      setLoading(false);
      setLoadingMore(false);
    } catch (error) {
      console.error('Error fetching notifications:', error);
      setError('Failed to load notifications');
      setLoading(false);
      setLoadingMore(false);
    }
  }, [currentUser.id]); // Only depend on user ID

  // Load more notifications
  const loadMoreNotifications = useCallback(async () => {
    if (!hasMore || loadingMore) return;
    
    console.log(`🔍 loadMoreNotifications called for ${currentUser.name}, currentOffset: ${currentOffsetRef.current}`);
    
    try {
      setLoadingMore(true);
      
      const response = await axios.get(`${API_URL}/notifications`, {
        params: {
          user_id: currentUser.id,
          limit: PAGE_SIZE,
          offset: currentOffsetRef.current,
          ...currentFiltersRef.current
        },
        timeout: 10000
      });
      
      setNotifications(prev => [...prev, ...response.data]);
      const newOffset = currentOffsetRef.current + response.data.length;
      setCurrentOffset(newOffset);
      currentOffsetRef.current = newOffset;
      setHasMore(response.data.length === PAGE_SIZE);
      setLoadingMore(false);
    } catch (error) {
      console.error('Error loading more notifications:', error);
      setLoadingMore(false);
    }
  }, [hasMore, loadingMore, currentUser.id]); // Remove changing dependencies

  // Reset notifications when user changes
  useEffect(() => {
    setNotifications([]);
    setUnreadCount(0);
    setLoading(true);
    setError(null);
    setToasts([]); // Clear any existing toast notifications
    setHasMore(true);
    setCurrentOffset(0);
    setCurrentFilters({});
    setConnectionState('disconnected');
    
    // Add small delay to ensure previous user's connections are cleaned up
    const timer = setTimeout(() => {
      // Directly call the fetch logic without dependencies to avoid infinite loop
      const loadInitialNotifications = async () => {
        console.log(`🔄 Loading initial notifications for user: ${currentUser.name} (${currentUser.id})`);
        console.log(`📡 API Call: GET ${API_URL}/notifications?user_id=${currentUser.id}&limit=${PAGE_SIZE}&offset=0`);
        try {
          setLoading(true);
          const abortController = new AbortController();
          
          const response = await axios.get(`${API_URL}/notifications`, {
            params: {
              user_id: currentUser.id,
              limit: PAGE_SIZE,
              offset: 0
            },
            signal: abortController.signal,
            timeout: 10000
          });
          
          setNotifications(response.data);
          setHasMore(response.data.length === PAGE_SIZE);
          
          const unread = response.data.filter(n => !n.is_read).length;
          setUnreadCount(unread);
          setLoading(false);
        } catch (error) {
          if (error.name === 'AbortError') {
            console.log('Request aborted - likely due to user switch');
          } else {
            console.error('Error fetching notifications:', error);
            setError('Failed to load notifications');
          }
          setLoading(false);
        }
      };
      
      loadInitialNotifications();
    }, 100);
    
    return () => clearTimeout(timer);
  }, [currentUser.id]); // Only depend on currentUser.id to avoid infinite loop

  // Show toast notification
  const showToast = useCallback((notification) => {
    const newToast = {
      id: notification.id,
      title: notification.title,
      content: notification.content,
      severity: notification.severity,
      timestamp: new Date()
    };
    
    setToasts(prev => [newToast, ...prev]);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== newToast.id));
    }, 5000);
  }, []);

  // Remove toast
  const removeToast = useCallback((toastId) => {
    setToasts(prev => prev.filter(t => t.id !== toastId));
  }, []);

  // Connect to NATS for real-time updates
  useEffect(() => {
    let natsConnection = null;
    let subscription = null;
    let isConnecting = false;
    let isCancelled = false;
    
    async function connectToNats() {
      if (isConnecting || isCancelled) return;
      
      try {
        isConnecting = true;
        setConnectionState('connecting');
        console.log(`Connecting to NATS for user: ${currentUser.name}`);
        
        const { connect } = await import('nats.ws');
        
        // Check if component was unmounted or user changed during import
        if (isCancelled) {
          console.log('Connection cancelled during import');
          setConnectionState('disconnected');
          return;
        }
        
        natsConnection = await connect({
          servers: NATS_WS_URL,
          reconnect: false, // Disable auto-reconnect to prevent resource buildup
          maxReconnectAttempts: 0,
          pingInterval: 30000, // 30 seconds
          timeout: 5000 // 5 second connection timeout
        });
        
        // Check again if cancelled after connection
        if (isCancelled) {
          console.log('Connection cancelled after connect, closing immediately');
          await natsConnection.close();
          setConnectionState('disconnected');
          return;
        }
        
        setConnectionState('connected');
        console.log(`✅ Connected to NATS for user: ${currentUser.name}`);
        
        // Subscribe to user's notification channel
        subscription = natsConnection.subscribe(`notification.user.${currentUser.id}`);
        
        // Process incoming notifications
        (async () => {
          try {
            for await (const msg of subscription) {
              // Check if cancelled during message processing
              if (isCancelled) {
                console.log('Message processing cancelled');
                break;
              }
              
              const notification = JSON.parse(new TextDecoder().decode(msg.data));
              console.log('Received notification for', currentUser.name, ':', notification);
              
              // Add to notifications
              setNotifications(prev => [notification, ...prev]);
              
              // Update unread count
              setUnreadCount(prev => prev + 1);
              
              // Show toast
              showToast(notification);
            }
          } catch (error) {
            if (!isCancelled) {
              console.error('Error in message processing:', error);
            }
          }
        })();
        
      } catch (error) {
        if (!isCancelled) {
          console.error('Error connecting to NATS:', error);
          setConnectionState('error');
          setError('Failed to connect to notification service. Real-time updates disabled.');
        }
      } finally {
        isConnecting = false;
      }
    }
    
    // Start connection
    connectToNats();
    
    // Cleanup function with improved resource management
    return () => {
      console.log(`🧹 Cleaning up NATS connection for user: ${currentUser.name}`);
      isCancelled = true;
      setConnectionState('disconnected');
      
      // Cleanup subscription first
      if (subscription) {
        try {
          subscription.unsubscribe();
          console.log('✅ Subscription unsubscribed');
        } catch (error) {
          console.warn('Warning during subscription cleanup:', error);
        }
        subscription = null;
      }
      
      // Then close connection with proper async handling
      if (natsConnection) {
        try {
          // Use setTimeout to ensure cleanup doesn't block
          setTimeout(async () => {
            try {
              await natsConnection.close();
              console.log('✅ NATS connection closed');
            } catch (error) {
              console.warn('Warning during async connection cleanup:', error);
            }
          }, 0);
        } catch (error) {
          console.warn('Warning during connection cleanup:', error);
        }
        natsConnection = null;
      }
    };
  }, [currentUser.id, showToast]); // Add showToast dependency

  // Mark notification as read
  const markAsRead = useCallback(async (notificationId) => {
    try {
      await axios.post(`${API_URL}/notifications/${notificationId}/read`, {}, {
        headers: {
          'X-User-ID': currentUser.id
        }
      });
      
      // Update local state
      setNotifications(prev => 
        prev.map(n => 
          n.id === notificationId ? { ...n, is_read: true } : n
        )
      );
      
      // Update unread count
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  }, [currentUser.id]);

  // Bulk mark notifications as read
  const bulkMarkAsRead = useCallback(async (notificationIds) => {
    try {
      await axios.post(`${API_URL}/notifications/bulk-read`, {
        notification_ids: notificationIds
      }, {
        headers: {
          'X-User-ID': currentUser.id
        }
      });
      
      // Update local state
      setNotifications(prev => 
        prev.map(n => 
          notificationIds.includes(n.id) ? { ...n, is_read: true } : n
        )
      );
      
      // Update unread count
      const markedCount = notificationIds.length;
      setUnreadCount(prev => Math.max(0, prev - markedCount));
    } catch (error) {
      console.error('Error bulk marking notifications as read:', error);
      throw error;
    }
  }, [currentUser.id]);

  // Mark all notifications as read
  const markAllAsRead = useCallback(async () => {
    try {
      const unreadNotifications = notifications.filter(n => !n.is_read);
      const unreadIds = unreadNotifications.map(n => n.id);
      
      if (unreadIds.length === 0) return;
      
      await bulkMarkAsRead(unreadIds);
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      throw error;
    }
  }, [notifications, bulkMarkAsRead]);

  // Subscribe to a path
  const subscribe = useCallback(async (path, includeChildren = true) => {
    try {
      const response = await axios.post(`${API_URL}/subscriptions`, {
        path,
        include_children: includeChildren,
      }, {
        headers: {
          'X-User-ID': currentUser.id
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Error creating subscription:', error);
      throw error;
    }
  }, [currentUser.id]);

  // Unsubscribe from a path
  const unsubscribe = useCallback(async (subscriptionId) => {
    try {
      await axios.delete(`${API_URL}/subscriptions/${subscriptionId}`, {
        headers: {
          'X-User-ID': currentUser.id
        }
      });
    } catch (error) {
      console.error('Error deleting subscription:', error);
      throw error;
    }
  }, [currentUser.id]);

  // Check subscription status
  const checkSubscription = useCallback(async (path) => {
    try {
      const response = await axios.get(`${API_URL}/subscriptions/check?path=${encodeURIComponent(path)}`, {
        headers: {
          'X-User-ID': currentUser.id
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error checking subscription:', error);
      throw error;
    }
  }, [currentUser.id]);

  // Get all subscriptions
  const getSubscriptions = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/subscriptions`, {
        headers: {
          'X-User-ID': currentUser.id
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching subscriptions:', error);
      throw error;
    }
  }, [currentUser.id]);

  // Context value
  const value = {
    notifications,
    unreadCount,
    loading,
    loadingMore,
    error,
    toasts,
    hasMore,
    connectionState,
    currentUser,
    fetchNotifications,
    loadMoreNotifications,
    markAsRead,
    bulkMarkAsRead,
    markAllAsRead,
    subscribe,
    unsubscribe,
    checkSubscription,
    getSubscriptions,
    removeToast
  };
  
  return (
    <NotificationContext.Provider value={value}>
      {children}
      
      {/* Toast container */}
      <div className="toast-container">
        {toasts.map(toast => (
          <div 
            key={toast.id} 
            className={`toast show notification-item severity-${toast.severity}`}
            role="alert"
          >
            <div className="toast-header">
              <strong className="me-auto">{toast.title}</strong>
              <small>{new Date(toast.timestamp).toLocaleTimeString()}</small>
              <button 
                type="button" 
                className="btn-close" 
                onClick={() => removeToast(toast.id)}
              ></button>
            </div>
            <div className="toast-body">
              {toast.content}
            </div>
          </div>
        ))}
      </div>
    </NotificationContext.Provider>
  );
}

// Custom hook to use the notification context
export function useNotifications() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
}
