"""Add configuration tables for severity levels and event types

Revision ID: 0001_add_configuration_tables
Revises: 09129a278f19
Create Date: 2025-07-10 15:46:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '0001_add_configuration_tables'
down_revision = None  # This is now the first migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create notifications schema first
    op.execute("CREATE SCHEMA IF NOT EXISTS notifications")
    
    # Create notification_subscriptions table
    op.create_table('notification_subscriptions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('path', sa.String(), nullable=False),
        sa.Column('include_children', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('notification_types', sa.JSON(), nullable=True),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='notifications'
    )
    op.create_index('ix_notification_subscriptions_user_id', 'notification_subscriptions', ['user_id'], schema='notifications')
    op.create_index('ix_notification_subscriptions_path', 'notification_subscriptions', ['path'], schema='notifications')
    
    # Create notifications table
    op.create_table('notifications',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False),
        sa.Column('object_path', sa.String(), nullable=False),
        sa.Column('action_url', sa.String(), nullable=True),
        sa.Column('subscription_id', sa.String(), nullable=True),
        sa.Column('inherited', sa.Boolean(), nullable=False),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['subscription_id'], ['notifications.notification_subscriptions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='notifications'
    )
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'], schema='notifications')
    op.create_index('ix_notifications_type', 'notifications', ['type'], schema='notifications')
    op.create_index('ix_notifications_severity', 'notifications', ['severity'], schema='notifications')
    op.create_index('ix_notifications_timestamp', 'notifications', ['timestamp'], schema='notifications')
    op.create_index('ix_notifications_is_read', 'notifications', ['is_read'], schema='notifications')
    op.create_index('ix_notifications_object_path', 'notifications', ['object_path'], schema='notifications')
    
    # Create severity_levels table
    op.create_table('severity_levels',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('label', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('bootstrap_class', sa.String(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='notifications'
    )
    
    # Create event_types table
    op.create_table('event_types',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('label', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('default_severity_id', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['default_severity_id'], ['notifications.severity_levels.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='notifications'
    )
    
    # Insert default severity levels
    current_time = datetime.utcnow()
    severity_levels_table = sa.table('severity_levels',
        sa.column('id', sa.String),
        sa.column('label', sa.String),
        sa.column('description', sa.Text),
        sa.column('bootstrap_class', sa.String),
        sa.column('priority', sa.Integer),
        sa.column('is_active', sa.Boolean),
        sa.column('created_at', sa.DateTime),
        schema='notifications'
    )
    
    op.bulk_insert(severity_levels_table,
        [
            {
                'id': 'info',
                'label': 'Info',
                'description': 'Informational messages',
                'bootstrap_class': 'info',
                'priority': 1,
                'is_active': True,
                'created_at': current_time
            },
            {
                'id': 'warning',
                'label': 'Warning',
                'description': 'Warning messages that require attention',
                'bootstrap_class': 'warning',
                'priority': 2,
                'is_active': True,
                'created_at': current_time
            },
            {
                'id': 'error',
                'label': 'Error',
                'description': 'Error messages indicating problems',
                'bootstrap_class': 'danger',
                'priority': 3,
                'is_active': True,
                'created_at': current_time
            },
            {
                'id': 'critical',
                'label': 'Critical',
                'description': 'Critical issues requiring immediate attention',
                'bootstrap_class': 'dark',
                'priority': 4,
                'is_active': True,
                'created_at': current_time
            }
        ]
    )
    
    # Insert default event types
    event_types_table = sa.table('event_types',
        sa.column('id', sa.String),
        sa.column('label', sa.String),
        sa.column('description', sa.Text),
        sa.column('default_severity_id', sa.String),
        sa.column('is_active', sa.Boolean),
        sa.column('created_at', sa.DateTime),
        schema='notifications'
    )
    
    op.bulk_insert(event_types_table,
        [
            {
                'id': 'created',
                'label': 'Created',
                'description': 'Object creation events',
                'default_severity_id': 'info',
                'is_active': True,
                'created_at': current_time
            },
            {
                'id': 'updated',
                'label': 'Updated',
                'description': 'Object modification events',
                'default_severity_id': 'info',
                'is_active': True,
                'created_at': current_time
            },
            {
                'id': 'deleted',
                'label': 'Deleted',
                'description': 'Object deletion events',
                'default_severity_id': 'warning',
                'is_active': True,
                'created_at': current_time
            },
            {
                'id': 'commented',
                'label': 'Commented',
                'description': 'Comment addition events',
                'default_severity_id': 'info',
                'is_active': True,
                'created_at': current_time
            },
            {
                'id': 'status_changed',
                'label': 'Status Changed',
                'description': 'Status transition events',
                'default_severity_id': 'info',
                'is_active': True,
                'created_at': current_time
            },
            {
                'id': 'assigned',
                'label': 'Assigned',
                'description': 'Assignment events',
                'default_severity_id': 'info',
                'is_active': True,
                'created_at': current_time
            }
        ]
    )


def downgrade() -> None:
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('event_types', schema='notifications')
    op.drop_table('severity_levels', schema='notifications')
    op.drop_table('notifications', schema='notifications')
    op.drop_table('notification_subscriptions', schema='notifications')
    # Note: We don't drop the schema as it might contain other objects
