# Hierarchical Notification System - AI Agent Specification

## Project Overview

Create a comprehensive, real-time hierarchical notification system that enables users to subscribe to events occurring within a hierarchical object structure and receive targeted notifications. The system should support multiple users, real-time event streaming, and flexible subscription management with an intuitive web interface.

## Core Architecture & Technology Stack

### Backend Services
- **Language**: Python 3.11+
- **Web Framework**: FastAPI with async support
- **Database**: PostgreSQL 15 with dedicated `notifications` schema
- **Message Broker**: NATS with JetStream for event streaming and persistence
- **ORM**: SQLAlchemy with asyncpg for async database operations
- **API Documentation**: Automatic OpenAPI/Swagger generation via FastAPI

### Frontend
- **Framework**: React 18 with functional components and hooks
- **UI Library**: Bootstrap 5 for responsive design
- **State Management**: React Context API
- **Routing**: React Router v6
- **Real-time Communication**: WebSocket connections to NATS
- **HTTP Client**: Fetch API with error handling

### Infrastructure
- **Containerization**: Docker with multi-service docker-compose setup
- **Development**: Hot-reload support for both frontend and backend
- **Monitoring**: NATS monitoring interface
- **Database Migrations**: Alembic for schema management

## System Components

### 1. Notification Service (FastAPI Backend)
**Port**: 8000

**Core Responsibilities**:
- Process incoming events and route notifications to subscribed users
- Manage subscription CRUD operations with hierarchical path matching
- Provide REST API endpoints for all frontend operations
- Handle WebSocket connections for real-time notifications
- Implement pagination for efficient data handling
- Bulk operations for marking notifications as read

**Key Features**:
- Hierarchical path subscription (e.g., subscribe to `/projects` to receive notifications for `/projects/project-a/tasks/task-1`)
- User-specific notification streams via NATS subjects
- Automatic database migrations on startup
- Event processing with configurable notification routing
- Comprehensive error handling and logging

### 2. Demo UI (React Frontend)
**Port**: 3000

**Pages & Features**:
- **Dashboard**: Overview with recent notifications and system status
- **Object Browser**: Visual hierarchy of subscribable paths with subscription indicators
- **Subscription Manager**: CRUD interface for managing user subscriptions
- **Notification Center**: Paginated view with filtering, bulk operations, infinite scroll
- **System Log**: Real-time system event monitoring for debugging

**UI Components**:
- **User Selector**: Dropdown to switch between 5 demo users (Alice, Bob, Carol, David, Emma)
- **Notification Dropdown**: Floating bell icon with recent notifications popup
- **Real-time Updates**: Live notification counts and automatic page refresh
- **Responsive Design**: Bootstrap-based mobile-friendly interface

### 3. NATS Message Broker
**Ports**: 4222 (client), 8222 (monitoring), 9222 (WebSocket)

**Configuration**:
- JetStream enabled for message persistence
- WebSocket support for browser connections
- Monitoring interface at http://localhost:8222
- Two main streams: `EVENTS` for application events, `NOTIFICATIONS` for user notifications

### 4. PostgreSQL Database
**Port**: 5432

**Schema**: `notifications`
- `notification_subscriptions`: User subscription management
- `notifications`: Individual notification records
- Proper indexing for performance with large datasets
- JSON fields for flexible metadata storage

### 5. Event Generator
**Purpose**: Simulate real-world events for testing and demonstration

**Features**:
- Generates events for hierarchical paths (projects, departments, resources, products)
- Various event types (created, updated, deleted, status_changed, etc.)
- Configurable generation interval
- Realistic sample data for comprehensive testing

## Data Models

### Notification Subscription
```python
{
    "id": "uuid",
    "user_id": "string",  # One of: alice, bob, carol, david, emma
    "path": "string",     # Hierarchical path like "/projects/project-a"
    "include_children": "boolean",  # Subscribe to child paths
    "created_at": "datetime",
    "notification_types": ["array"],  # Filter by event types
    "settings": "object"  # User preferences
}
```

### Notification
```python
{
    "id": "uuid",
    "user_id": "string",
    "type": "string",     # Event type (created, updated, etc.)
    "title": "string",
    "content": "string",
    "severity": "string", # info, warning, error, critical
    "timestamp": "datetime",
    "is_read": "boolean",
    "object_path": "string",  # Path where event occurred
    "action_url": "string",   # Optional action link
    "subscription_id": "string",
    "inherited": "boolean",   # True if from parent path subscription
    "extra_data": "object"    # Additional event metadata
}
```

## Key Functional Requirements

### 1. Hierarchical Subscription System
- Users can subscribe to specific paths or parent paths
- Parent path subscriptions automatically include child path events
- Subscription inheritance clearly marked in notifications
- Support for event type filtering per subscription

### 2. Multi-User Support
- 5 demo users with distinct notification streams
- User switching preserves context and navigation state
- User-specific subscription management
- Per-user notification counting and read status

### 3. Real-time Event Processing
- Events published to NATS trigger notification creation
- Efficient path matching algorithm for subscription routing
- User-specific NATS subjects for notification delivery
- WebSocket connections for instant UI updates

