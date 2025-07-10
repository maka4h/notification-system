#!/bin/bash

# Clean restart: stop, remove volumes, build, and start
echo "🧹 Performing clean restart (removing all data)..."
echo ""

# Stop services and remove volumes
echo "🛑 Step 1: Stopping services and removing volumes..."
docker-compose down -v

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
echo "✅ Clean restart finished successfully!"
echo ""
echo "⚠️  Note: All previous data has been removed (fresh database)"
echo ""
echo "🌐 Access points:"
echo "  - Demo UI: http://localhost:3000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - NATS Monitor: http://localhost:8222"
echo ""
echo "🔔 The floating notification dropdown is ready to use!"
