# Notification System

A real-time, hierarchical notification system built with FastAPI, NATS, PostgreSQL (TimescaleDB), and React. The system provides event-driven notifications with subscription management and supports hierarchical object paths for flexible notification routing.

## 🏗️ Architecture

The system consists of five main components:

- **NATS Server**: Message broker for event streaming with JetStream persistence
- **PostgreSQL + TimescaleDB**: Database for storing notifications and subscriptions
- **Notification Service**: FastAPI backend that processes events and manages subscriptions
- **Demo UI**: React frontend for managing subscriptions and viewing notifications
- **Event Generator**: Simulates real-world events for testing and demonstration

## ✨ Features

- **Hierarchical Subscriptions**: Subscribe to specific paths or parent paths to receive child notifications
- **Real-time Notifications**: Event-driven architecture with NATS streaming
- **Smart Filtering**: Filter notifications by severity, event type, path, read status, and more
- **System Monitoring**: View all system events for debugging and monitoring
- **Responsive UI**: Modern React interface with Bootstrap styling
- **Auto-refresh**: Real-time updates in the notification center and system log

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

2. **Start all services**:
   ```bash
   docker-compose up -d
   ```

3. **Access the application**:
   - **Demo UI**: http://localhost:3000
   - **API Documentation**: http://localhost:8000/docs
   - **NATS Monitoring**: http://localhost:8222

4. **Stop the system**:
   ```bash
   docker-compose down
   ```

5. **Clean restart** (removes all data):
   ```bash
   docker-compose down -v
   docker-compose build --no-cache
   docker-compose up -d
   ```

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

### NATS Server (Ports 4222, 8222, 9222)
- **4222**: NATS client connections
- **8222**: HTTP monitoring interface
- **9222**: WebSocket connections

### PostgreSQL (Port 5432)
TimescaleDB-enabled PostgreSQL for storing notifications and subscriptions.

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

### Health & Monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health check |
| `GET` | `/docs` | API documentation (Swagger) |

## 📁 Project Structure

```
notification-system/
├── docker-compose.yml          # Multi-service orchestration
├── nats.conf                   # NATS server configuration
├── README.md                   # This file
├── demo-ui/                    # React frontend
│   ├── Dockerfile
│   ├── package.json
│   ├── public/
│   └── src/
│       ├── App.js             # Main app component
│       ├── context/           # React context for notifications
│       └── pages/             # UI pages
├── event-generator/            # Event simulation service
│   ├── Dockerfile
│   ├── generator.py           # Event generation logic
│   └── requirements.txt
└── notification-service/       # FastAPI backend
    ├── Dockerfile
    ├── main.py                # Main API application
    ├── models.py              # Database models
    ├── schemas.py             # Pydantic schemas
    └── requirements.txt
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

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with the provided setup
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
