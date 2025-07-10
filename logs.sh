#!/bin/bash

# Show logs for all services or a specific service
SERVICE=${1:-""}

if [ -z "$SERVICE" ]; then
    echo "📋 Showing logs for all services..."
    echo "💡 Tip: Use './logs.sh <service>' to see logs for a specific service"
    echo "   Available services: demo-ui, notification-service, event-generator, nats, postgres"
    echo ""
    docker-compose logs -f
else
    echo "📋 Showing logs for service: $SERVICE"
    docker-compose logs -f $SERVICE
fi
