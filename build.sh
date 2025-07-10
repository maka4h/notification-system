#!/bin/bash

# Build all Docker images without cache
echo "🔨 Building notification system images..."
docker-compose build --no-cache

echo "✅ All images built successfully!"
