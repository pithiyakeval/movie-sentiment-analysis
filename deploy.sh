#!/bin/bash

echo "🚀 Deploying Movie Sentiment App to Kubernetes..."

# Set project variables
NAMESPACE="movie-sentiment"

# Create namespace if not exists
if ! kubectl get namespace $NAMESPACE >/dev/null 2>&1; then
  echo "📦 Creating namespace: $NAMESPACE"
  kubectl create namespace $NAMESPACE
fi

echo "🧹 Cleaning up old deployments..."
kubectl delete all --all -n $NAMESPACE --ignore-not-found=true

echo "⚙️ Applying ConfigMaps and Secrets..."
kubectl apply -f kubernates/secret.yaml -n $NAMESPACE
kubectl apply -f kubernates/configmap.yaml -n $NAMESPACE

echo "🐘 Deploying PostgreSQL..."
kubectl apply -f kubernates/postgres-deployment.yaml -n $NAMESPACE
kubectl apply -f kubernates/postgres-service.yaml -n $NAMESPACE

echo "🔧 Deploying Backend (Flask API)..."
kubectl apply -f kubernates/backend-deployment.yaml -n $NAMESPACE
kubectl apply -f kubernates/backend-service.yaml -n $NAMESPACE

echo "🖥️ Deploying Frontend (React + Nginx)..."
kubectl apply -f kubernates/frontend-deployment.yaml -n $NAMESPACE
kubectl apply -f kubernates/frontend-service.yaml -n $NAMESPACE

echo "⏳ Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=sentiment-frontend -n $NAMESPACE --timeout=120s
kubectl wait --for=condition=ready pod -l app=sentiment-api -n $NAMESPACE --timeout=120s

echo "📊 Checking deployment status..."
kubectl get pods -n $NAMESPACE
kubectl get svc -n $NAMESPACE

echo "🌐 Accessing frontend service..."
minikube service sentiment-frontend -n $NAMESPACE --url

echo "✅ Deployment completed successfully!"
