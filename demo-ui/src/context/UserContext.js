import React, { createContext, useContext, useState, useEffect } from 'react';

// Pre-defined users for the demo
const DEMO_USERS = [
  { id: 'user123', name: 'Alice Johnson', role: 'Project Manager' },
  { id: 'user456', name: 'Bob Smith', role: 'Developer' },
  { id: 'user789', name: 'Carol Davis', role: 'System Administrator' },
  { id: 'user000', name: 'David Wilson', role: 'QA Engineer' },
  { id: 'user111', name: 'Emma Brown', role: 'DevOps Engineer' }
];

// Create context
const UserContext = createContext();

export function UserProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(() => {
    // Load from localStorage if available, otherwise default to first user
    const savedUser = localStorage.getItem('notification-system-user');
    if (savedUser) {
      try {
        const parsed = JSON.parse(savedUser);
        // Verify the user still exists in our demo users
        const userExists = DEMO_USERS.find(u => u.id === parsed.id);
        if (userExists) {
          return parsed;
        }
      } catch (e) {
        console.warn('Invalid saved user data');
      }
    }
    return DEMO_USERS[0]; // Default to Alice
  });
  const [switchingUser, setSwitchingUser] = useState(false);
  const [navigationCallback, setNavigationCallback] = useState(null);

  // Save to localStorage whenever user changes
  useEffect(() => {
    localStorage.setItem('notification-system-user', JSON.stringify(currentUser));
  }, [currentUser]);

  const switchUser = (userId) => {
    const user = DEMO_USERS.find(u => u.id === userId);
    if (user && userId !== currentUser.id) {
      setSwitchingUser(true);
      setCurrentUser(user);
      // Navigate to main page when switching users (if navigation callback is set)
      if (navigationCallback) {
        navigationCallback('/');
      }
      // Reset switching state after a brief moment
      setTimeout(() => setSwitchingUser(false), 500);
    }
  };

  const setNavigation = (navigateFunc) => {
    setNavigationCallback(() => navigateFunc);
  };

  const value = {
    currentUser,
    availableUsers: DEMO_USERS,
    switchUser,
    switchingUser,
    setNavigation
  };

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
}

export { DEMO_USERS };
