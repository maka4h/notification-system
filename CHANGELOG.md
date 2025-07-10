# Changelog

All notable changes to the Notification System project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-07-10

### Added
- **Floating Notification Dropdown**: 
  - Added `NotificationDropdown.js` component for quick notification access
  - Bell icon in navbar with unread count badge
  - 400px floating window showing recent notifications
  - Auto-close when clicking outside
  - "Mark as read" functionality within dropdown
  - "View All" button linking to full notification center
- **Bulk Selection in Notification Center**:
  - Master "Select All" checkbox for unread notifications
  - Individual selection checkboxes for each unread notification
  - Bulk actions toolbar with selection count
  - "Mark X as read" button for bulk operations
  - Visual highlighting for selected notifications
- **Dynamic Object Browser**:
  - New `/objects/hierarchy` backend endpoint
  - Object Browser now fetches hierarchy from real database data
  - Automatically builds tree structure from notifications and subscriptions
  - Supports loading states and error handling
  - Refresh functionality to update hierarchy
  - Empty state handling for systems without data
- **Convenience Shell Scripts**:
  - `start.sh` - Start all services with status display
  - `stop.sh` - Stop all running containers
  - `build.sh` - Build Docker images without cache
  - `restart.sh` - Complete restart (stop, build, start)
  - `clean-restart.sh` - Clean restart removing all data
  - `status.sh` - System status and health checks
  - `logs.sh` - View service logs (all or specific service)
- **Enhanced Documentation**:
  - Comprehensive README updates with script documentation
  - Detailed usage examples and workflows
  - Project structure updates
  - Troubleshooting guides

### Enhanced
- **User Experience**:
  - Improved notification access without page switching
  - Efficient bulk notification management
  - Better visual feedback for user actions
  - Dynamic object discovery instead of static data
- **Developer Experience**:
  - Easy-to-use shell scripts for common operations
  - Colored output with emojis for better readability
  - Health checks and system monitoring
- **UI/UX Improvements**:
  - Selected notification styling with blue borders
  - Real-time state management for selections
  - Responsive design for different screen sizes
  - Loading spinners and error states

### Technical
- **Backend APIs**: New hierarchical object structure endpoint
- **React Components**: Enhanced notification management with hooks
- **State Management**: Efficient Set-based selection tracking
- **CSS Styling**: Added visual states for selected notifications
- **Integration**: Seamless integration between dropdown and notification center
- **Data-Driven Architecture**: Object Browser now uses real database data

### Removed
- **Static Data**: Removed hardcoded object hierarchy from Object Browser
- **Static Imports**: Eliminated sample data dependencies

## [0.2.0] - Previous Release

### Added
- Real-time hierarchical notification system
- FastAPI backend with NATS message streaming
- PostgreSQL/TimescaleDB database support
- React frontend with Bootstrap styling
- System log UI for monitoring all notifications
- Event generator for testing and demonstrations
- Docker Compose orchestration

### Features
- Hierarchical subscription management
- Real-time event processing
- Notification filtering and search
- Subscription inheritance for nested paths
- Health monitoring and API documentation

## [0.1.0] - Initial Release

### Added
- Basic notification system architecture
- Core backend services
- Initial frontend implementation
- Docker container setup
- Basic documentation

---

## Release Notes

### v0.3.0 Highlights

This release significantly enhances the user experience with three major improvements:

1. **Floating Notification Dropdown** - Users can now quickly view and interact with recent notifications without leaving their current page, providing a seamless workflow experience.

2. **Bulk Selection Feature** - The notification center now supports efficient bulk operations, allowing users to select and mark multiple notifications as read simultaneously.

3. **Dynamic Object Browser** - The Object Browser now fetches real object hierarchy from the database instead of using static data, providing accurate and up-to-date information about the system's structure.

Additionally, the development experience is greatly improved with convenient shell scripts that simplify Docker management and provide comprehensive system monitoring.

### Upgrade Instructions

1. Pull the latest changes
2. Use the new `./restart.sh` script to apply updates
3. All new features are immediately available in the UI

### Breaking Changes

None - this release is fully backward compatible.

### Migration Guide

No migration steps required. All existing data and functionality remain intact.
