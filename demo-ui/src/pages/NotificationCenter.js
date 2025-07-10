import React, { useState, useEffect } from 'react';
import { useNotifications } from '../context/NotificationContext';
import { configService } from '../services/configService';
import { FaFilter, FaSearch, FaCheckCircle, FaCheckSquare, FaSquare } from 'react-icons/fa';

function NotificationCenter() {
  const { 
    notifications, 
    loading, 
    error, 
    fetchNotifications, 
    markAsRead,
    unreadCount
  } = useNotifications();
  
  // Filter state
  const [filters, setFilters] = useState({
    is_read: null,
    severity: '',
    path: '',
    event_type: '',
    search: ''
  });

  // Selection state
  const [selectedNotifications, setSelectedNotifications] = useState(new Set());
  const [selectAll, setSelectAll] = useState(false);
  
  // Configuration state
  const [severityLevels, setSeverityLevels] = useState([]);
  const [eventTypes, setEventTypes] = useState([]);
  const [configLoading, setConfigLoading] = useState(true);
  
  // Apply filters
  const applyFilters = () => {
    const activeFilters = {};
    
    if (filters.is_read !== null) {
      activeFilters.is_read = filters.is_read;
    }
    
    if (filters.severity) {
      activeFilters.severity = filters.severity;
    }
    
    if (filters.path) {
      activeFilters.path = filters.path;
    }
    
    if (filters.event_type) {
      activeFilters.event_type = filters.event_type;
    }
    
    if (filters.search) {
      activeFilters.search = filters.search;
    }
    
    fetchNotifications(activeFilters);
  };

  // Load configuration on component mount
  useEffect(() => {
    const loadConfig = async () => {
      try {
        setConfigLoading(true);
        const [severities, events] = await Promise.all([
          configService.getSeverityLevels(),
          configService.getEventTypes()
        ]);
        setSeverityLevels(severities);
        setEventTypes(events);
      } catch (error) {
        console.error('Failed to load configuration:', error);
        // Fallback to empty arrays - component will still work
        setSeverityLevels([]);
        setEventTypes([]);
      } finally {
        setConfigLoading(false);
      }
    };

    loadConfig();
  }, []);
  
  // Handle filter change
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  // Handle read status filter
  const handleReadFilter = (value) => {
    setFilters(prev => ({
      ...prev,
      is_read: value
    }));
  };
  
  // Reset filters
  const resetFilters = () => {
    setFilters({
      is_read: null,
      severity: '',
      path: '',
      event_type: '',
      search: ''
    });
    
    fetchNotifications();
  };
  
  // Mark notification as read
  const handleMarkAsRead = (id) => {
    markAsRead(id);
  };

  // Handle individual notification selection
  const handleNotificationSelect = (id) => {
    setSelectedNotifications(prev => {
      const newSelected = new Set(prev);
      if (newSelected.has(id)) {
        newSelected.delete(id);
      } else {
        newSelected.add(id);
      }
      return newSelected;
    });
  };

  // Handle select all/none
  const handleSelectAll = () => {
    if (selectAll) {
      setSelectedNotifications(new Set());
    } else {
      const unreadNotifications = notifications.filter(n => !n.is_read);
      setSelectedNotifications(new Set(unreadNotifications.map(n => n.id)));
    }
    setSelectAll(!selectAll);
  };

  // Mark selected notifications as read
  const handleMarkSelectedAsRead = async () => {
    const selectedArray = Array.from(selectedNotifications);
    for (const id of selectedArray) {
      await markAsRead(id);
    }
    setSelectedNotifications(new Set());
    setSelectAll(false);
  };

  // Update select all state when notifications change
  useEffect(() => {
    const unreadNotifications = notifications.filter(n => !n.is_read);
    const selectedUnread = unreadNotifications.filter(n => selectedNotifications.has(n.id));
    
    if (unreadNotifications.length === 0) {
      setSelectAll(false);
    } else {
      setSelectAll(selectedUnread.length === unreadNotifications.length);
    }
  }, [notifications, selectedNotifications]);
  
  // Group notifications by date
  const groupedNotifications = notifications.reduce((groups, notification) => {
    const date = new Date(notification.timestamp).toLocaleDateString();
    
    if (!groups[date]) {
      groups[date] = [];
    }
    
    groups[date].push(notification);
    return groups;
  }, {});
  
  return (
    <div className="notification-center">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Notification Center</h2>
        <span className="badge bg-primary">{unreadCount} unread</span>
      </div>
      
      {/* Filters */}
      <div className="card mb-4">
        <div className="card-header bg-light">
          <div className="d-flex justify-content-between align-items-center">
            <h5 className="mb-0">
              <FaFilter className="me-2" />
              Filters
            </h5>
            <button 
              className="btn btn-sm btn-outline-secondary" 
              onClick={resetFilters}
            >
              Reset
            </button>
          </div>
        </div>
        <div className="card-body">
          <div className="row g-3">
            <div className="col-md-6">
              <div className="input-group">
                <span className="input-group-text">
                  <FaSearch />
                </span>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Search in notifications..."
                  name="search"
                  value={filters.search}
                  onChange={handleFilterChange}
                />
              </div>
            </div>
            
            <div className="col-md-3">
              <select 
                className="form-select" 
                name="severity"
                value={filters.severity}
                onChange={handleFilterChange}
                disabled={configLoading}
              >
                <option value="">All Severities</option>
                {severityLevels.map(severity => (
                  <option key={severity.value} value={severity.value}>
                    {severity.label}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="col-md-3">
              <select 
                className="form-select" 
                name="event_type"
                value={filters.event_type}
                onChange={handleFilterChange}
                disabled={configLoading}
              >
                <option value="">All Event Types</option>
                {eventTypes.map(eventType => (
                  <option key={eventType.value} value={eventType.value}>
                    {eventType.label}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="col-md-6">
              <input
                type="text"
                className="form-control"
                placeholder="Filter by object path (e.g., /projects/project-a)"
                name="path"
                value={filters.path}
                onChange={handleFilterChange}
              />
            </div>
            
            <div className="col-md-6">
              <div className="btn-group w-100" role="group">
                <button 
                  type="button" 
                  className={`btn ${filters.is_read === null ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => handleReadFilter(null)}
                >
                  All
                </button>
                <button 
                  type="button" 
                  className={`btn ${filters.is_read === false ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => handleReadFilter(false)}
                >
                  Unread
                </button>
                <button 
                  type="button" 
                  className={`btn ${filters.is_read === true ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => handleReadFilter(true)}
                >
                  Read
                </button>
              </div>
            </div>
            
            <div className="col-12">
              <button 
                className="btn btn-primary w-100" 
                onClick={applyFilters}
              >
                Apply Filters
              </button>
            </div>
          </div>
        </div>
      </div>
      
      {/* Notifications list */}
      {loading ? (
        <div className="text-center p-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : error ? (
        <div className="alert alert-danger">{error}</div>
      ) : notifications.length === 0 ? (
        <div className="alert alert-info">
          No notifications found. Try changing the filters or subscribe to some objects.
        </div>
      ) : (
        <>
          {/* Bulk actions */}
          {notifications.some(n => !n.is_read) && (
            <div className="card mb-3">
              <div className="card-body py-2">
                <div className="d-flex justify-content-between align-items-center">
                  <div className="d-flex align-items-center">
                    <button
                      className="btn btn-sm btn-outline-secondary me-3"
                      onClick={handleSelectAll}
                      title={selectAll ? "Deselect all" : "Select all unread"}
                    >
                      {selectAll ? <FaCheckSquare /> : <FaSquare />}
                    </button>
                    <span className="text-muted">
                      {selectedNotifications.size > 0 
                        ? `${selectedNotifications.size} selected` 
                        : "Select unread notifications"}
                    </span>
                  </div>
                  
                  {selectedNotifications.size > 0 && (
                    <button
                      className="btn btn-sm btn-success"
                      onClick={handleMarkSelectedAsRead}
                    >
                      <FaCheckCircle className="me-1" />
                      Mark {selectedNotifications.size} as read
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}
          
          {/* Grouped notifications */}
          {Object.entries(groupedNotifications).map(([date, items]) => (
            <div key={date} className="mb-4">
              <h5 className="border-bottom pb-2">{date}</h5>
              
              <div className="list-group">
                {items.map(notification => (
                  <div 
                    key={notification.id} 
                    className={`list-group-item list-group-item-action notification-item severity-${notification.severity} ${notification.is_read ? '' : 'unread'} ${selectedNotifications.has(notification.id) ? 'selected' : ''}`}
                  >
                    <div className="d-flex align-items-start">
                      {/* Selection checkbox */}
                      {!notification.is_read && (
                        <div className="me-3 mt-1">
                          <button
                            className="btn btn-sm btn-outline-secondary"
                            onClick={() => handleNotificationSelect(notification.id)}
                            title={selectedNotifications.has(notification.id) ? "Deselect" : "Select"}
                          >
                            {selectedNotifications.has(notification.id) ? <FaCheckSquare /> : <FaSquare />}
                          </button>
                        </div>
                      )}
                      
                      {/* Notification content */}
                      <div className="flex-grow-1">
                        <div className="d-flex justify-content-between align-items-center">
                          <h5 className="mb-1">{notification.title}</h5>
                          <div>
                            <span className={`badge bg-${configService.getSeverityClass(notification.severity, severityLevels)} me-2`}>
                              {notification.severity}
                            </span>
                            <small className="timestamp">
                              {new Date(notification.timestamp).toLocaleTimeString()}
                            </small>
                          </div>
                        </div>
                        
                        <p className="mb-1">{notification.content}</p>
                        
                        <div className="d-flex justify-content-between align-items-center mt-2">
                          <small className="path-display">
                            {formatPath(notification.object_path)}
                          </small>
                          
                          {!notification.is_read && (
                            <button 
                              className="btn btn-sm btn-outline-primary"
                              onClick={() => handleMarkAsRead(notification.id)}
                            >
                              <FaCheckCircle className="me-1" />
                              Mark as read
                            </button>
                          )}
                        </div>
                        
                        {notification.inherited && (
                          <div className="mt-1">
                            <small className="text-muted">
                              Via subscription to: {notification.extra_data?.subscription_path}
                            </small>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </>
      )}
    </div>
  );
}

function formatPath(path) {
  if (!path) return '';
  const segments = path.split('/').filter(Boolean);
  
  if (segments.length === 0) return '/';
  
  return (
    <>
      <span className="path-segment">/</span>
      {segments.map((segment, index) => (
        <React.Fragment key={index}>
          <span className="path-segment">{segment}</span>
          {index < segments.length - 1 && <span className="path-separator">/</span>}
        </React.Fragment>
      ))}
    </>
  );
}

export default NotificationCenter;
