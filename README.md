# 🔔 Hierarchical Notification System

A real-time, hierarchical notification system built with FastAPI, NATS, PostgreSQL, and React. The system provides event-driven notifications with subscription management and supports hierarchical object paths for flexible notification routing.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org)

## 🏗️ Architecture

The system consists of five main components:

- **NATS Server**: Message broker for event streaming with JetStream persistence
- **PostgreSQL**: Database for storing notifications, subscriptions, and configuration
- **Notification Service**: FastAPI backend that processes events and manages subscriptions  
- **Demo UI**: React frontend for managing subscriptions and viewing notifications
- **Event Generator**: Simulates real-world events for testing and demonstration

## ✨ Features

- **Hierarchical Subscriptions**: Subscribe to specific paths or parent paths to receive child notifications
- **Real-time Notifications**: Event-driven architecture with NATS streaming
- **Floating Notification Dropdown**: Quick access to recent notifications without leaving the current page
- **Smart Filtering**: Filter notifications by severity, event type, path, read status, and more
- **System Monitoring**: View all system events for debugging and monitoring
- **Responsive UI**: Modern React interface with Bootstrap styling
- **Auto-refresh**: Real-time updates in the notification center and system log

## 🆕 Version 0.5.0 Highlights

### Database-Driven Configuration
- **Dynamic Severity Levels**: Severity levels are now stored in the database and configurable via API
- **Dynamic Event Types**: Event types are managed through database configuration
- **PostgreSQL Migration**: Migrated from TimescaleDB to standard PostgreSQL with proper schema management
- **Alembic Migrations**: All database schema changes are managed through Alembic migrations

### Clean Architecture Implementation
- **Layered Architecture**: Implemented proper separation of concerns with API, Service, Repository, and Core layers
- **Dependency Injection**: Clean dependency management through the core layer
- **Maintainable Codebase**: Easy to test, extend, and maintain with clear separation between layers
- **Entry Point Simplification**: `main.py` now only handles application startup

### Enhanced Database Management
- **Migration-Only Schema**: Database objects are created exclusively through Alembic migrations
- **Foreign Key Relationships**: Proper database relationships between configuration tables
- **Data Integrity**: Enhanced data consistency and referential integrity
- **Clean Database Setup**: Fresh database setup with automated migration execution

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Running the System

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd notification-system
   ```

2. **Using the convenience scripts** (recommended):
   ```bash
   # Start all services
   ./start.sh
   
   # Stop all services
   ./stop.sh
   
   # Build fresh images
   ./build.sh
   
   # Complete restart (stop, build, start)
   ./restart.sh
   
   # Clean restart (removes all data)
   ./clean-restart.sh
   
   # Check system status
   ./status.sh
   
   # View logs (all services or specific service)
   ./logs.sh
   ./logs.sh demo-ui
   ```

3. **Using Docker Compose directly**:
   ```bash
   # Start all services
   docker-compose up -d
   
   # Stop all services
   docker-compose down
   
   # Clean restart (removes all data)
   docker-compose down -v
   docker-compose build --no-cache
   docker-compose up -d
   ```

4. **Access the application**:
   - **Demo UI**: http://localhost:3000
   - **API Documentation**: http://localhost:8000/docs
   - **NATS Monitoring**: http://localhost:8222

## 📊 Services Overview

### Notification Service (Port 8000)
FastAPI backend that handles subscriptions, notifications, and event processing.

### Demo UI (Port 3000)
React frontend with the following pages:
- **Dashboard**: Overview and quick access
- **Object Browser**: Browse hierarchical object structure
- **Subscription Manager**: Create and manage subscriptions
- **Notification Center**: View and filter personal notifications
- **System Log**: Monitor all system events (debugging)

**Key UI Features**:
- **Floating Notification Dropdown**: Click the bell icon in the navbar to see recent notifications in a popup window without leaving your current page
- **Real-time Updates**: Live notification count badge and automatic refresh
- **Smart Notifications**: Mark notifications as read directly from the dropdown
- **Quick Navigation**: "View All" button to access the full notification center

### NATS Server (Ports 4222, 8222, 9222)
- **4222**: NATS client connections
- **8222**: HTTP monitoring interface
- **9222**: WebSocket connections

### PostgreSQL (Port 5432)
PostgreSQL database for storing notifications, subscriptions, and system configuration. The database schema is managed through Alembic migrations with proper foreign key relationships.

### Event Generator
Continuously generates sample events every 30 seconds for testing.

## 🔌 API Endpoints

### Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/notifications` | Get user notifications with filtering |
| `POST` | `/notifications/{id}/read` | Mark notification as read |
| `GET` | `/system/notifications` | Get all system notifications (monitoring) |

