import React, { useState, useEffect } from 'react';
import { useNotifications } from '../context/NotificationContext';
import { FaBell, FaBellSlash, FaChevronDown, FaChevronRight, FaSpinner } from 'react-icons/fa';

function ObjectBrowser() {
  const { subscribe, unsubscribe, checkSubscription, getSubscriptions, currentUser } = useNotifications();
  const [expandedNodes, setExpandedNodes] = useState({});
  const [subscriptionStatus, setSubscriptionStatus] = useState({});
  const [loading, setLoading] = useState({});
  const [hierarchyData, setHierarchyData] = useState([]);
  const [hierarchyLoading, setHierarchyLoading] = useState(true);
  const [hierarchyError, setHierarchyError] = useState(null);
  const [existingSubscriptions, setExistingSubscriptions] = useState([]);
  
  // Load both hierarchy and existing subscriptions
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        console.log(`🔄 Object Browser: Loading data for user ${currentUser.name} (${currentUser.id})`);
        
        // Reset states when user changes
        setSubscriptionStatus({});
        setExpandedNodes({});
        setHierarchyData([]);
        setExistingSubscriptions([]);
        
        // Load existing subscriptions first
        const subscriptions = await getSubscriptions();
        console.log(`📋 Found ${subscriptions.length} subscriptions for user ${currentUser.name}:`, subscriptions.map(s => s.path));
        setExistingSubscriptions(subscriptions);
        
        // Update subscription status for existing subscriptions
        const statusUpdates = {};
        subscriptions.forEach(sub => {
          statusUpdates[sub.path] = {
            isSubscribed: true,
            isDirect: true,
            isInherited: false,
            subscriptionId: sub.id,
            includeChildren: sub.include_children ?? true,
          };
        });
        
        setSubscriptionStatus(statusUpdates);
        
        // Then load hierarchy
        await fetchObjectHierarchy(subscriptions);
        
      } catch (error) {
        console.error('Error loading initial data:', error);
      }
    };
    
    loadInitialData();
  }, [currentUser.id, getSubscriptions]); // Add currentUser.id as dependency

  const loadExistingSubscriptions = async () => {
    try {
      const subscriptions = await getSubscriptions();
      setExistingSubscriptions(subscriptions);
      
      // Update subscription status for existing subscriptions
      const statusUpdates = {};
      subscriptions.forEach(sub => {
        statusUpdates[sub.path] = {
          isSubscribed: true,
          isDirect: true,
          isInherited: false,
          subscriptionId: sub.id,
          includeChildren: sub.include_children ?? true,
        };
      });
      
      setSubscriptionStatus(prev => ({
        ...prev,
        ...statusUpdates
      }));
      
      return subscriptions;
    } catch (error) {
      console.error('Error loading existing subscriptions:', error);
      return [];
    }
  };
  
  const fetchObjectHierarchy = async (subscriptions = []) => {
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
        
        // Also expand nodes that lead to existing subscriptions
        const expandedWithSubscriptions = { ...topLevelExpanded };
        subscriptions.forEach(sub => {
          // Expand all parent paths of subscribed paths
          const pathSegments = sub.path.split('/').filter(Boolean);
          let currentPath = '';
          pathSegments.forEach(segment => {
            currentPath += '/' + segment;
            expandedWithSubscriptions[currentPath] = true;
          });
        });
        
        setExpandedNodes(expandedWithSubscriptions);
        
        // Check subscription status for visible nodes
        const allVisiblePaths = [...data.map(node => node.path)];
        
        // Add paths from existing subscriptions and their children
        subscriptions.forEach(sub => {
          allVisiblePaths.push(sub.path);
          // Find node in the loaded data and add children
          const node = findNodeByPath(sub.path, data);
          if (node && node.children) {
            node.children.forEach(child => allVisiblePaths.push(child.path));
          }
        });
        
        // Remove duplicates and check status
        const uniquePaths = [...new Set(allVisiblePaths)];
        checkSubscriptionStatusBatch(uniquePaths);
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
  const findNodeByPath = (targetPath, data = hierarchyData) => {
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
    
    return findNode(data);
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
          className={`p-2 border rounded object-item d-flex justify-content-between align-items-center ${
            status.isDirect 
              ? 'border-primary bg-primary bg-opacity-10' 
              : status.isInherited 
                ? 'border-secondary bg-secondary bg-opacity-10' 
                : 'border-light'
          }`}
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
              <span className="me-2">
                {status.isDirect && <FaBell className="text-primary me-1" size="0.8em" title="Direct subscription" />}
                {status.isInherited && !status.isDirect && <FaBell className="text-secondary me-1" size="0.8em" title="Inherited subscription" />}
                <strong className={status.isDirect ? 'text-primary' : status.isInherited ? 'text-secondary' : ''}>
                  {getPathName(node.path)}
                </strong>
                {status.isDirect && <small className="badge bg-primary ms-1" title="Direct subscription">Direct</small>}
                {status.isInherited && !status.isDirect && <small className="badge bg-secondary ms-1" title="Inherited subscription">Inherited</small>}
              </span>
              <small className="text-muted path-display d-block">{node.path}</small>
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
          <ul className="mb-3">
            <li>Click <strong>Subscribe</strong> to subscribe directly to an object</li>
            <li>When you subscribe to a parent object, you automatically receive notifications for all child objects</li>
            <li>Objects with <strong>Inherited</strong> status are covered by a parent subscription</li>
            <li>You can't unsubscribe from inherited subscriptions directly (unsubscribe from the parent instead)</li>
          </ul>
          
          <div className="row">
            <div className="col-md-4">
              <div className="d-flex align-items-center mb-2">
                <FaBell className="text-primary me-2" />
                <span className="badge bg-primary me-2">Direct</span>
                <small>Direct subscription</small>
              </div>
            </div>
            <div className="col-md-4">
              <div className="d-flex align-items-center mb-2">
                <FaBell className="text-secondary me-2" />
                <span className="badge bg-secondary me-2">Inherited</span>
                <small>Inherited subscription</small>
              </div>
            </div>
            <div className="col-md-4">
              <div className="d-flex align-items-center mb-2">
                <FaBellSlash className="text-muted me-2" />
                <small>Not subscribed</small>
              </div>
            </div>
          </div>
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
