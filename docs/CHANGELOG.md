# Changelog

All notable changes to the Notification System project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-07-22

### Added
- **External Configuration for Event Generator**: Event generator now loads configuration from external `config.json` file
- **Docker Volume Mount**: Added volume mount in docker-compose.yml to override event generator configuration without rebuilding
- **Configurable Hierarchical Paths**: Teams can now define custom object paths in config.json for their specific use cases
- **Configurable Event Types**: Event types are now externally configurable (created, updated, deleted, commented, etc.)
- **Configurable Users**: Test users are now defined in external configuration for team flexibility
- **Configurable Settings**: Generation interval and initial event count are now configurable via external file

### Enhanced
- **Team Collaboration**: Other teams can now easily use the event generator with their own objects and event types
- **Configuration Flexibility**: No need to rebuild Docker images when changing event generation parameters
- **Environment Variable Support**: Added CONFIG_FILE environment variable for flexible configuration file location

### Technical
- **External Config Loading**: Event generator reads from `/app/config.json` by default, configurable via CONFIG_FILE env var
- **Docker Integration**: Configuration file is mounted as read-only volume in docker-compose.yml
- **Backward Compatibility**: System gracefully handles missing or invalid configuration files

## [1.0.1] - 2025-07-21

### Fixed
- **Unread Count Bug**: Fixed issue where unread notification count was incorrectly limited to page size (50) instead of showing the true total count after user switching
- **Notification Count Display**: Removed "99+" cap in notification dropdown, now displays actual count regardless of size
- **User Switching**: Ensured unread count persists correctly when switching between users by fetching from backend API

### Added
- **Notification Count API**: Added `/notifications/count` endpoint to return total notification count with optional filtering
- **Backend Service Method**: Added `get_notification_count` method in NotificationService for accurate count retrieval

### Enhanced
- **Frontend Count Logic**: Updated NotificationContext to fetch unread count from API instead of calculating from loaded notifications
- **Real Count Display**: Bell icon now shows true notification count (e.g., 187) instead of capping at 99+

## [0.7.0] - 2025-07-15

### Added
- **Pagination Support**: Implemented efficient pagination for notifications to handle large datasets (3000+ notifications)
- **Load More Functionality**: Added "Load More" button and automatic loading when scrolling near the bottom
- **Bulk Operations**: Enhanced bulk mark-as-read functionality with improved performance
- **Mark All as Read**: New "Mark All Read" button for quickly managing all unread notifications
- **Infinite Scroll**: Automatic loading of more notifications when scrolling to the end
- **Object Browser User Switching**: Object Browser now properly refreshes subscriptions when switching users
- **Enhanced Visual Indicators**: Improved subscription status visibility with badges and color coding
- **Performance Optimizations**: 
  - Page size of 50 notifications per request
  - Lazy loading prevents memory issues with large notification lists
  - Efficient state management for pagination

### Enhanced
- **Notification Center**: Redesigned with scrollable container (70vh max height)
- **Loading States**: Added loading indicators for "load more" operations
- **User Experience**: Shows total notification count and "all loaded" indicator
- **Context API**: Extended with pagination state management and bulk operations

### Fixed
- **Memory Issues**: Resolved problems when loading thousands of notifications
- **Performance**: Eliminated lag when marking multiple notifications as read
- **UI Responsiveness**: Improved interface responsiveness with large datasets
- **NATS Connection Management**: Fixed resource exhaustion when switching users
  - Proper cleanup of existing connections before creating new ones
  - Added connection state tracking and timeout handling
  - Improved error handling and reconnection logic
  - Added request timeouts and abort controllers for API calls
- **Object Browser Subscriptions**: Fixed issue where current subscriptions weren't visible when switching users
  - Added proper user dependency tracking
  - Enhanced subscription status loading and display
  - Improved visual indicators for subscription states
- **Frontend Infinite Loop**: Resolved infinite API calls when switching users
  - Fixed circular dependencies in notification loading
  - Implemented stable references using useRef for offset and filters
  - Improved useEffect dependency management
- **Backend Schema Compatibility**: Fixed Pydantic v2 compatibility issues
  - Updated schemas to use `from_attributes = True` instead of `orm_mode = True`
  - Replaced `from_orm()` with `model_validate()` for proper serialization
  - Resolved subscription check API 500 errors