**Notification Filters**:
- `path`: Filter by object path
- `event_type`: Filter by event type (created, updated, deleted, etc.)
- `severity`: Filter by severity (info, warning, error, critical)
- `from_date`/`to_date`: Date range filtering
- `is_read`: Filter by read status
- `search`: Text search in title/content
- `limit`/`offset`: Pagination

### Subscriptions

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/subscriptions` | Create new subscription |
| `GET` | `/subscriptions` | Get user subscriptions |
| `DELETE` | `/subscriptions/{id}` | Delete subscription |
| `GET` | `/subscriptions/check` | Check subscription status for path |

**Subscription Parameters**:
- `object_path`: Path to subscribe to (e.g., `/projects/project-a`)
- `event_types`: List of event types to subscribe to
- `severity_filter`: Minimum severity level

### Configuration (New in v0.5.0)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/configuration/severity-levels` | Get available severity levels from database |
| `GET` | `/configuration/event-types` | Get available event types from database |
| `GET` | `/configuration/ui-config` | Get UI configuration settings |

### System & Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health check |
| `GET` | `/docs` | API documentation (Swagger) |
| `GET` | `/system/objects` | Get object hierarchy for path browsing |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `WS` `/ws/notifications/{user_id}` | Real-time notification streaming |

## 🔔 Notification Dropdown

The Demo UI features a floating notification dropdown that provides quick access to recent notifications without leaving the current page.

### Features

- **Bell Icon**: Located in the navbar with a red badge showing unread count
- **Floating Window**: 400px wide dropdown that appears below the bell icon
- **Recent Notifications**: Shows the 10 most recent notifications with:
  - Notification title and timestamp (e.g., "5m ago", "Just now")
  - Truncated content preview
  - Object path and severity level
  - Visual indicators for unread notifications (bold text, blue border)
- **Quick Actions**:
  - Mark individual notifications as read
  - "View All" button to navigate to the full notification center
- **Smart Behavior**:
  - Auto-closes when clicking outside the dropdown
  - Fetches fresh data each time it opens
  - Shows loading states and empty state messages
  - Integrates with real-time notification updates

### Usage

1. **View Recent Notifications**: Click the bell icon in the navbar
2. **Mark as Read**: Click the "Mark as read" button on unread notifications
3. **Access Full List**: Click "View All Notifications" to go to the notification center
4. **Close Dropdown**: Click outside the dropdown or press Escape

This feature enhances user experience by keeping users informed without interrupting their workflow.

## 🛠️ Convenience Scripts

The project includes several shell scripts to make managing the Docker environment easier:

| Script | Purpose | Usage |
|--------|---------|-------|
| `start.sh` | Start all services | `./start.sh` |
| `stop.sh` | Stop all services | `./stop.sh` |
| `build.sh` | Build Docker images | `./build.sh` |
| `restart.sh` | Complete restart (stop, build, start) | `./restart.sh` |
| `clean-restart.sh` | Clean restart (removes all data) | `./clean-restart.sh` |
| `status.sh` | Check system status and health | `./status.sh` |
| `logs.sh` | View service logs | `./logs.sh [service-name]` |

### Script Details:

#### 🚀 `start.sh`
- Starts all Docker services in detached mode
- Shows service status after startup
- Displays access points (Demo UI, API Docs, NATS Monitor)
- Includes helpful messages about the floating notification dropdown

#### 🛑 `stop.sh`
- Stops and removes all running containers
- Clean shutdown of the notification system
- Simple and fast operation

#### 🔨 `build.sh`
- Builds all Docker images without using cache
- Ensures fresh builds with latest code changes
- Useful after making code modifications

#### 🔄 `restart.sh`
- Complete restart sequence: stop → build → start
- Preserves database data and volumes
- Ideal for applying code changes while keeping data

#### 🧹 `clean-restart.sh`
- Complete clean restart: stop → remove volumes → build → start
- Removes all data including database contents
- Fresh start with empty database
- Use when you want to reset everything

#### 📊 `status.sh`
- Shows current status of all services
- Performs health checks on key endpoints
- Displays service accessibility information
- Helpful for troubleshooting

#### 📋 `logs.sh`
- View logs for all services or specific service
- Real-time log following with `-f` flag
- Usage: `./logs.sh` (all) or `./logs.sh service-name`
- Available services: demo-ui, notification-service, event-generator, nats, postgres

### Script Examples:

