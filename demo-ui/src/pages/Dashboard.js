import React, { useState, useEffect } from 'react';
import { useNotifications } from '../context/NotificationContext';
import { configService } from '../services/configService';
import { Link } from 'react-router-dom';

function Dashboard() {
  const { unreadCount, notifications, loading } = useNotifications();
  const [uiConfig, setUiConfig] = useState(null);
  const [severityLevels, setSeverityLevels] = useState([]);
  
  // Get recent notifications (last 5)
  const recentNotifications = notifications.slice(0, 5);

  // Load UI configuration
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const [config, severities] = await Promise.all([
          configService.getUIConfig(),
          configService.getSeverityLevels()
        ]);
        setUiConfig(config);
        setSeverityLevels(severities);
      } catch (error) {
        console.error('Failed to load configuration:', error);
        // Fallback to default values
        setUiConfig({
          dashboard: {
            title: "Notification System Demo",
            description: "This demo showcases a hierarchical notification system with the following features:",
            features: [
              "Subscribe to objects at any level in a hierarchy",
              "Automatically receive notifications for child objects",
              "Real-time notification delivery via WebSockets",
              "Persistent notification history",
              "Filter and search through notifications"
            ],
            instructions: {
              title: "How to use this demo:",
              steps: [
                "Go to the Object Browser to view the hierarchical object structure",
                "Subscribe to objects by clicking the bell icon",
                "An event generator is randomly creating events for objects",
                "You'll receive real-time notifications for subscribed objects and their children",
                "View and manage your subscriptions in My Subscriptions",
                "See all notifications in the Notification Center"
              ]
            }
          }
        });
        setSeverityLevels([]);
      }
    };

    loadConfig();
  }, []);

  // Helper function to get severity class using backend configuration
  const getSeverityClass = (severity) => {
    return configService.getSeverityClass(severity, severityLevels);
  };

  if (!uiConfig) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{height: '200px'}}>
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }
  
  return (
    <div className="dashboard">
      <div className="row">
        <div className="col-md-8">
          <div className="card">
            <div className="card-header bg-primary text-white">
              <h5 className="card-title mb-0">{uiConfig.dashboard.title}</h5>
            </div>
            <div className="card-body">
              <p>{uiConfig.dashboard.description}</p>
              
              <ul>
                {uiConfig.dashboard.features.map((feature, index) => (
                  <li key={index}>{feature}</li>
                ))}
              </ul>
              
              <h5 className="mt-4">{uiConfig.dashboard.instructions.title}</h5>
              
              <ol>
                {uiConfig.dashboard.instructions.steps.map((step, index) => (
                  <li key={index}>
                    {step.includes('Object Browser') ? (
                      <>Go to the <Link to="/objects">Object Browser</Link> to view the hierarchical object structure</>
                    ) : step.includes('My Subscriptions') ? (
                      <>View and manage your subscriptions in <Link to="/subscriptions">My Subscriptions</Link></>
                    ) : step.includes('Notification Center') ? (
                      <>See all notifications in the <Link to="/notifications">Notification Center</Link></>
                    ) : (
                      step
                    )}
                  </li>
                ))}
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

export default Dashboard;
