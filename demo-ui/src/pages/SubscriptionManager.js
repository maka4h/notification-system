import React, { useState, useEffect } from 'react';
import { useNotifications } from '../context/NotificationContext';
import { FaBell, FaBellSlash, FaArrowRight, FaChevronDown, FaChevronRight } from 'react-icons/fa';

function SubscriptionManager() {
  const { getSubscriptions, unsubscribe } = useNotifications();
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedPaths, setExpandedPaths] = useState({});
  
  // Load subscriptions
  useEffect(() => {
    fetchSubscriptions();
  }, []);
  
  // Fetch subscriptions
  const fetchSubscriptions = async () => {
    try {
      setLoading(true);
      const data = await getSubscriptions();
      setSubscriptions(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching subscriptions:', error);
      setError('Failed to load subscriptions');
      setLoading(false);
    }
  };
  
  // Handle unsubscribe
  const handleUnsubscribe = async (id) => {
    try {
      await unsubscribe(id);
      // Remove from list
      setSubscriptions(prev => prev.filter(sub => sub.id !== id));
    } catch (error) {
      console.error('Error unsubscribing:', error);
      setError('Failed to unsubscribe');
    }
  };
  
  // Toggle expand
  const toggleExpand = (path) => {
    setExpandedPaths(prev => ({
      ...prev,
      [path]: !prev[path]
    }));
  };
  
  // Group subscriptions into a tree structure
  const groupSubscriptionsHierarchically = (subscriptions) => {
    // Sort by path to ensure parents come before children
    const sortedSubs = [...subscriptions].sort((a, b) => 
      a.path.split('/').length - b.path.split('/').length || a.path.localeCompare(b.path)
    );
    
    const nodes = {};
    const rootNodes = [];
    
    // Create nodes for each subscription
    sortedSubs.forEach(sub => {
      const node = {
        ...sub,
        children: [],
        displayName: getPathName(sub.path),
        level: sub.path.split('/').filter(Boolean).length
      };
      
      nodes[sub.path] = node;
      
      // Find parent
      const parentPath = getParentPath(sub.path);
      
      if (parentPath && nodes[parentPath]) {
        // Add as child to parent
        nodes[parentPath].children.push(node);
      } else {
        // Add to root nodes
        rootNodes.push(node);
      }
    });
    
    return rootNodes;
  };
  
  // Get parent path
  const getParentPath = (path) => {
    const segments = path.split('/').filter(Boolean);
    if (segments.length <= 1) return null;
    
    segments.pop();
    return '/' + segments.join('/');
  };
  
  // Get the display name from a path
  const getPathName = (path) => {
    const segments = path.split('/').filter(Boolean);
    return segments.length > 0 ? segments[segments.length - 1] : 'Root';
  };
  
  // Hierarchical tree
  const hierarchicalSubscriptions = groupSubscriptionsHierarchically(subscriptions);
  
  // Render subscription tree recursively
  const renderSubscriptionTree = (nodes, level = 0) => {
    return (
      <ul className="list-group subscription-tree">
        {nodes.map(node => (
          <li key={node.id} className="mb-2">
            <div className={`subscription-item ${node.children.length > 0 ? 'has-children' : ''}`}>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <div className="d-flex align-items-center">
                    {/* Expand button if has children */}
                    {node.children.length > 0 && (
                      <button 
                        className="btn btn-sm btn-link text-dark p-0 me-2"
                        onClick={() => toggleExpand(node.path)}
                      >
                        {expandedPaths[node.path] ? (
                          <FaChevronDown />
                        ) : (
                          <FaChevronRight />
                        )}
                      </button>
                    )}
                    
                    {/* Subscription icon */}
                    <div className="me-2">
                      <FaBell className="text-primary" />
                    </div>
                    
                    <div>
                      <h5 className="mb-0">{node.displayName}</h5>
                      <small className="text-muted path-display">{node.path}</small>
                    </div>
                  </div>
                  
                  <div className="mt-1">
                    {node.include_children && (
                      <span className="badge bg-success me-2">Includes children</span>
                    )}
                    
                    {node.notification_types?.map(type => (
                      <span key={type} className="badge bg-info me-1">
                        {type}
                      </span>
                    ))}
                    
                    <small className="text-muted ms-2">
                      Subscribed on {new Date(node.created_at).toLocaleDateString()}
                    </small>
                  </div>
                </div>
                
                <div>
                  <button 
                    className="btn btn-sm btn-outline-danger"
                    onClick={() => handleUnsubscribe(node.id)}
                  >
                    <FaBellSlash className="me-1" />
                    Unsubscribe
                  </button>
                </div>
              </div>
            </div>
            
            {/* Render children if expanded */}
            {node.children.length > 0 && expandedPaths[node.path] && (
              <div className="ps-4 mt-2 border-start">
                {renderSubscriptionTree(node.children, level + 1)}
              </div>
            )}
          </li>
        ))}
      </ul>
    );
  };
  
  return (
    <div className="subscription-manager">
      <h2 className="mb-4">My Subscriptions</h2>
      
      {loading ? (
        <div className="text-center p-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : error ? (
        <div className="alert alert-danger">{error}</div>
      ) : subscriptions.length === 0 ? (
        <div className="alert alert-info">
          You don't have any subscriptions yet. Visit the Object Browser to subscribe to objects.
        </div>
      ) : (
        <div className="card">
          <div className="card-header bg-light">
            <h5 className="mb-0">Your subscription hierarchy</h5>
          </div>
          <div className="card-body">
            {renderSubscriptionTree(hierarchicalSubscriptions)}
          </div>
        </div>
      )}
    </div>
  );
}

export default SubscriptionManager;
