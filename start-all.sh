  #!/bin/bash
  echo "🚀 Starting Movie Sentiment Full Stack Setup..."

  # Stop & remove old containers
  echo "🛑 Cleaning up old containers..."
  docker stop sentiment-db sentiment-api sentiment-frontend 2>/dev/null || true
  docker rm sentiment-db sentiment-api sentiment-frontend 2>/dev/null || true

  # Remove old network if exists
  docker network rm sentiment-net 2>/dev/null || true

  # Create new Docker network
  echo "🌐 Creating network: sentiment-net"
  docker network create sentiment-net

  # --- Start PostgreSQL ---
  echo "🐘 Starting PostgreSQL..."
  docker run -d \
    --name sentiment-db \
    --network sentiment-net \
    -e POSTGRES_DB=moviesentiment \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=password \
    -p 5432:5432 \
    -v postgres_data:/var/lib/postgresql/data \
    postgres:13

  # Wait for DB to initialize
  echo "⏳ Waiting 15 seconds for PostgreSQL to be ready..."
  sleep 15

  # --- Start Backend (Flask API) ---
  echo "🔧 Starting Flask Backend..."
  docker run -d \
    --name sentiment-api \
    --network sentiment-net \
    -e DB_HOST=sentiment-db \
    -e DB_PORT=5432 \
    -e DB_NAME=moviesentiment \
    -e DB_USER=postgres \
    -e DB_PASSWORD=password \
    -p 5000:5000 \
    movie-sentiment-api

  # Wait for API startup
  echo "⚙️ Waiting 10 seconds for API to initialize..."
  sleep 10

  # --- Start Frontend (React + Nginx) ---
  echo "🖥️ Starting Frontend..."
  docker run -d \
    --name sentiment-frontend \
    --network sentiment-net \
    -p 3000:80 \
    movie-sentiment-frontend

  # Wait a bit before testing
  sleep 5

  # --- Health Check ---
  echo "🧪 Checking backend health..."
  curl -s http://localhost:5000/health || echo "❌ Backend not responding"

  echo ""
  echo "✅ All containers started successfully!"
  echo "🌐 Network: sentiment-net"
  echo "📊 Backend: http://localhost:5000"
  echo "🎬 Frontend: http://localhost:3000"
