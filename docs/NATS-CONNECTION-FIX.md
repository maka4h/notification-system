# NATS Connection Resource Management Fix

## Issue Description
Users were encountering "ERR_INSUFFICIENT_RES" errors when switching between users and subscribing to different objects. This error typically indicates resource exhaustion, usually due to too many open WebSocket connections or subscriptions not being properly cleaned up.

## Root Cause
The NATS WebSocket connections were not being properly cleaned up during user switches, leading to:
1. Multiple concurrent connections
2. Subscriptions not being unsubscribed
3. Resource accumulation over time
4. WebSocket connection limits being exceeded

## Solution Implemented

### 1. Enhanced Connection Management
```javascript
// Added connection state tracking
const [connectionState, setConnectionState] = useState('disconnected');

// Added cancellation flag to prevent race conditions
let isCancelled = false;
let isConnecting = false;
```

### 2. Improved Cleanup Process
- **Proper async cleanup**: Added setTimeout for connection.close() to prevent blocking
- **Cancellation flags**: Prevent new connections if cleanup is in progress
- **Better error handling**: Warnings instead of errors during cleanup
- **Connection state tracking**: Visual feedback for connection status

### 3. Connection Configuration
```javascript
natsConnection = await connect({
  servers: NATS_WS_URL,
  reconnect: false, // Disable auto-reconnect to prevent resource buildup
  maxReconnectAttempts: 0,
  pingInterval: 30000, // 30 seconds
  timeout: 5000 // 5 second connection timeout
});
```

### 4. Request Timeout Management
```javascript
// Added abort controller for HTTP requests
const abortController = new AbortController();
const timeoutId = setTimeout(() => abortController.abort(), 10000);

const response = await axios.get(`${API_URL}/notifications?${params}`, {
  signal: abortController.signal,
  timeout: 10000
});
```

### 5. User Switch Delay
```javascript
// Add small delay to ensure previous user's connections are cleaned up
const timer = setTimeout(() => {
  fetchNotifications();
}, 100);
```

## Visual Indicators Added
- Connection status badge showing: 🟢 connected, 🟡 connecting, 🔴 error, ⚪ disconnected
- Real-time feedback on connection state
- Better error messages for debugging

## Testing Instructions

### To Test the Fix:
1. **Rapid User Switching**: Switch between users quickly multiple times
2. **Subscription Changes**: Subscribe/unsubscribe to different objects rapidly
3. **Connection Monitoring**: Watch the connection status indicator
4. **Console Logging**: Check browser console for cleanup messages

### Expected Behavior:
- No "ERR_INSUFFICIENT_RES" errors
- Clean connection transitions between users
- Proper cleanup messages in console
- Connection status badge updates correctly

### Console Output Example:
```
🧹 Cleaning up NATS connection for user: Alice Johnson
✅ Subscription unsubscribed
✅ NATS connection closed
Connecting to NATS for user: Bob Smith
✅ Connected to NATS for user: Bob Smith
```

## Prevention Measures
1. **Connection Limits**: Disabled auto-reconnect to prevent connection buildup
2. **Timeout Management**: Added timeouts for all async operations
3. **Race Condition Prevention**: Using cancellation flags
4. **Resource Monitoring**: Visual connection state tracking

## Performance Impact
- **Minimal**: Small 100ms delay during user switches
- **Positive**: Prevents resource exhaustion
- **Stable**: Reliable connection management
- **Visible**: User feedback through status indicators

## Future Improvements
- Connection pooling for multiple users
- WebSocket heartbeat monitoring
- Automatic reconnection with backoff
- Connection metrics and monitoring