### Technical Improvements
- Extended `NotificationContext` with pagination state (`hasMore`, `currentOffset`, `loadingMore`)
- Added `loadMoreNotifications()` and `bulkMarkAsRead()` functions
- Implemented scroll-based infinite loading
- Enhanced API calls with proper limit/offset parameters

## [0.6.0] - 2025-07-11

### Added
- **User Switching System**:
  - Complete user context management with UserProvider and UserSelector components
  - Dynamic user switching with automatic navigation to main page
  - User-specific notification loading and real-time updates
  - User session persistence via localStorage
  - Five demo users: Alice Johnson (Project Manager), Bob Smith (Developer), Carol Davis (System Administrator), David Wilson (QA Engineer), Emma Brown (DevOps Engineer)

- **Enhanced User Experience**:
  - Loading states during user switching with visual feedback
  - Automatic notification clearing when switching users
  - User-specific NATS subscription management
  - Clean state reset for notifications, toasts, and bell icon counts

- **Frontend Architecture Improvements**:
  - UserContext with navigation callback pattern to avoid circular dependencies
  - Enhanced NotificationContext with proper user-based API calls
  - All API endpoints now correctly use X-User-ID headers
  - User-specific notification dropdown in navigation bar

- **Backend User Support**:
  - Enhanced dependencies.py to support user identification via headers and query parameters
  - User-specific notification filtering and retrieval
  - Event generator updated to support multiple demo users
  - Proper user context propagation throughout the API layer

### Fixed
- **API Authentication Issues**:
  - Fixed mark-as-read functionality to work for all users (was only working for Alice)
  - Fixed notification dropdown to show correct user's notifications
  - Added missing X-User-ID headers to all API calls
  - Resolved dependency array issues in React hooks causing stale user references

- **User Interface Bugs**:
  - Fixed notification bell icon to display correct unread count per user
  - Resolved issue where notification dropdown always showed first user's data
  - Fixed user switching to properly clear previous user's data
  - Corrected useCallback dependencies to prevent stale closures

### Enhanced
- **Development Tooling**:
  - Enhanced clean-restart.sh script with Docker health checks
  - Added confirmation prompts for destructive operations
  - Improved error handling and status reporting
  - Better Docker system cleanup and volume management

## [0.5.0] - 2025-07-11

### Added
- **Database-Driven Configuration System**:
  - Migrated severity levels from hardcoded values to database tables
  - Migrated event types from hardcoded values to database tables
  - All configuration endpoints now read from database instead of static data
  - Initial data population via Alembic migrations
- **Complete Database Migration Framework**:
  - Migrated from TimescaleDB to standard PostgreSQL
  - Consolidated all table creation into single Alembic migration
  - All database objects now created exclusively via Alembic migrations
  - Removed SQLAlchemy `create_all()` calls from application startup

### Changed
- **Clean Architecture Implementation**:
  - Refactored `main.py` to only handle application startup (clean architecture)
  - Created proper service layer in `app/services/` for business logic
  - Created repository layer in `app/repositories/` for data access
  - Created API layer in `app/api/` for endpoint handling
  - Created core layer in `app/core/` for configuration and dependencies
  - Proper separation of concerns across all application layers
- **Database Schema Management**:
  - All database schema creation now handled exclusively by Alembic migrations
  - Removed TimescaleDB extensions and hypertables
  - Clean PostgreSQL schema with notifications namespace
  - Proper foreign key relationships between configuration tables
- **Timezone Handling**:
  - Fixed inconsistent timestamp handling across the system
  - Backend now consistently uses UTC timestamps (`datetime.utcnow()`)
  - Frontend displays timestamps in user's local timezone
  - Added `TZ: UTC` environment variables to all Docker containers
  - SystemLog now properly displays local time instead of UTC

### Fixed
- **Database Migration Issues**:
  - Fixed duplicate table creation in Alembic migration files
  - Resolved table already exists errors during migration
  - Clean migration process from scratch with fresh environment
- **Container Configuration**:
  - Enhanced Dockerfile to properly copy `alembic.ini` during build
  - Improved Docker Compose configuration with proper dependencies
  - Clean container startup with proper health checks
