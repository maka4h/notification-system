import React, { useState, useEffect } from 'react';
import { useNotifications } from '../context/NotificationContext';
import { FaBell, FaBellSlash, FaChevronDown, FaChevronRight, FaSpinner } from 'react-icons/fa';

function ObjectBrowser() {
  const { subscribe, unsubscribe, checkSubscription } = useNotifications();
  const [expandedNodes, setExpandedNodes] = useState({});
  const [subscriptionStatus, setSubscriptionStatus] = useState({});
  const [loading, setLoading] = useState({});
  const [hierarchyData, setHierarchyData] = useState([]);
  const [hierarchyLoading, setHierarchyLoading] = useState(true);
  const [hierarchyError, setHierarchyError] = useState(null);
  
  // Fetch object hierarchy from the backend
  useEffect(() => {
    fetchObjectHierarchy();
  }, []);
  
  const fetchObjectHierarchy = async () => {
    try {
      setHierarchyLoading(true);
      setHierarchyError(null);
      
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/objects/hierarchy`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch object hierarchy: ${response.status}`);
      }
      
      const data = await response.json();
      setHierarchyData(data);
      
      // Auto-expand top-level nodes if there are any
      if (data.length > 0) {
        const topLevelExpanded = {};
        data.forEach(node => {
          topLevelExpanded[node.path] = true;
        });
        setExpandedNodes(topLevelExpanded);
        
        // Check subscription status for top-level nodes
        const topLevelPaths = data.map(node => node.path);
        checkSubscriptionStatusBatch(topLevelPaths);
      }
    } catch (error) {
      console.error('Error fetching object hierarchy:', error);
      setHierarchyError(error.message);
    } finally {
      setHierarchyLoading(false);
    }
  };
  
  // Toggle node expansion
  const toggleNode = (path) => {
    setExpandedNodes(prev => ({
      ...prev,
      [path]: !prev[path]
    }));
    
    // Check subscription status for children if expanded
    if (!expandedNodes[path]) {
      const node = findNodeByPath(path);
      if (node && node.children) {
        const childPaths = node.children.map(child => child.path);
        checkSubscriptionStatusBatch(childPaths);
      }
    }
  };
  
  // Find a node by path
  const findNodeByPath = (targetPath) => {
    const findNode = (nodes) => {
      for (const node of nodes) {
        if (node.path === targetPath) {
          return node;
        }
        if (node.children) {
          const found = findNode(node.children);
          if (found) return found;
        }
      }
      return null;
    };
    
    return findNode(hierarchyData);
  };
  
  // Check subscription status for multiple paths
  const checkSubscriptionStatusBatch = async (paths) => {
    for (const path of paths) {
      checkSubscriptionStatusForPath(path);
    }
  };
  
  // Check subscription status for a single path
  const checkSubscriptionStatusForPath = async (path) => {
    try {
      setLoading(prev => ({ ...prev, [path]: true }));
      const result = await checkSubscription(path);
      
      setSubscriptionStatus(prev => ({
        ...prev,
        [path]: {
          isSubscribed: result.is_subscribed,
          isDirect: !!result.direct_subscription,
          isInherited: !!result.inherited_subscription,
          subscriptionId: result.direct_subscription?.id,
          includeChildren: result.direct_subscription?.include_children ?? true,
        }
      }));
    } catch (error) {
      console.error(`Error checking subscription for ${path}:`, error);
    } finally {
      setLoading(prev => ({ ...prev, [path]: false }));
    }
  };
  
  // Handle subscription toggle
  const handleSubscriptionToggle = async (path) => {
    const status = subscriptionStatus[path];
    
    try {
      setLoading(prev => ({ ...prev, [path]: true }));
      
      if (status?.isDirect) {
        // Unsubscribe
        await unsubscribe(status.subscriptionId);
        
        // Update status
        setSubscriptionStatus(prev => ({
          ...prev,
          [path]: {
            ...prev[path],
            isSubscribed: status.isInherited, // Still subscribed if inherited
            isDirect: false,
            subscriptionId: null,
          }
        }));
      } else {
        // Subscribe
        const result = await subscribe(path, true);
        
        // Update status
        setSubscriptionStatus(prev => ({
          ...prev,
          [path]: {
            isSubscribed: true,
            isDirect: true,
            isInherited: false,
            subscriptionId: result.id,
            includeChildren: true,
          }
        }));
      }
    } catch (error) {
      console.error(`Error toggling subscription for ${path}:`, error);
    } finally {
      setLoading(prev => ({ ...prev, [path]: false }));
    }
  };
  
  // Get the display name from a path
  const getPathName = (path) => {
    const segments = path.split('/').filter(Boolean);
    return segments.length > 0 ? segments[segments.length - 1] : 'Root';
  };
  
  // Render a hierarchical object node
  const renderNode = (node, level = 0) => {
    const hasChildren = node.children && node.children.length > 0;
    const isExpanded = expandedNodes[node.path];
    const status = subscriptionStatus[node.path] || { isSubscribed: false, isDirect: false, isInherited: false };
    const isLoading = loading[node.path];
    
    return (
      <div key={node.path} className="mb-2">
        <div 
          className="p-2 border rounded object-item d-flex justify-content-between align-items-center"
          style={{ marginLeft: `${level * 20}px` }}
        >
          <div className="d-flex align-items-center">
            {/* Expand/collapse button */}
            {hasChildren && (
              <button
                className="btn btn-sm btn-link p-0 me-2"
                onClick={() => toggleNode(node.path)}
              >
                {isExpanded ? <FaChevronDown /> : <FaChevronRight />}
              </button>
            )}
            
            {/* Object name */}
            <div>
              <span className="me-2">{getPathName(node.path)}</span>
              <small className="text-muted path-display">{node.path}</small>
            </div>
          </div>
          
          {/* Subscription controls */}
          <div>
            <button
              className={`btn btn-sm ${
                status.isDirect 
                  ? 'btn-primary' 
                  : status.isInherited 
                    ? 'btn-secondary' 
                    : 'btn-outline-primary'
              }`}
              onClick={() => handleSubscriptionToggle(node.path)}
              disabled={isLoading || (status.isInherited && !status.isDirect)}
              title={
                status.isInherited && !status.isDirect
                  ? 'Inherited from parent subscription'
                  : ''
              }
            >
              {isLoading ? (
                <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
              ) : status.isDirect ? (
                <>
                  <FaBell className="me-1" />
                  Subscribed
                </>
              ) : status.isInherited ? (
                <>
                  <FaBell className="me-1" />
                  Inherited
                </>
              ) : (
                <>
                  <FaBellSlash className="me-1" />
                  Subscribe
                </>
              )}
            </button>
          </div>
        </div>
        
        {/* Render children if expanded */}
        {hasChildren && isExpanded && (
          <div className="ps-4 mt-2">
            {node.children.map(child => renderNode(child, level + 1))}
          </div>
        )}
      </div>
    );
  };
  
  // Render loading state
  if (hierarchyLoading) {
    return (
      <div className="object-browser">
        <h2 className="mb-4">Object Browser</h2>
        <div className="text-center py-5">
          <FaSpinner className="fa-spin fa-2x mb-3" />
          <p>Loading object hierarchy...</p>
        </div>
      </div>
    );
  }
  
  // Render error state
  if (hierarchyError) {
    return (
      <div className="object-browser">
        <h2 className="mb-4">Object Browser</h2>
        <div className="alert alert-danger" role="alert">
          <h4 className="alert-heading">Error Loading Object Hierarchy</h4>
          <p>{hierarchyError}</p>
          <button 
            className="btn btn-outline-danger"
            onClick={fetchObjectHierarchy}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }
  
  // Render empty state
  if (hierarchyData.length === 0) {
    return (
      <div className="object-browser">
        <h2 className="mb-4">Object Browser</h2>
        
        <div className="card mb-4">
          <div className="card-header bg-light">
            <h5 className="mb-0">How subscriptions work</h5>
          </div>
          <div className="card-body">
            <ul className="mb-0">
              <li>Click <strong>Subscribe</strong> to subscribe directly to an object</li>
              <li>When you subscribe to a parent object, you automatically receive notifications for all child objects</li>
              <li>Objects with <strong>Inherited</strong> status are covered by a parent subscription</li>
              <li>You can't unsubscribe from inherited subscriptions directly (unsubscribe from the parent instead)</li>
            </ul>
          </div>
        </div>
        
        <div className="card">
          <div className="card-header bg-light">
            <h5 className="mb-0">Object Hierarchy</h5>
          </div>
          <div className="card-body">
            <div className="text-center py-4">
              <p className="text-muted">No objects found in the system.</p>
              <p className="text-muted">
                Objects will appear here once notifications are generated or subscriptions are created.
              </p>
              <button 
                className="btn btn-outline-primary"
                onClick={fetchObjectHierarchy}
              >
                Refresh
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="object-browser">
      <h2 className="mb-4">Object Browser</h2>
      
      <div className="card mb-4">
        <div className="card-header bg-light">
          <h5 className="mb-0">How subscriptions work</h5>
        </div>
        <div className="card-body">
          <ul className="mb-0">
            <li>Click <strong>Subscribe</strong> to subscribe directly to an object</li>
            <li>When you subscribe to a parent object, you automatically receive notifications for all child objects</li>
            <li>Objects with <strong>Inherited</strong> status are covered by a parent subscription</li>
            <li>You can't unsubscribe from inherited subscriptions directly (unsubscribe from the parent instead)</li>
          </ul>
        </div>
      </div>
      
      <div className="card">
        <div className="card-header bg-light d-flex justify-content-between align-items-center">
          <h5 className="mb-0">Object Hierarchy</h5>
          <button 
            className="btn btn-sm btn-outline-secondary"
            onClick={fetchObjectHierarchy}
            disabled={hierarchyLoading}
          >
            {hierarchyLoading ? <FaSpinner className="fa-spin" /> : 'Refresh'}
          </button>
        </div>
        <div className="card-body">
          {hierarchyData.map(node => renderNode(node))}
        </div>
      </div>
    </div>
  );
}

export default ObjectBrowser;
