# Database Schema Documentation

## Overview

The Notification System uses PostgreSQL for reliable data storage and management. All database objects are organized under the `notifications` schema to provide clear namespace separation and better database organization.

## Database Configuration

- **Database Engine**: PostgreSQL 15
- **Schema**: `notifications`
- **Connection**: Async SQLAlchemy with asyncpg driver
- **Migrations**: Automatic table creation via SQLAlchemy metadata

## Schema Structure

### Schema: `notifications`

All application tables are contained within the `notifications` schema, providing:
- Clear namespace separation from other potential applications
- Better organization and security
- Easier database administration and backup strategies

## Tables

### 1. `notifications.notification_subscriptions`

This table manages user subscriptions to hierarchical object paths for receiving notifications.

#### Schema Definition

```sql
CREATE TABLE notifications.notification_subscriptions (
    id VARCHAR NOT NULL PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    path VARCHAR NOT NULL,
    include_children BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notification_types JSON,
    settings JSON
);

-- Indexes
CREATE INDEX ix_notification_subscriptions_user_id ON notifications.notification_subscriptions (user_id);
CREATE INDEX ix_notification_subscriptions_path ON notifications.notification_subscriptions (path);
```

#### Column Details

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | VARCHAR | PRIMARY KEY | Unique identifier (UUID) |
| `user_id` | VARCHAR | NOT NULL, INDEXED | User identifier for the subscription owner |
| `path` | VARCHAR | NOT NULL, INDEXED | Hierarchical object path (e.g., `/projects/alpha`) |
| `include_children` | BOOLEAN | NOT NULL, DEFAULT true | Whether to include notifications for child objects |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW | Subscription creation timestamp |
| `notification_types` | JSON | NULLABLE | Array of event types to subscribe to (optional filter) |
| `settings` | JSON | NULLABLE | User preferences for notification delivery |

#### Usage Patterns

- **Hierarchical Subscriptions**: Users can subscribe to `/projects` and receive notifications for `/projects/alpha`, `/projects/beta`, etc.
- **Selective Filtering**: `notification_types` allows users to receive only specific event types (e.g., only "created" and "updated")
- **Customization**: `settings` stores user preferences like email delivery, push notifications, etc.

#### Relationships

- Referenced by `notifications.notifications.subscription_id` (one-to-many)

---

### 2. `notifications.notifications`

This table stores all notification records with full audit trail and metadata.

#### Schema Definition

```sql
CREATE TABLE notifications.notifications (
    id VARCHAR NOT NULL PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    type VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    content TEXT NOT NULL,
    severity VARCHAR NOT NULL,
    timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN NOT NULL DEFAULT false,
    object_path VARCHAR NOT NULL,
    action_url VARCHAR,
    subscription_id VARCHAR,
    inherited BOOLEAN NOT NULL DEFAULT false,
    extra_data JSON,
    FOREIGN KEY(subscription_id) REFERENCES notifications.notification_subscriptions (id)
);

-- Indexes for query optimization
CREATE INDEX ix_notifications_user_id ON notifications.notifications (user_id);
CREATE INDEX ix_notifications_type ON notifications.notifications (type);
CREATE INDEX ix_notifications_severity ON notifications.notifications (severity);
CREATE INDEX ix_notifications_timestamp ON notifications.notifications (timestamp);
CREATE INDEX ix_notifications_is_read ON notifications.notifications (is_read);
CREATE INDEX ix_notifications_object_path ON notifications.notifications (object_path);
```

#### Column Details

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | VARCHAR | PRIMARY KEY | Unique identifier (UUID) |
| `user_id` | VARCHAR | NOT NULL, INDEXED | Recipient user identifier |
| `type` | VARCHAR | NOT NULL, INDEXED | Event type (created, updated, deleted, etc.) |
| `title` | VARCHAR | NOT NULL | Human-readable notification title |
| `content` | TEXT | NOT NULL | Detailed notification content/description |
| `severity` | VARCHAR | NOT NULL, INDEXED | Severity level (info, warning, error, critical) |
| `timestamp` | TIMESTAMP | NOT NULL, INDEXED, DEFAULT NOW | When the notification was created |
| `is_read` | BOOLEAN | NOT NULL, INDEXED, DEFAULT false | Read status for the user |
| `object_path` | VARCHAR | NOT NULL, INDEXED | Path of the object that triggered the notification |
| `action_url` | VARCHAR | NULLABLE | Optional URL for notification action/link |
| `subscription_id` | VARCHAR | NULLABLE, FK | Reference to the subscription that generated this notification |
| `inherited` | BOOLEAN | NOT NULL, DEFAULT false | Whether notification was inherited from parent subscription |
| `extra_data` | JSON | NULLABLE | Additional metadata and context |

#### Usage Patterns

- **Time-Series Data**: Heavily indexed by timestamp for chronological queries
- **User Filtering**: Efficient queries by user_id for personal notification feeds
- **Status Management**: is_read field enables read/unread filtering and bulk operations
- **Hierarchical Tracking**: object_path enables path-based filtering and organization
- **Audit Trail**: Full history of all notifications with immutable records

#### Relationships

- Foreign key to `notifications.notification_subscriptions.id`
- Supports cascading updates when subscriptions are modified

## Indexes and Performance

### Primary Indexes

- **Primary Keys**: Clustered B-tree indexes on all `id` columns
- **User Queries**: `user_id` indexes for efficient user-specific data retrieval
- **Time-Series**: `timestamp` index for chronological sorting and range queries
- **Status Filtering**: `is_read` index for unread notification queries
- **Path Filtering**: `object_path` index for hierarchical path queries

