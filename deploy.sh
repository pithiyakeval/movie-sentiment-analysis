#!/bin/bash

echo "🚀 Deploying Movie Sentiment API..."

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t movie-sentiment-api:latest .

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Start new containers
echo "🎯 Starting new containers..."
docker-compose -f docker-compose.prod.yml up -d

echo "✅ Deployment completed!"
echo "🌐 API should be available at: http://localhost:5000"
echo "📊 Check health: curl http://localhost:5000/health"