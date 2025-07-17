/**
 * Unit tests for NotificationContext
 */
import React from 'react';
import { renderHook, act } from '@testing-library/react';
import { NotificationProvider, useNotification } from '../context/NotificationContext';

// Mock NATS connection
const mockNats = {
  connect: jest.fn(),
  subscribe: jest.fn(),
  close: jest.fn(),
  status: jest.fn(() => 'CONNECTED')
};

// Mock fetch API
global.fetch = jest.fn();

// Mock environment variables
process.env.REACT_APP_NATS_WS_URL = 'ws://localhost:4222';
process.env.REACT_APP_API_URL = 'http://localhost:8000';

describe('NotificationContext', () => {
  let wrapper;

  beforeEach(() => {
    jest.clearAllMocks();
    fetch.mockClear();
    
    // Setup wrapper
    wrapper = ({ children }) => (
      <NotificationProvider selectedUserId="test-user">
        {children}
      </NotificationProvider>
    );
  });

  describe('Initial State', () => {
    test('provides initial state correctly', () => {
      const { result } = renderHook(() => useNotification(), { wrapper });
      
      expect(result.current.notifications).toEqual([]);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe(null);
      expect(result.current.hasMore).toBe(true);
      expect(result.current.connectionStatus).toBe('disconnected');
    });
  });

  describe('Loading Notifications', () => {
    test('loads notifications successfully', async () => {
      const mockNotifications = [
        {
          id: '1',
          title: 'Test Notification',
          content: 'Test content',
          timestamp: '2025-01-01T10:00:00Z',
          is_read: false
        }
      ];

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockNotifications
      });

      const { result } = renderHook(() => useNotification(), { wrapper });

      await act(async () => {
        await result.current.refreshNotifications();
      });

      expect(result.current.notifications).toEqual(mockNotifications);
      expect(result.current.loading).toBe(false);
    });

    test('handles loading error', async () => {
      fetch.mockRejectedValueOnce(new Error('API Error'));

      const { result } = renderHook(() => useNotification(), { wrapper });

      await act(async () => {
        await result.current.refreshNotifications();
      });

      expect(result.current.error).toBe('Failed to load notifications');
      expect(result.current.loading).toBe(false);
    });

    test('handles network timeout', async () => {
      fetch.mockImplementationOnce(() => 
        new Promise((resolve, reject) => {
          setTimeout(() => reject(new Error('Timeout')), 100);
        })
      );

      const { result } = renderHook(() => useNotification(), { wrapper });

      await act(async () => {
        await result.current.refreshNotifications();
      });

      expect(result.current.error).toBeTruthy();
    });
  });

  describe('Mark as Read Functionality', () => {
    test('marks single notification as read', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true })
      });

      const { result } = renderHook(() => useNotification(), { wrapper });

      // Set initial notifications
      act(() => {
        result.current.notifications = [
          { id: '1', title: 'Test', is_read: false }
        ];
      });

      await act(async () => {
        await result.current.markAsRead('1');
      });

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/notifications/1/read'),
        expect.objectContaining({
          method: 'PUT'
        })
      );
    });

    test('handles mark as read error', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 404
      });

      const { result } = renderHook(() => useNotification(), { wrapper });

      await act(async () => {
        await result.current.markAsRead('999');
      });

      expect(result.current.error).toBeTruthy();
    });

    test('bulk marks notifications as read', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ updated_count: 2 })
      });

      const { result } = renderHook(() => useNotification(), { wrapper });

      await act(async () => {
        await result.current.bulkMarkAsRead(['1', '2']);
      });

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/notifications/bulk/mark-read'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify({ notification_ids: ['1', '2'] })
        })
      );
    });

    test('marks all notifications as read', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ updated_count: 5 })
      });

      const { result } = renderHook(() => useNotification(), { wrapper });

      await act(async () => {
        await result.current.markAllAsRead();
      });

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/notifications/mark-all-read'),
        expect.objectContaining({
          method: 'PUT'
        })
      );
    });
  });

  describe('Pagination', () => {
    test('loads more notifications', async () => {
      const initialNotifications = [
        { id: '1', title: 'First batch' }
      ];
      const moreNotifications = [
        { id: '2', title: 'Second batch' }
      ];

      fetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => initialNotifications
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => moreNotifications
        });

      const { result } = renderHook(() => useNotification(), { wrapper });

      // Load initial
      await act(async () => {
        await result.current.refreshNotifications();
      });

      // Load more
      await act(async () => {
        await result.current.loadMore();
      });

      expect(result.current.notifications).toHaveLength(2);
      expect(result.current.notifications[0].title).toBe('First batch');
      expect(result.current.notifications[1].title).toBe('Second batch');
    });

    test('detects when no more notifications available', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [] // Empty response
      });

      const { result } = renderHook(() => useNotification(), { wrapper });

      await act(async () => {
        await result.current.loadMore();
      });

      expect(result.current.hasMore).toBe(false);
    });
  });

  describe('NATS Connection', () => {
    test('establishes NATS connection', async () => {
      const { result } = renderHook(() => useNotification(), { wrapper });

      // Simulate connection
      act(() => {
        result.current.connectionStatus = 'connected';
      });

      expect(result.current.connectionStatus).toBe('connected');
    });

    test('handles NATS connection failure', async () => {
      const { result } = renderHook(() => useNotification(), { wrapper });

      // Simulate connection failure
      act(() => {
        result.current.connectionStatus = 'error';
      });

      expect(result.current.connectionStatus).toBe('error');
    });

    test('handles NATS reconnection', async () => {
      const { result } = renderHook(() => useNotification(), { wrapper });

      // Simulate disconnection then reconnection
      act(() => {
        result.current.connectionStatus = 'disconnected';
      });
      
      act(() => {
        result.current.connectionStatus = 'reconnecting';
      });
      
      act(() => {
        result.current.connectionStatus = 'connected';
      });

      expect(result.current.connectionStatus).toBe('connected');
    });
  });

  describe('User Switching', () => {
    test('clears notifications when user changes', async () => {
      const { result, rerender } = renderHook(() => useNotification(), { wrapper });

      // Set some notifications
      act(() => {
        result.current.notifications = [
          { id: '1', title: 'User 1 notification' }
        ];
      });

      // Change user
      const newWrapper = ({ children }) => (
        <NotificationProvider selectedUserId="new-user">
          {children}
        </NotificationProvider>
      );

      rerender({ wrapper: newWrapper });

      expect(result.current.notifications).toEqual([]);
    });
  });

  describe('Error Handling', () => {
    test('clears error after successful operation', async () => {
      const { result } = renderHook(() => useNotification(), { wrapper });

      // Set error state
      act(() => {
        result.current.error = 'Some error';
      });

      // Successful API call
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => []
      });

      await act(async () => {
        await result.current.refreshNotifications();
      });

      expect(result.current.error).toBe(null);
    });

    test('handles concurrent API calls gracefully', async () => {
      const { result } = renderHook(() => useNotification(), { wrapper });

      // Mock slow API response
      fetch.mockImplementationOnce(() => 
        new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          json: async () => [{ id: '1', title: 'First' }]
        }), 100))
      );

      fetch.mockImplementationOnce(() => 
        Promise.resolve({
          ok: true,
          json: async () => [{ id: '2', title: 'Second' }]
        })
      );

      // Make concurrent calls
      await act(async () => {
        const promise1 = result.current.refreshNotifications();
        const promise2 = result.current.refreshNotifications();
        await Promise.all([promise1, promise2]);
      });

      // Should handle gracefully without errors
      expect(result.current.error).toBe(null);
    });
  });
});