### Query Optimization

The database schema is optimized for common query patterns:

1. **User Dashboard**: `SELECT * FROM notifications WHERE user_id = ? ORDER BY timestamp DESC`
2. **Unread Count**: `SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = false`
3. **Path Filtering**: `SELECT * FROM notifications WHERE user_id = ? AND object_path = ?`
4. **Bulk Operations**: `UPDATE notifications SET is_read = true WHERE id IN (...)`

## Data Types and Constraints

### JSON Columns

- **notification_types**: Array of strings representing event types
  ```json
  ["created", "updated", "deleted"]
  ```

- **settings**: User preference object
  ```json
  {
    "email": true,
    "push": false,
    "digest_frequency": "daily"
  }
  ```

- **extra_data**: Flexible metadata storage
  ```json
  {
    "source_event": "app.events.project.created",
    "payload": {...},
    "system_event": false
  }
  ```

### Hierarchical Paths

Object paths follow a consistent hierarchical format:
- Root level: `/projects`, `/departments`, `/resources`
- Nested levels: `/projects/alpha/tasks/task-1`
- Always start with `/` and use `/` as separator
- Case-sensitive and URL-safe characters

## Performance Optimization

The system is designed for efficient querying and data management:

### Index Strategy

PostgreSQL indexes are strategically placed for optimal performance:

```sql
-- Existing indexes for fast lookups
CREATE INDEX idx_notifications_user_timestamp ON notifications.notifications (user_id, timestamp DESC);
CREATE INDEX idx_notifications_object_path ON notifications.notifications (object_path);
CREATE INDEX idx_notifications_severity_timestamp ON notifications.notifications (severity, timestamp DESC);
CREATE INDEX idx_subscriptions_path_user ON notifications.notification_subscriptions (path, user_id);
```

### Time-Series Queries

PostgreSQL provides efficient time-based analytics:

```sql
-- Notification volume by day
SELECT date_trunc('day', timestamp) as day, 
       COUNT(*) as notification_count
FROM notifications.notifications 
WHERE timestamp >= NOW() - INTERVAL '30 days'
GROUP BY day 
ORDER BY day;

-- User engagement metrics
SELECT user_id,
       COUNT(*) as total_notifications,
       COUNT(*) FILTER (WHERE is_read = true) as read_notifications
FROM notifications.notifications
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY user_id;
```

## Migration Strategy

### From Unschematized Tables

If migrating from tables without schema:

```sql
-- Create new schema
CREATE SCHEMA IF NOT EXISTS notifications;

-- Move existing tables
ALTER TABLE notification_subscriptions SET SCHEMA notifications;
ALTER TABLE notifications SET SCHEMA notifications;

-- Update foreign key references
ALTER TABLE notifications.notifications 
DROP CONSTRAINT IF EXISTS notifications_subscription_id_fkey;

ALTER TABLE notifications.notifications 
ADD CONSTRAINT notifications_subscription_id_fkey 
FOREIGN KEY (subscription_id) 
REFERENCES notifications.notification_subscriptions (id);
```

## Security Considerations

### Schema-Level Security

```sql
-- Create application role
CREATE ROLE notification_app;

-- Grant schema usage
GRANT USAGE ON SCHEMA notifications TO notification_app;

-- Grant table permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA notifications TO notification_app;

-- Grant sequence permissions
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA notifications TO notification_app;
```

### Row-Level Security (Optional)

For multi-tenant scenarios:

```sql
-- Enable RLS on notifications table
ALTER TABLE notifications.notifications ENABLE ROW LEVEL SECURITY;

-- Create policy for user isolation
CREATE POLICY user_notifications ON notifications.notifications
FOR ALL TO notification_app
USING (user_id = current_setting('app.current_user_id'));
```

## Monitoring and Maintenance

### Key Metrics to Monitor

1. **Table Growth**: Monitor row counts and storage size
2. **Index Usage**: Ensure indexes are being utilized effectively
3. **Query Performance**: Track slow queries and optimization opportunities
4. **Notification Volume**: Monitor notification creation rates

### Maintenance Tasks

1. **Vacuum and Analyze**: Regular maintenance for optimal performance
2. **Index Maintenance**: Monitor and rebuild fragmented indexes
3. **Archival**: Consider archiving old notifications based on retention policies
4. **Statistics Update**: Ensure query planner has current statistics

## Connection Configuration

### SQLAlchemy Configuration

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Database connection with schema support
POSTGRES_URL = "postgresql+asyncpg://user:password@host:port/database"
engine = create_async_engine(POSTGRES_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Schema creation
async with engine.begin() as conn:
    await conn.execute(text("CREATE SCHEMA IF NOT EXISTS notifications"))
    await conn.run_sync(Base.metadata.create_all)
```

## Best Practices

1. **Use Transactions**: Wrap related operations in database transactions
2. **Prepared Statements**: SQLAlchemy automatically handles query preparation
3. **Connection Pooling**: Configure appropriate pool sizes for your workload
4. **Monitoring**: Implement database monitoring and alerting
5. **Backup Strategy**: Regular backups with point-in-time recovery capability
6. **Schema Evolution**: Use proper migration tools for schema changes

## Future Enhancements

Potential database improvements for future versions:

1. **Partitioning**: Partition notifications table by time or user_id
2. **Read Replicas**: Implement read replicas for scaling read operations
3. **Archival Strategy**: Automated archival of old notifications
4. **Analytics Tables**: Dedicated tables for notification analytics and reporting
5. **Full-Text Search**: Add full-text search capabilities for notification content
