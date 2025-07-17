#!/bin/bash

# Stop and remove all notification system containers
echo "🛑 Stopping notification system..."
docker-compose down

echo "✅ Notification system stopped successfully!"
