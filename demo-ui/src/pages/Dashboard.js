import React from 'react';
import { useNotifications } from '../context/NotificationContext';
import { Link } from 'react-router-dom';

function Dashboard() {
  const { unreadCount, notifications, loading } = useNotifications();
  
  // Get recent notifications (last 5)
  const recentNotifications = notifications.slice(0, 5);
  
  return (
    <div className="dashboard">
      <div className="row">
        <div className="col-md-8">
          <div className="card">
            <div className="card-header bg-primary text-white">
              <h5 className="card-title mb-0">Notification System Demo</h5>
            </div>
            <div className="card-body">
              <p>This demo showcases a hierarchical notification system with the following features:</p>
              
              <ul>
                <li>Subscribe to objects at any level in a hierarchy</li>
                <li>Automatically receive notifications for child objects</li>
                <li>Real-time notification delivery via WebSockets</li>
                <li>Persistent notification history</li>
                <li>Filter and search through notifications</li>
              </ul>
              
              <h5 className="mt-4">How to use this demo:</h5>
              
              <ol>
                <li>Go to the <Link to="/objects">Object Browser</Link> to view the hierarchical object structure</li>
                <li>Subscribe to objects by clicking the bell icon</li>
                <li>An event generator is randomly creating events for objects</li>
                <li>You'll receive real-time notifications for subscribed objects and their children</li>
                <li>View and manage your subscriptions in <Link to="/subscriptions">My Subscriptions</Link></li>
                <li>See all notifications in the <Link to="/notifications">Notification Center</Link></li>
              </ol>
            </div>
          </div>
        </div>
        
        <div className="col-md-4">
          <div className="card">
            <div className="card-header bg-primary text-white d-flex justify-content-between align-items-center">
              <h5 className="card-title mb-0">Recent Notifications</h5>
              <span className="badge bg-light text-primary">{unreadCount} unread</span>
            </div>
            <div className="card-body p-0">
              {loading ? (
                <div className="text-center p-3">
                  <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Loading...</span>
                  </div>
                </div>
              ) : recentNotifications.length === 0 ? (
                <div className="p-3 text-center text-muted">
                  No notifications yet. Subscribe to some objects to receive notifications.
                </div>
              ) : (
                <ul className="list-group list-group-flush">
                  {recentNotifications.map(notification => (
                    <li 
                      key={notification.id} 
                      className={`list-group-item notification-item severity-${notification.severity} ${notification.is_read ? '' : 'unread'}`}
                    >
                      <h6 className="mb-1">{notification.title}</h6>
                      <p className="mb-1 small">{notification.content}</p>
                      <div className="d-flex justify-content-between">
                        <small className="timestamp">
                          {new Date(notification.timestamp).toLocaleString()}
                        </small>
                        <span className={`badge bg-${getSeverityClass(notification.severity)}`}>
                          {notification.severity}
                        </span>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
              
              <div className="card-footer text-center">
                <Link to="/notifications" className="btn btn-sm btn-primary">
                  View All Notifications
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function getSeverityClass(severity) {
  switch (severity) {
    case 'info': return 'info';
    case 'warning': return 'warning';
    case 'error': return 'danger';
    case 'critical': return 'dark';
    default: return 'secondary';
  }
}

export default Dashboard;
