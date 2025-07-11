import React, { useState } from 'react';
import { useUser } from '../context/UserContext';

function UserSelector() {
  const { currentUser, availableUsers, switchUser, switchingUser } = useUser();
  const [isOpen, setIsOpen] = useState(false);

  // Generate user initials for avatar
  const getUserInitials = (name) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase();
  };

  const handleUserClick = (userId, event) => {
    event.preventDefault();
    event.stopPropagation();
    switchUser(userId);
    setIsOpen(false);
  };

  const toggleDropdown = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsOpen(!isOpen);
  };

  const closeDropdown = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsOpen(false);
  };

  return (
    <div style={{ position: 'relative', marginLeft: '1rem', display: 'inline-block' }}>
      {/* Dropdown Button */}
      <button
        onClick={toggleDropdown}
        type="button"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.5rem 1rem',
          backgroundColor: 'transparent',
          border: '1px solid rgba(255,255,255,0.5)',
          borderRadius: '0.375rem',
          color: 'white',
          cursor: 'pointer',
          minWidth: '180px',
          fontSize: '14px',
          outline: 'none'
        }}
      >
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '50%',
          backgroundColor: '#0056b3',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontWeight: 'bold',
          fontSize: '12px'
        }}>
          {getUserInitials(currentUser.name)}
        </div>
        <div style={{ textAlign: 'left', flex: 1 }}>
          <div style={{ fontWeight: 'bold' }}>
            {switchingUser ? 'Switching...' : currentUser.name}
          </div>
          <div style={{ fontSize: '12px', opacity: 0.8 }}>
            {switchingUser ? 'Loading notifications...' : currentUser.role}
          </div>
        </div>
        <span>{switchingUser ? '⟳' : '▼'}</span>
      </button>

      {/* Backdrop */}
      {isOpen && (
        <div
          onClick={closeDropdown}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            zIndex: 999,
            backgroundColor: 'rgba(0,0,0,0.1)'
          }}
        />
      )}

      {/* Dropdown Menu */}
      {isOpen && (
        <div style={{
          position: 'absolute',
          top: '100%',
          right: 0,
          backgroundColor: 'white',
          border: '1px solid #ccc',
          borderRadius: '0.375rem',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
          minWidth: '280px',
          zIndex: 1000,
          marginTop: '0.25rem'
        }}>
          {/* Header */}
          <div style={{
            padding: '0.75rem 1rem',
            borderBottom: '1px solid #eee',
            fontWeight: 'bold',
            color: '#666',
            fontSize: '14px'
          }}>
            👥 Switch User
          </div>

          {/* User List */}
          {availableUsers.map(user => (
            <div
              key={user.id}
              onClick={(e) => handleUserClick(user.id, e)}
              onMouseDown={(e) => e.preventDefault()}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                padding: '0.75rem 1rem',
                cursor: 'pointer',
                backgroundColor: user.id === currentUser.id ? '#e3f2fd' : 'white',
                borderBottom: '1px solid #f0f0f0',
                transition: 'background-color 0.2s',
                userSelect: 'none'
              }}
              onMouseEnter={(e) => {
                if (user.id !== currentUser.id) {
                  e.target.style.backgroundColor = '#f8f9fa';
                }
              }}
              onMouseLeave={(e) => {
                if (user.id !== currentUser.id) {
                  e.target.style.backgroundColor = 'white';
                }
              }}
            >
              <div style={{
                width: '36px',
                height: '36px',
                borderRadius: '50%',
                backgroundColor: user.id === currentUser.id ? '#1976d2' : '#007bff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontWeight: 'bold',
                fontSize: '14px'
              }}>
                {getUserInitials(user.name)}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ 
                  fontWeight: user.id === currentUser.id ? 'bold' : 'normal',
                  color: '#333'
                }}>
                  {user.name}
                </div>
                <div style={{ 
                  fontSize: '12px', 
                  color: '#666' 
                }}>
                  {user.role}
                </div>
              </div>
              {user.id === currentUser.id && (
                <div style={{ 
                  color: '#1976d2', 
                  fontSize: '12px',
                  fontWeight: 'bold'
                }}>
                  ✓ Current
                </div>
              )}
            </div>
          ))}

          {/* Footer */}
          <div style={{
            padding: '0.75rem 1rem',
            fontSize: '12px',
            color: '#666',
            backgroundColor: '#f8f9fa',
            borderTop: '1px solid #eee'
          }}>
            ℹ️ Select a user to view their notifications
          </div>
        </div>
      )}
    </div>
  );
}

export default UserSelector;
