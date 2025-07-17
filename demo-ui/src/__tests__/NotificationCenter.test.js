/**
 * Unit tests for NotificationCenter component
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import NotificationCenter from '../pages/NotificationCenter';
import { NotificationProvider } from '../context/NotificationContext';

// Mock the notification context
const mockNotificationContext = {
  notifications: [
    {
      id: '1',
      title: 'Test Notification 1',
      content: 'Test content 1',
      timestamp: '2025-01-01T10:00:00Z',
      severity: 'info',
      is_read: false,
      type: 'task.completed'
    },
    {
      id: '2',
      title: 'Test Notification 2',
      content: 'Test content 2',
      timestamp: '2025-01-01T09:00:00Z',
      severity: 'high',
      is_read: true,
      type: 'task.failed'
    }
  ],
  loading: false,
  error: null,
  hasMore: false,
  connectionStatus: 'connected',
  markAsRead: jest.fn(),
  bulkMarkAsRead: jest.fn(),
  markAllAsRead: jest.fn(),
  loadMore: jest.fn(),
  refreshNotifications: jest.fn()
};

// Mock React Context
jest.mock('../context/NotificationContext', () => ({
  useNotification: () => mockNotificationContext,
  NotificationProvider: ({ children }) => children
}));

// Mock intersection observer for infinite scroll
global.IntersectionObserver = jest.fn(() => ({
  observe: jest.fn(),
  disconnect: jest.fn(),
  unobserve: jest.fn()
}));

describe('NotificationCenter', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders notification center with title', () => {
    render(<NotificationCenter />);
    
    expect(screen.getByText('Notification Center')).toBeInTheDocument();
  });

  test('displays notifications when available', () => {
    render(<NotificationCenter />);
    
    expect(screen.getByText('Test Notification 1')).toBeInTheDocument();
    expect(screen.getByText('Test Notification 2')).toBeInTheDocument();
    expect(screen.getByText('Test content 1')).toBeInTheDocument();
  });

  test('shows connection status indicator', () => {
    render(<NotificationCenter />);
    
    // Should show connected status
    expect(screen.getByText(/connected/i)).toBeInTheDocument();
  });

  test('handles mark as read functionality', async () => {
    const user = userEvent.setup();
    render(<NotificationCenter />);
    
    // Find the first unread notification's mark as read button
    const markAsReadButtons = screen.getAllByText(/mark as read/i);
    await user.click(markAsReadButtons[0]);
    
    expect(mockNotificationContext.markAsRead).toHaveBeenCalledWith('1');
  });

  test('handles bulk mark as read', async () => {
    const user = userEvent.setup();
    render(<NotificationCenter />);
    
    // Select notifications (assuming checkboxes exist)
    const checkboxes = screen.getAllByRole('checkbox');
    if (checkboxes.length > 0) {
      await user.click(checkboxes[0]);
      await user.click(checkboxes[1]);
      
      // Click bulk mark as read button
      const bulkButton = screen.getByText(/mark selected as read/i);
      await user.click(bulkButton);
      
      expect(mockNotificationContext.bulkMarkAsRead).toHaveBeenCalled();
    }
  });

  test('handles mark all as read', async () => {
    const user = userEvent.setup();
    render(<NotificationCenter />);
    
    const markAllButton = screen.getByText(/mark all as read/i);
    await user.click(markAllButton);
    
    expect(mockNotificationContext.markAllAsRead).toHaveBeenCalled();
  });

  test('displays loading state', () => {
    const loadingContext = { ...mockNotificationContext, loading: true };
    jest.doMock('../context/NotificationContext', () => ({
      useNotification: () => loadingContext,
      NotificationProvider: ({ children }) => children
    }));
    
    render(<NotificationCenter />);
    
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('displays error state', () => {
    const errorContext = { 
      ...mockNotificationContext, 
      error: 'Failed to load notifications' 
    };
    jest.doMock('../context/NotificationContext', () => ({
      useNotification: () => errorContext,
      NotificationProvider: ({ children }) => children
    }));
    
    render(<NotificationCenter />);
    
    expect(screen.getByText(/failed to load notifications/i)).toBeInTheDocument();
  });

  test('filters notifications by severity', async () => {
    const user = userEvent.setup();
    render(<NotificationCenter />);
    
    // Assuming severity filter exists
    const severityFilter = screen.getByRole('combobox', { name: /severity/i });
    if (severityFilter) {
      await user.selectOptions(severityFilter, 'high');
      
      // Should show only high severity notifications
      expect(screen.getByText('Test Notification 2')).toBeInTheDocument();
    }
  });

  test('shows notification timestamps correctly', () => {
    render(<NotificationCenter />);
    
    // Check that timestamps are displayed
    const timestamps = screen.getAllByText(/ago|at/i);
    expect(timestamps.length).toBeGreaterThan(0);
  });

  test('handles notification click navigation', async () => {
    const user = userEvent.setup();
    render(<NotificationCenter />);
    
    const notification = screen.getByText('Test Notification 1');
    await user.click(notification);
    
    // Should mark as read when clicked
    expect(mockNotificationContext.markAsRead).toHaveBeenCalledWith('1');
  });
});

describe('NotificationCenter - Edge Cases', () => {
  test('handles empty notification list', () => {
    const emptyContext = { 
      ...mockNotificationContext, 
      notifications: [] 
    };
    jest.doMock('../context/NotificationContext', () => ({
      useNotification: () => emptyContext,
      NotificationProvider: ({ children }) => children
    }));
    
    render(<NotificationCenter />);
    
    expect(screen.getByText(/no notifications/i)).toBeInTheDocument();
  });

  test('handles disconnected state', () => {
    const disconnectedContext = { 
      ...mockNotificationContext, 
      connectionStatus: 'disconnected' 
    };
    jest.doMock('../context/NotificationContext', () => ({
      useNotification: () => disconnectedContext,
      NotificationProvider: ({ children }) => children
    }));
    
    render(<NotificationCenter />);
    
    expect(screen.getByText(/disconnected/i)).toBeInTheDocument();
  });

  test('handles very long notification content', () => {
    const longContentContext = {
      ...mockNotificationContext,
      notifications: [{
        id: '1',
        title: 'Very Long Notification Title That Should Be Truncated',
        content: 'This is a very long notification content that should be properly handled and maybe truncated if it exceeds the maximum length limits set by the component.',
        timestamp: '2025-01-01T10:00:00Z',
        severity: 'info',
        is_read: false,
        type: 'task.completed'
      }]
    };
    
    jest.doMock('../context/NotificationContext', () => ({
      useNotification: () => longContentContext,
      NotificationProvider: ({ children }) => children
    }));
    
    render(<NotificationCenter />);
    
    expect(screen.getByText(/Very Long Notification Title/)).toBeInTheDocument();
  });

  test('handles special characters in notifications', () => {
    const specialCharsContext = {
      ...mockNotificationContext,
      notifications: [{
        id: '1',
        title: 'Notification with "quotes" & <tags>',
        content: 'Content with special chars: @#$%^&*()[]{}',
        timestamp: '2025-01-01T10:00:00Z',
        severity: 'info',
        is_read: false,
        type: 'test.special'
      }]
    };
    
    jest.doMock('../context/NotificationContext', () => ({
      useNotification: () => specialCharsContext,
      NotificationProvider: ({ children }) => children
    }));
    
    render(<NotificationCenter />);
    
    expect(screen.getByText(/Notification with "quotes"/)).toBeInTheDocument();
  });
});
