import React, { useState, useEffect, useRef } from 'react';
import { useNotifications } from '../context/NotificationContext';
import { useUser } from '../context/UserContext';
import { FaBell, FaEye, FaExternalLinkAlt } from 'react-icons/fa';
import { Link } from 'react-router-dom';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function NotificationDropdown() {
  const [isOpen, setIsOpen] = useState(false);
  const [recentNotifications, setRecentNotifications] = useState([]);
  const [loading, setLoading] = useState(false);
  const dropdownRef = useRef(null);
  
  const { currentUser } = useUser();
  const { 
    unreadCount, 
    markAsRead
  } = useNotifications();

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Fetch recent notifications when dropdown opens
  const fetchRecentNotifications = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/notifications?limit=10`, {
        headers: {
          'X-User-ID': currentUser.id
        }
      });
      setRecentNotifications(response.data || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching recent notifications:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchRecentNotifications();
    }
  }, [isOpen, currentUser.id]);

  // Clear notifications when user changes
  useEffect(() => {
    setRecentNotifications([]);
    setIsOpen(false); // Close dropdown when switching users
  }, [currentUser.id]);

  const handleBellClick = (e) => {
    e.preventDefault();
    setIsOpen(!isOpen);
  };

  const handleMarkAsRead = (notification) => {
    markAsRead(notification.id);
    // Update local state
    setRecentNotifications(prev => 
      prev.map(n => 
        n.id === notification.id 
          ? { ...n, is_read: true }
          : n
      )
    );
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const notificationTime = new Date(timestamp);
    const diffInMinutes = Math.floor((now - notificationTime) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'error': return 'text-danger';
      case 'warning': return 'text-warning';
      case 'info': return 'text-info';
      case 'critical': return 'text-danger fw-bold';
      default: return 'text-secondary';
    }
  };

  const truncateText = (text, maxLength = 80) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <div className="position-relative" ref={dropdownRef}>
      {/* Bell Button */}
      <button 
        className="btn btn-outline-light position-relative"
        onClick={handleBellClick}
        style={{ border: 'none' }}
      >
        <FaBell />
        {unreadCount > 0 && (
          <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
            {unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div 
          className="position-absolute bg-white border shadow-lg rounded"
          style={{
            top: '100%',
            right: '0',
            width: '400px',
            maxHeight: '500px',
            overflowY: 'auto',
            zIndex: 1050,
            marginTop: '0.5rem'
          }}
        >
          {/* Header */}
          <div className="d-flex justify-content-between align-items-center p-3 border-bottom bg-light">
            <h6 className="mb-0 text-dark">
              <FaBell className="me-2" />
              Notifications
            </h6>
            <div className="d-flex gap-2">
              <span className="badge bg-primary">{unreadCount} unread</span>
              <Link 
                to="/notifications" 
                className="btn btn-sm btn-outline-primary"
                onClick={() => setIsOpen(false)}
              >
                <FaExternalLinkAlt className="me-1" />
                View All
              </Link>
            </div>
          </div>

          {/* Loading */}
          {loading && (
            <div className="text-center p-4">
              <div className="spinner-border spinner-border-sm text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
              <div className="mt-2 text-muted">Loading notifications...</div>
            </div>
          )}

          {/* No Notifications */}
          {!loading && recentNotifications.length === 0 && (
            <div className="text-center p-4 text-muted">
              <FaBell className="mb-2" style={{ fontSize: '2rem', opacity: 0.3 }} />
              <div>No notifications yet</div>
              <small>Subscribe to objects to receive notifications</small>
            </div>
          )}

          {/* Notifications List */}
          {!loading && recentNotifications.length > 0 && (
            <div className="list-group list-group-flush">
              {recentNotifications.map((notification, index) => (
                <div 
                  key={notification.id}
                  className={`list-group-item list-group-item-action p-3 ${!notification.is_read ? 'bg-light border-start border-primary border-3' : ''}`}
                  style={{ borderLeft: !notification.is_read ? '3px solid var(--bs-primary)' : 'none' }}
                >
                  <div className="d-flex justify-content-between align-items-start">
                    <div className="flex-grow-1">
                      {/* Title and Time */}
                      <div className="d-flex justify-content-between align-items-center mb-1">
                        <h6 className={`mb-0 text-dark ${!notification.is_read ? 'fw-bold' : ''}`}>
                          {truncateText(notification.title, 40)}
                        </h6>
                        <small className="text-muted">
                          {formatTimeAgo(notification.timestamp)}
                        </small>
                      </div>

                      {/* Content */}
                      <p className="mb-2 text-muted small">
                        {truncateText(notification.content, 60)}
                      </p>

                      {/* Path and Severity */}
                      <div className="d-flex justify-content-between align-items-center">
                        <small className="text-muted">
                          <code>{notification.object_path}</code>
                        </small>
                        <span className={`badge bg-secondary ${getSeverityColor(notification.severity)}`}>
                          {notification.severity}
                        </span>
                      </div>

                      {/* Actions */}
                      {!notification.is_read && (
                        <div className="mt-2">
                          <button 
                            className="btn btn-sm btn-outline-primary"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleMarkAsRead(notification);
                            }}
                          >
                            <FaEye className="me-1" />
                            Mark as read
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Footer */}
          {!loading && recentNotifications.length > 0 && (
            <div className="p-3 bg-light border-top text-center">
              <Link 
                to="/notifications" 
                className="btn btn-primary btn-sm"
                onClick={() => setIsOpen(false)}
              >
                View All Notifications
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default NotificationDropdown;
