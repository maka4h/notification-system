# Hierarchical Notification System

This project implements a hierarchical notification system with the following features:

- Subscribe to objects at any level in a hierarchy
- Automatically receive notifications for child objects
- Real-time notification delivery via WebSockets
- Persistent notification history
- Filter and search through notifications

## Architecture

The system consists of the following components:

- **Notification Service**: FastAPI backend that processes events and manages subscriptions
- **NATS Server**: Messaging system for event distribution and real-time notifications
- **PostgreSQL with TimescaleDB**: Database for storing notifications and subscriptions
- **Demo UI**: React application to demonstrate the notification system
- **Event Generator**: Service that generates random events for testing

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Running the System

1. Clone this repository
2. Navigate to the project directory
3. Start the system with Docker Compose:

```bash
docker-compose up -d
```

4. Wait for all services to start (this may take a minute or two)
5. Access the demo UI at: http://localhost:3000

### Testing the System

Once the system is running, you can test it with these steps:

1. Visit http://localhost:3000 to access the demo UI
2. Go to the "Object Browser" to see the hierarchical structure
3. Subscribe to some objects by clicking the Subscribe button
4. The event generator will automatically generate random events
5. You'll receive real-time notifications for subscribed objects and their children
6. Check the "Notification Center" to see all notifications
7. Go to "My Subscriptions" to manage your subscriptions

## How Hierarchical Subscriptions Work

The system implements a path-based hierarchy:

- Objects have paths like `/projects/project-a/tasks/task-1`
- When you subscribe to `/projects/project-a`, you'll receive notifications for all tasks and other child objects
- You can subscribe at any level of the hierarchy
- The system efficiently checks subscription status by traversing the path hierarchy

## Development

### API Endpoints

The notification service exposes the following API endpoints:

- `GET /notifications`: Get notifications with optional filtering
- `POST /notifications/{notification_id}/read`: Mark a notification as read
- `POST /subscriptions`: Create a subscription to a path
- `GET /subscriptions`: Get all subscriptions
- `DELETE /subscriptions/{subscription_id}`: Delete a subscription
- `GET /subscriptions/check`: Check subscription status for a path

### Environment Variables

The following environment variables can be configured:

- `NATS_URL`: NATS server URL (default: `nats://nats:4222`)
- `POSTGRES_URL`: PostgreSQL connection string
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `NATS_WS_URL`: WebSocket URL for the frontend (default: `ws://localhost:9222`)

## Project Structure

```
notification-system/
├── docker-compose.yml           # Docker Compose configuration
├── notification-service/        # Backend service
│   ├── Dockerfile               # Dockerfile for the service
│   ├── main.py                  # Main application code
│   ├── models.py                # Database models
│   ├── requirements.txt         # Python dependencies
│   └── schemas.py               # Pydantic schemas
├── demo-ui/                     # Frontend demo application
│   ├── Dockerfile               # Dockerfile for the UI
│   ├── package.json             # NPM package configuration
│   ├── public/                  # Static assets
│   └── src/                     # React application code
└── event-generator/             # Test event generator
    ├── Dockerfile               # Dockerfile for the generator
    ├── generator.py             # Event generation script
    └── requirements.txt         # Python dependencies
```
