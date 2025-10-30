#!/bin/bash
echo "🔍 Checking Backend & Database..."

echo "1. Checking containers..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n2. Testing API health..."
curl -s http://localhost:5000/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:5000/health

echo -e "\n3. Testing database connection..."
docker exec movie-sentiment_db_1 pg_isready -U postgres

echo -e "\n4. Testing sentiment analysis..."
curl -s -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Quick test of our awesome API!"}' | python3 -m json.tool 2>/dev/null || curl -s -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Quick test of our awesome API!"}'

echo -e "\n✅ Backend check completed!"
