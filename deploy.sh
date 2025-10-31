#!/bin/bash
set -e

echo "🚀 Deploying Movie Sentiment App to Kubernetes..."

# Namespace name
NAMESPACE="movie-sentiment"

# Create namespace if not exists
if ! kubectl get namespace $NAMESPACE >/dev/null 2>&1; then
  echo "📦 Creating namespace: $NAMESPACE"
  kubectl create namespace $NAMESPACE
else
  echo "✅ Namespace $NAMESPACE already exists"
fi

echo "⚙️ Applying ConfigMaps and Secrets..."
kubectl apply -f kubernetes/secret.yaml -n $NAMESPACE
kubectl apply -f kubernetes/configmap.yaml -n $NAMESPACE

echo "🐘 Deploying PostgreSQL..."
kubectl apply -f kubernetes/postgres-deployment.yaml -n $NAMESPACE
kubectl apply -f kubernetes/postgres-service.yaml -n $NAMESPACE

echo "🔧 Deploying Backend (Flask API)..."
kubectl apply -f kubernetes/backend-deployment.yaml -n $NAMESPACE
kubectl apply -f kubernetes/backend-service.yaml -n $NAMESPACE

echo "🖥️ Deploying Frontend (React + Nginx)..."
kubectl apply -f kubernetes/frontend-deployment.yaml -n $NAMESPACE
kubectl apply -f kubernetes/frontend-service.yaml -n $NAMESPACE

echo "⏳ Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=movie-backend -n $NAMESPACE --timeout=180s || true
kubectl wait --for=condition=ready pod -l app=movie-frontend -n $NAMESPACE --timeout=180s || true

echo "📊 Checking deployment status..."
kubectl get pods -n $NAMESPACE
kubectl get svc -n $NAMESPACE

echo "✅ Deployment completed successfully!"