- **Timestamp Display Issues**:
  - Fixed 4-8 hour timezone discrepancies in UI
  - Resolved inconsistent timestamp storage (some local, some UTC)
  - SystemLog now shows correct local timestamps
  - Database consistently stores UTC timestamps

### Technical Debt Reduction
- **Code Organization**:
  - Eliminated god objects and monolithic main.py
  - Proper dependency injection patterns
  - Clear separation between API, business logic, and data layers
- **Database Management**:
  - Migration-only schema management (no code-based table creation)
  - Consistent timestamp handling across all components
  - Proper database constraints and relationships

## [0.4.0] - 2025-07-10

### Added
- **Comprehensive Swagger/OpenAPI Documentation**:
  - Enhanced all API endpoints with detailed descriptions and examples
  - Added comprehensive endpoint documentation with parameter descriptions
  - Structured API documentation with organized tags:
    - `notifications`: Notification management and bulk operations
    - `subscriptions`: Hierarchical subscription management  
    - `configuration`: Backend-driven UI configuration
    - `system`: Health checks and object hierarchy
    - `websocket`: Real-time notification streaming
  - Added API metadata with contact info, license, and terms of service
  - Response schemas with detailed examples for all endpoints
  - Error response definitions and status codes
  - Use case explanations for each endpoint
- **Bulk Operations API**:
  - New `/notifications/bulk-read` endpoint for marking multiple notifications as read
  - Proper request/response schemas with validation
  - Support for batch processing with user filtering
  - Detailed API documentation with examples
- **WebSocket Real-time Notifications**:
  - Added `/ws/notifications/{user_id}` WebSocket endpoint
  - Real-time notification streaming to connected clients
  - Proper connection management and error handling
  - Documentation with usage examples
- **Backend-Driven Configuration**:
  - Enhanced `/config/severity-levels` with detailed UI configuration
  - Enhanced `/config/event-types` with comprehensive event definitions
  - Enhanced `/config/ui` with dynamic content management
  - All configuration endpoints now have proper documentation
- **New Pydantic Schemas**:
  - `BulkMarkAsReadRequest` for bulk operation requests
  - `BulkMarkAsReadResponse` for bulk operation responses
  - Enhanced validation and type safety

### Enhanced
- **API Documentation Quality**:
  - All endpoints now have comprehensive FastAPI decorators
  - Detailed parameter descriptions with examples
  - Response examples showing real data structures
  - Error handling documentation with status codes
  - Professional-grade API documentation via Swagger UI
- **Developer Experience**:
  - Complete self-documenting API interface
  - Easy testing via Swagger UI
  - Clear endpoint organization and categorization
  - Comprehensive API examples and use cases
- **Code Quality**:
  - Enhanced type safety with new Pydantic schemas
  - Better separation of concerns in API documentation
  - Improved error handling and validation

### Technical
- **FastAPI Enhancements**:
  - Comprehensive OpenAPI metadata configuration
  - Organized endpoint tags for better API navigation
  - Enhanced response models with examples
  - Professional API documentation structure
- **WebSocket Integration**:
  - Real-time notification delivery system
  - Proper connection lifecycle management
  - Error handling and graceful disconnection
- **API Standards**:
  - RESTful API design with proper HTTP methods
  - Consistent response formats across endpoints
  - Proper error status codes and messages
  - Comprehensive request/response validation

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

### v0.4.0 Highlights

This release focuses on enhancing the API documentation and introducing new API features:

1. **Comprehensive Swagger/OpenAPI Documentation** - All API endpoints now have detailed documentation with descriptions, examples, and structured organization, making it easier for developers to understand and use the API.

2. **Bulk Operations API** - A new API endpoint for marking multiple notifications as read has been added, supporting efficient bulk operations.

3. **WebSocket Real-time Notifications** - Introduced a WebSocket endpoint for real-time notification streaming to connected clients.

4. **Backend-Driven Configuration** - Configuration endpoints have been enhanced with detailed UI configuration and dynamic content management.

5. **New Pydantic Schemas** - Added new Pydantic schemas for bulk operation requests and responses, improving validation and type safety.

### Upgrade Instructions

1. Pull the latest changes
2. Use the new `./restart.sh` script to apply updates
3. All new features are immediately available in the UI

### Breaking Changes

None - this release is fully backward compatible.

### Migration Guide

No migration steps required. All existing data and functionality remain intact.

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
