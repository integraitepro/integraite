#!/bin/bash

# Integraite Backend Deployment Script for EC2
# This script builds and deploys the backend application using Docker

set -e  # Exit on any error

# Configuration
APP_NAME="integraite-backend"
CONTAINER_NAME="integraite-backend-container"
PORT=8000
ENV_FILE=".env"

echo "🚀 Starting Integraite Backend Deployment..."

# Stop and remove existing container if it exists
if docker ps -a --format 'table {{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "🔄 Stopping existing container..."
    docker stop $CONTAINER_NAME || true
    echo "🗑️  Removing existing container..."
    docker rm $CONTAINER_NAME || true
fi

# Remove existing image if it exists
if docker images --format 'table {{.Repository}}' | grep -q "^${APP_NAME}$"; then
    echo "🗑️  Removing existing image..."
    docker rmi $APP_NAME || true
fi

# Build new Docker image
echo "🔨 Building Docker image..."
docker build -t $APP_NAME .

# Create data directory for persistent storage
mkdir -p $(pwd)/data
mkdir -p $(pwd)/logs

# Check if environment file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "⚠️  Warning: $ENV_FILE not found. Creating from example..."
    if [ -f "env.example" ]; then
        cp env.example $ENV_FILE
        echo "📝 Please edit $ENV_FILE with your configuration before running the container."
    else
        echo "❌ Error: No environment file found. Please create $ENV_FILE"
        exit 1
    fi
fi

# Run new container
echo "🏃 Starting new container..."
docker run -d \
    --name $CONTAINER_NAME \
    --restart unless-stopped \
    -p $PORT:8000 \
    -v $(pwd)/data:/app/data \
    -v $(pwd)/logs:/app/logs \
    --env-file $ENV_FILE \
    $APP_NAME

# Wait a moment for container to start
echo "⏳ Waiting for container to start..."
sleep 5

# Check if container is running
if docker ps --format 'table {{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "✅ Container is running successfully!"
    
    # Test health endpoint
    echo "🔍 Testing health endpoint..."
    if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
        echo "✅ Health check passed!"
        echo "🌐 Application is available at: http://localhost:$PORT"
        echo "📖 API Documentation: http://localhost:$PORT/docs"
    else
        echo "⚠️  Health check failed. Container may still be starting..."
        echo "📋 Check logs with: docker logs $CONTAINER_NAME"
    fi
else
    echo "❌ Container failed to start!"
    echo "📋 Check logs with: docker logs $CONTAINER_NAME"
    exit 1
fi

# Initialize database
echo "🗄️  Initializing database..."
docker exec $CONTAINER_NAME python -c "
import asyncio
from app.core.init_db import init_database

async def main():
    try:
        await init_database()
        print('✅ Database initialized successfully!')
    except Exception as e:
        print(f'❌ Database initialization failed: {e}')

asyncio.run(main())
"

echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Useful commands:"
echo "  View logs:    docker logs $CONTAINER_NAME"
echo "  Stop app:     docker stop $CONTAINER_NAME"
echo "  Start app:    docker start $CONTAINER_NAME"
echo "  Restart app:  docker restart $CONTAINER_NAME"
echo "  Remove app:   docker stop $CONTAINER_NAME && docker rm $CONTAINER_NAME"
echo ""