```bash
# Quick start
./start.sh

# Check if everything is running
./status.sh

# View all logs
./logs.sh

# View specific service logs
./logs.sh demo-ui
./logs.sh notification-service

# Apply code changes (keeps data)
./restart.sh

# Fresh start (removes all data)
./clean-restart.sh

# Stop everything
./stop.sh

# Build fresh images
./build.sh
```

### Common Workflows:

```bash
# Development workflow (preserves data)
./stop.sh          # Stop services
# Make code changes
./restart.sh       # Apply changes

# Clean development start
./clean-restart.sh # Fresh start with empty database

# Troubleshooting
./status.sh        # Check service health
./logs.sh          # View all logs
./logs.sh demo-ui  # Check specific service
```

### Script Features:

- **🎨 Colored Output**: Uses emojis and clear formatting for better readability
- **📊 Health Checks**: Automatic service health verification
- **⏱️ Progress Indicators**: Shows operation progress and wait times
- **🔗 Quick Access**: Displays all service URLs after startup
- **💡 Smart Messages**: Helpful tips and status information
- **🚀 One-Command Operations**: Simple commands for complex operations
- **🛡️ Safe Operations**: Proper error handling and confirmations

### Troubleshooting with Scripts:

```bash
# Check if services are running
./status.sh

# View recent logs for debugging
./logs.sh

# Check specific service issues
./logs.sh notification-service
./logs.sh demo-ui

# Force clean restart if issues persist
./clean-restart.sh
```

All scripts are executable and ready to use. They provide a convenient way to manage the notification system without remembering complex Docker commands.

## 📁 Project Structure

```
notification-system/
├── docker-compose.yml          # Multi-service orchestration
├── nats.conf                   # NATS server configuration
├── README.md                   # This file
├── CHANGELOG.md                # Version history and changes
├── LICENSE                     # MIT License
├── .github/workflows/          # GitHub Actions CI/CD
│   └── ci.yml                 # Automated testing and building
├── start.sh                    # Start all services
├── stop.sh                     # Stop all services
├── build.sh                    # Build Docker images
├── restart.sh                  # Complete restart
├── clean-restart.sh            # Clean restart (removes data)
├── status.sh                   # Check system status
├── logs.sh                     # View service logs
├── demo-ui/                    # React frontend
│   ├── Dockerfile
│   ├── package.json
│   ├── public/
│   └── src/
│       ├── App.js             # Main app component
│       ├── components/        # Reusable components
│       │   └── NotificationDropdown.js  # Floating notification popup
│       ├── context/           # React context for notifications
│       └── pages/             # UI pages
├── event-generator/            # Event simulation service
│   ├── Dockerfile
│   ├── generator.py           # Event generation logic
│   └── requirements.txt
└── notification-service/       # FastAPI backend (Clean Architecture)
    ├── Dockerfile
    ├── main.py                # Legacy entry point (imports from app/)
    ├── models.py              # Database models (legacy)
    ├── schemas.py             # Pydantic schemas (legacy)
    ├── requirements.txt
    ├── alembic.ini             # Database migration configuration
    ├── alembic/                # Database migrations
    │   ├── env.py
    │   └── versions/
    │       └── 0001_add_configuration_tables.py
    └── app/                    # Clean Architecture Implementation
        ├── __init__.py
        ├── main.py            # 🎯 Main FastAPI application
        ├── api/               # 🌐 API Layer (Controllers)
        │   ├── __init__.py
        │   ├── router.py      # Main API router
        │   ├── configuration.py  # Configuration endpoints
        │   ├── notifications.py  # Notification endpoints
        │   ├── objects.py     # Object hierarchy endpoints
        │   ├── subscriptions.py  # Subscription endpoints
        │   └── system.py      # System health endpoints
        ├── core/              # ⚙️ Core Configuration
        │   ├── __init__.py
        │   ├── config.py      # Application settings
        │   └── dependencies.py   # Dependency injection
        ├── services/          # 🧠 Business Logic Layer
        │   ├── __init__.py
        │   ├── event_processor.py    # Event processing logic
        │   └── notification_service.py   # Notification business logic
        └── repositories/      # 💾 Data Access Layer
            ├── __init__.py
            └── notification_repository.py   # Database operations
```

## 🎯 Usage Examples

### Creating a Subscription via API

```bash
curl -X POST "http://localhost:8000/subscriptions" \
  -H "Content-Type: application/json" \
  -d '{
    "object_path": "/projects/project-a",
    "event_types": ["created", "updated", "deleted"],
    "severity_filter": "info"
  }'
```