### 4. Performance & Scalability
- Pagination with configurable page sizes
- Infinite scroll with "Load More" functionality
- Bulk operations for marking notifications as read
- Database indexing for efficient queries
- Optimized subscription matching algorithms

### 5. User Experience
- Floating notification dropdown for quick access
- Real-time notification count badges
- Advanced filtering (severity, type, path, read status)
- Responsive design for mobile and desktop
- Intuitive navigation with contextual information

## API Endpoints Structure

### Notifications
- `GET /api/notifications/` - List notifications with pagination and filtering
- `GET /api/notifications/{id}` - Get specific notification
- `PUT /api/notifications/{id}/read` - Mark notification as read
- `PUT /api/notifications/bulk-read` - Bulk mark as read
- `GET /api/notifications/count` - Get unread count

### Subscriptions
- `GET /api/subscriptions/` - List user subscriptions
- `POST /api/subscriptions/` - Create new subscription
- `GET /api/subscriptions/{id}` - Get specific subscription
- `PUT /api/subscriptions/{id}` - Update subscription
- `DELETE /api/subscriptions/{id}` - Delete subscription

### Objects
- `GET /api/objects/` - Browse hierarchical object structure
- `GET /api/objects/subscription-status` - Check subscription status for paths

### System
- `GET /api/system/events` - System event monitoring
- `GET /api/system/health` - Health check endpoint

## WebSocket Events

### Client to Server
- `subscribe_notifications` - Subscribe to user's notification stream
- `unsubscribe_notifications` - Unsubscribe from notification stream

### Server to Client
- `notification_received` - New notification for user
- `notification_updated` - Notification status changed
- `connection_status` - Connection state updates

## Development Requirements

### Project Structure
```
notification-system/
├── VERSION                          # Global version file (0.8.0)
├── README.md                       # Main documentation
├── docker-compose.yml              # Multi-service setup
├── scripts/                        # Utility scripts
│   ├── start.sh, stop.sh, restart.sh
│   ├── build.sh, clean-restart.sh
│   ├── test.sh                     # Test runner with cleanup
│   ├── status.sh, logs.sh
│   └── README.md                   # Scripts documentation
├── docs/                           # Documentation
│   ├── CHANGELOG.md, DATABASE.md
│   ├── v0.7.0-ENHANCEMENTS.md
│   └── README.md                   # Docs index
├── notification-service/           # FastAPI backend
│   ├── app/                        # Application code
│   ├── alembic/                    # Database migrations
│   ├── tests/                      # Backend tests
│   └── requirements.txt
├── demo-ui/                        # React frontend
│   ├── src/                        # React components
│   ├── public/                     # Static assets
│   └── package.json
└── event-generator/                # Event simulation
    ├── generator.py
    └── requirements.txt
```

### Testing Requirements
- Comprehensive backend tests with pytest
- Frontend tests with Jest and React Testing Library
- Integration tests for API endpoints
- Event processing unit tests
- Test coverage reporting
- Automated test cleanup with `scripts/test.sh --clean`

### Configuration Management
- Environment-based configuration
- Docker environment variables
- Development vs production settings
- Secure database connection strings
- NATS connection configuration

## Sample Data & Demo Scenarios

### Hierarchical Paths
```
/projects/project-a/tasks/task-1
/projects/project-a/documents/doc-1
/projects/project-b/tasks/task-3
/departments/engineering/teams/frontend
/departments/engineering/teams/backend
/departments/marketing
/resources/servers/web-1
/resources/databases/users-db
/products/widgets/widget-a
/products/gadgets/gadget-x
```

### Demo Users
- **Alice**: Engineering team lead with broad subscriptions
- **Bob**: Developer focused on specific projects
- **Carol**: Marketing with department-wide subscriptions
- **David**: System administrator monitoring resources
- **Emma**: Product manager tracking product events

### Event Types
- `created` - New object created
- `updated` - Object modified
- `deleted` - Object removed
- `status_changed` - Status update
- `assigned` - Task assignment
- `completed` - Task completion
- `error` - System error
- `maintenance` - Maintenance event

## Quality Requirements

### Performance
- Handle 3000+ notifications efficiently
- Sub-second response times for API calls
- Real-time event processing with minimal latency
- Efficient database queries with proper indexing

### Usability
- Intuitive user interface with minimal learning curve
- Responsive design for various screen sizes
- Clear visual indicators for subscription status
- Contextual help and error messages

### Reliability
- Graceful error handling and recovery
- Database transaction integrity
- Connection resilience with automatic retry
- Comprehensive logging for debugging

### Maintainability
- Well-structured codebase with clear separation of concerns
- Comprehensive documentation and comments
- Automated testing with good coverage
- Easy deployment with Docker
- Clear project organization with scripts and docs folders

## Implementation Notes

1. **Start with the core backend service** implementing the event processing and subscription logic
2. **Set up the database schema** with proper migrations and sample data
3. **Implement the React frontend** with user switching and basic notification display
4. **Add real-time features** with WebSocket connections and live updates
5. **Enhance with advanced features** like pagination, filtering, and bulk operations
6. **Create comprehensive tests** for all components
7. **Add utility scripts** for easy development and deployment
8. **Document thoroughly** with examples and troubleshooting guides

The system should demonstrate a production-ready notification platform that could be adapted for real-world enterprise applications with minimal modifications.
