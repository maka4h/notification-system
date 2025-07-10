#!/bin/bash

# Complete restart: stop, build, and start the notification system
echo "🔄 Performing complete restart of notification system..."
echo ""

# Stop services
echo "🛑 Step 1: Stopping services..."
docker-compose down

# Build images
echo ""
echo "🔨 Step 2: Building fresh images..."
docker-compose build --no-cache

# Start services
echo ""
echo "🚀 Step 3: Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "📊 Service status:"
docker-compose ps

echo ""
echo "✅ Complete restart finished successfully!"
echo ""
echo "🌐 Access points:"
echo "  - Demo UI: http://localhost:3000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - NATS Monitor: http://localhost:8222"
echo ""
echo "🔔 The floating notification dropdown is ready to use!"