### Getting Notifications

```bash
# Get recent notifications
curl "http://localhost:8000/notifications?limit=10"

# Get only error notifications
curl "http://localhost:8000/notifications?severity=error"

# Search in notifications
curl "http://localhost:8000/notifications?search=project-a"
```

### System Monitoring

```bash
# Get all system events (for debugging)
curl "http://localhost:8000/system/notifications?limit=50"

# Monitor specific path
curl "http://localhost:8000/system/notifications?path=/projects/project-a"
```

## 🔄 Event Types

The system supports the following event types:

- `created`: New object created
- `updated`: Object modified
- `deleted`: Object removed
- `commented`: Comment added
- `status_changed`: Status updated
- `assigned`: Object assigned to user
- `completed`: Task/project completed
- `error`: Error occurred
- `warning`: Warning condition

## 📊 Severity Levels

- `info`: Informational events
- `warning`: Warning conditions
- `error`: Error conditions
- `critical`: Critical failures

## 🌲 Hierarchical Subscriptions

The system supports hierarchical object paths where subscribing to a parent path automatically receives notifications for all child paths:

```
/projects/project-a              # Parent path
├── /projects/project-a/tasks/task-1    # Child path
├── /projects/project-a/tasks/task-2    # Child path
└── /projects/project-a/documents/doc-1 # Child path
```

Subscribing to `/projects/project-a` will receive notifications for:
- `/projects/project-a` (direct)
- `/projects/project-a/tasks/task-1` (inherited)
- `/projects/project-a/tasks/task-2` (inherited)
- `/projects/project-a/documents/doc-1` (inherited)

## 🔧 Configuration

### Environment Variables

**Notification Service**:
- `NATS_URL`: NATS server URL (default: `nats://nats:4222`)
- `POSTGRES_URL`: PostgreSQL connection string
- `LOG_LEVEL`: Logging level (default: `INFO`)

**Event Generator**:
- `NATS_URL`: NATS server URL (default: `nats://nats:4222`)
- `GENERATE_INTERVAL`: Event generation interval in seconds (default: `30`)

### Database Schema

The system uses two main tables:

**notifications**:
- `id`: Unique identifier
- `user_id`: User identifier (or "system" for system events)
- `title`: Notification title
- `content`: Notification content
- `object_path`: Hierarchical object path
- `type`: Event type
- `severity`: Severity level
- `timestamp`: Creation timestamp
- `is_read`: Read status
- `subscription_id`: Associated subscription
- `inherited`: Whether notification is inherited from parent path

**notification_subscriptions**:
- `id`: Unique identifier
- `user_id`: User identifier
- `object_path`: Subscribed path
- `event_types`: JSON array of event types
- `severity_filter`: Minimum severity level
- `created_at`: Subscription creation time

## 🐛 Debugging

### View Logs

```bash
# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f notification-service
docker-compose logs -f event-generator
docker-compose logs -f demo-ui
```

### Database Access

```bash
# Connect to PostgreSQL
docker exec -it notification-system-postgres-1 psql -U postgres -d notification_db

# View notifications
SELECT * FROM notifications ORDER BY timestamp DESC LIMIT 10;

# View subscriptions
SELECT * FROM notification_subscriptions;
```

### NATS Monitoring

Visit http://localhost:8222 for NATS server monitoring interface.

## 🚨 Troubleshooting

### Common Issues

1. **Services not starting**: Check if ports 3000, 4222, 5432, 8000, 8222, 9222 are available
2. **No notifications appearing**: Ensure event generator is running and subscriptions are created
3. **Database connection errors**: Wait for PostgreSQL health check to pass
4. **UI not loading**: Check if notification-service is responding at http://localhost:8000/health

### Health Checks

```bash
# Check service health
curl http://localhost:8000/health

# Check if events are being generated
docker logs notification-system-event-generator-1 --tail 10

# Check database connectivity
docker exec notification-system-postgres-1 pg_isready -U postgres
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test with the provided setup
5. Commit your changes: `git commit -m 'Add some amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏷️ Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework for building APIs
- [NATS](https://nats.io/) - High-performance messaging system
- [React](https://reactjs.org/) - Frontend framework
- [PostgreSQL](https://www.postgresql.org/) - Powerful, open source object-relational database system

## 📞 Support

If you have any questions or need help, please:
1. Check the [troubleshooting section](#-troubleshooting)
2. Look through existing [issues](../../issues)
3. Create a new issue if needed

---

**Happy coding!** 🚀

## 📄 License

This project is licensed under the MIT License.
