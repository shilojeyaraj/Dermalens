#!/bin/bash

# Deploy backend
echo "🚀 Deploying backend..."
gcloud run deploy dermalens-backend --source ./apps/api --platform managed --region us-central1 --allow-unauthenticated --port 8000 --memory 2Gi --cpu 2 --timeout 600 --max-instances 5

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 30

# Seed the database
echo "🌱 Seeding Elasticsearch database..."
cd backend
python seed_elasticsearch_data.py

# Deploy frontend
echo "🎨 Deploying frontend..."
cd ../frontend
gcloud run deploy dermalens-frontend --source . --platform managed --region us-central1 --allow-unauthenticated --port 3000 --memory 2Gi --cpu 2 --timeout 600 --max-instances 5 --set-env-vars="NEXT_PUBLIC_API_URL=https://dermalens-backend-941238576063.us-central1.run.app,NODE_ENV=production"

echo "✅ Deployment complete!"
