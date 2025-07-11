#!/bin/bash

# Notification System - Enhanced Clean Restart Script
# This script performs a complete cleanup and fresh start

echo "🧹 Notification System - Complete Clean Restart"
echo "================================================"
echo ""
echo "This script will:"
echo "  1. Stop all containers"
echo "  2. Remove all volumes and data"
echo "  3. Clean Docker images and build cache"
echo "  4. Rebuild all containers from scratch"
echo "  5. Start all services fresh"
echo ""
echo "⚠️  WARNING: This will permanently delete ALL data!"
echo ""

# Confirmation prompt
read -p "Are you sure you want to proceed? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Operation cancelled."
    exit 1
fi

echo ""
echo "� Checking Docker status..."
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo ""
echo "�🛑 Step 1: Stopping all containers and removing volumes..."
docker-compose down -v

echo ""
echo "🧽 Step 2: Cleaning up Docker system (images, cache, networks)..."
docker system prune -a -f

echo ""
echo "🔨 Step 3: Rebuilding all containers from scratch (no cache)..."
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
