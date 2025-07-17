#!/bin/bash

# Show status of all services
echo "📊 Notification System Status"
echo "=============================="
echo ""

# Check if services are running
if [ "$(docker-compose ps -q)" ]; then
    echo "✅ Services are running:"
    echo ""
    docker-compose ps
    echo ""
    
    # Check service health
    echo "🔍 Service Health Check:"
    echo "------------------------"
    
    # Check Demo UI
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Demo UI (http://localhost:3000) - Accessible"
    else
        echo "❌ Demo UI (http://localhost:3000) - Not accessible"
    fi
    
    # Check Notification Service
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Notification Service (http://localhost:8000) - Healthy"
    else
        echo "❌ Notification Service (http://localhost:8000) - Not healthy"
    fi
    
    # Check NATS Monitor
    if curl -s http://localhost:8222 > /dev/null 2>&1; then
        echo "✅ NATS Monitor (http://localhost:8222) - Accessible"
    else
        echo "❌ NATS Monitor (http://localhost:8222) - Not accessible"
    fi
    
    echo ""
    echo "🌐 Access Points:"
    echo "  - Demo UI: http://localhost:3000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo "  - NATS Monitor: http://localhost:8222"
    
else
    echo "❌ No services are currently running"
    echo ""
    echo "💡 To start the system, run: ./start.sh"
fi
