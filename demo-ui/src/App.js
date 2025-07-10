import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import { useNotifications } from './context/NotificationContext';
import NotificationDropdown from './components/NotificationDropdown';

// Pages
import Dashboard from './pages/Dashboard';
import NotificationCenter from './pages/NotificationCenter';
import SubscriptionManager from './pages/SubscriptionManager';
import ObjectBrowser from './pages/ObjectBrowser';
import SystemLog from './pages/SystemLog';

function App() {
  const { unreadCount } = useNotifications();
  
  return (
    <div className="App">
      <nav className="navbar navbar-expand-lg navbar-dark bg-primary">
        <div className="container">
          <Link className="navbar-brand" to="/">Notification System Demo</Link>
          <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav me-auto">
              <li className="nav-item">
                <Link className="nav-link" to="/">Dashboard</Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link" to="/objects">Object Browser</Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link" to="/subscriptions">My Subscriptions</Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link" to="/system-log">System Log</Link>
              </li>
            </ul>
            <div className="d-flex align-items-center">
              <NotificationDropdown />
              <span className="navbar-text text-light ms-3">User: Demo User</span>
            </div>
          </div>
        </div>
      </nav>

      <div className="container mt-4">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/notifications" element={<NotificationCenter />} />
          <Route path="/subscriptions" element={<SubscriptionManager />} />
          <Route path="/objects" element={<ObjectBrowser />} />
          <Route path="/system-log" element={<SystemLog />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
