import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
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
  const [error, setError] = useState(null);
  const [toasts, setToasts] = useState([]);
  
  // Fetch notifications from API
  const fetchNotifications = useCallback(async (filters = {}) => {
    try {
      setLoading(true);
      
      const params = new URLSearchParams({
        ...filters,
        user_id: currentUser.id
      });
      
      const response = await axios.get(`${API_URL}/notifications?${params}`);
      
      setNotifications(response.data);
      
      // Count unread
      const unread = response.data.filter(n => !n.is_read).length;
      setUnreadCount(unread);
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching notifications:', error);
      setError('Failed to load notifications');
      setLoading(false);
    }
  }, [currentUser.id]);

  // Reset notifications when user changes
  useEffect(() => {
    setNotifications([]);
    setUnreadCount(0);
    setLoading(true);
    setError(null);
    setToasts([]); // Clear any existing toast notifications
    fetchNotifications();
  }, [currentUser.id, fetchNotifications]);

  // Connect to NATS for real-time updates
  useEffect(() => {
    let natsConnection = null;
    let subscription = null;
    
    async function connectToNats() {
      try {
        const { connect } = await import('nats.ws');
        
        natsConnection = await connect({
          servers: NATS_WS_URL
        });
        
        console.log(`Connected to NATS for user: ${currentUser.name}`);
        
        // Subscribe to user's notification channel
        subscription = natsConnection.subscribe(`notification.user.${currentUser.id}`);
        
        // Process incoming notifications
        (async () => {
          for await (const msg of subscription) {
            const notification = JSON.parse(new TextDecoder().decode(msg.data));
            console.log('Received notification for', currentUser.name, ':', notification);
            
            // Add to notifications
            setNotifications(prev => [notification, ...prev]);
            
            // Update unread count
            setUnreadCount(prev => prev + 1);
            
            // Show toast
            showToast(notification);
          }
        })();
      } catch (error) {
        console.error('Error connecting to NATS:', error);
        setError('Failed to connect to notification service. Real-time updates disabled.');
      }
    }
    
    connectToNats();
    
    // Cleanup on unmount or user change
    return () => {
      if (subscription) {
        subscription.unsubscribe();
      }
      if (natsConnection) {
        natsConnection.close();
      }
    };
  }, [currentUser.id]); // Re-connect when user changes

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

  // Context value
  const value = {
    notifications,
    unreadCount,
    loading,
    error,
    toasts,
    fetchNotifications,
    markAsRead,
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
