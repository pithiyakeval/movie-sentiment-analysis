#!/bin/bash
echo "🚀 Starting Movie Sentiment Frontend..."

# Stop and remove any old frontend container
echo "🛑 Cleaning old containers..."
docker stop sentiment-frontend 2>/dev/null || true
docker rm sentiment-frontend 2>/dev/null || true

# Make sure the network exists (backend should’ve created it)
if ! docker network inspect movie-network >/dev/null 2>&1; then
  echo "🌐 Network not found. Creating movie-network..."
  docker network create movie-network
else
  echo "🌐 Using existing movie-network"
fi

# Build frontend image (only if not built yet)
if ! docker image inspect movie-sentiment-frontend >/dev/null 2>&1; then
  echo "⚙️ Building frontend image..."
  docker build -t movie-sentiment-frontend -f frontend/Dockerfile .
else
  echo "✅ Frontend image already exists"
fi

# Start frontend container
echo "🖥️ Starting frontend container..."
docker run -d \
  --name sentiment-frontend \
  --network movie-network \
  -p 3000:3000 \
  movie-sentiment-frontend

# Wait for startup
sleep 5

# Verify frontend running
if curl -s http://localhost:3000 >/dev/null; then
  echo "✅ Frontend is running successfully!"
else
  echo "❌ Frontend failed to start. Check logs:"
  docker logs sentiment-frontend
fi

echo "🎉 Frontend started successfully!"
echo "🌍 URL: http://localhost:3000"
