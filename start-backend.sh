#!/bin/bash
echo "🚀 Starting Movie Sentiment Backend & Database..."

# Stop and remove existing containers
echo "🛑 Stopping existing containers..."
docker stop postgres-db sentiment-api 2>/dev/null || true
docker rm postgres-db sentiment-api 2>/dev/null || true

# Remove existing network
docker network rm movie-network 2>/dev/null || true

# Create network
echo "🌐 Creating Docker network..."
docker network create movie-network

# Start PostgreSQL
echo "🐘 Starting PostgreSQL..."
docker run -d --name postgres-db --network movie-network \
  -e POSTGRES_DB=moviesentiment \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:13

# Wait for database
echo "⏳ Waiting for database to start..."
sleep 15

# Test database connection
echo "🔍 Testing database connection..."
docker exec postgres-db pg_isready -U postgres

# Start Backend API
echo "🔧 Starting Backend API..."
docker run -d --name sentiment-api --network movie-network \
  -p 5000:5000 \
  -e DB_HOST=postgres-db \
  -e DB_PORT=5432 \
  -e DB_NAME=moviesentiment \
  -e DB_USER=postgres \
  -e DB_PASSWORD=password \
  movie-sentiment-api

# Wait for API to start
echo "⏳ Waiting for API to start..."
sleep 10

# Test everything
echo "🧪 Testing setup..."
curl -s http://localhost:5000/health > /dev/null && echo "✅ Backend is healthy" || echo "❌ Backend failed"

# Test database connection from backend
curl -s http://localhost:5000/health | grep -q "connected" && echo "✅ Database connected" || echo "❌ Database not connected"

echo "🎉 Backend & Database started successfully!"
echo "📊 Backend API: http://localhost:5000"
echo "🗄️  Database: localhost:5432"
echo "🌐 Network: movie-network"
