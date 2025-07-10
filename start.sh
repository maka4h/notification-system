#!/bin/bash

# Start all notification system services
echo "🚀 Starting notification system..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 5

echo "📊 Service status:"
docker-compose ps

echo ""
echo "✅ Notification system started successfully!"
echo ""
echo "🌐 Access points:"
echo "  - Demo UI: http://localhost:3000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - NATS Monitor: http://localhost:8222"
echo ""
echo "🔔 The floating notification dropdown is ready to use!"
