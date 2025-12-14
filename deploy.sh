#!/bin/bash

# 🚀 Dermalens Google Cloud Deployment Script
# This script automates the deployment of Dermalens to Google Cloud Platform

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="dermalens-production"
REGION="us-central1"
BACKEND_SERVICE="dermalens-backend"
FRONTEND_SERVICE="dermalens-frontend"

echo -e "${BLUE}🚀 Starting Dermalens Deployment to Google Cloud${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Google Cloud CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠️  Please authenticate with Google Cloud first:${NC}"
    echo "gcloud auth login"
    exit 1
fi

# Set the project
echo -e "${BLUE}📋 Setting project to ${PROJECT_ID}${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${BLUE}🔧 Enabling required Google Cloud APIs...${NC}"
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable monitoring.googleapis.com

# Set default region
gcloud config set run/region $REGION
gcloud config set compute/region $REGION

echo -e "${GREEN}✅ APIs enabled successfully${NC}"

# Deploy Backend
echo -e "${BLUE}🔧 Deploying Backend (FastAPI)...${NC}"
cd apps/api

# Build and deploy backend
gcloud run deploy $BACKEND_SERVICE \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID"

# Get backend URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region=$REGION --format="value(status.url)")
echo -e "${GREEN}✅ Backend deployed successfully: ${BACKEND_URL}${NC}"

# Test backend health
echo -e "${BLUE}🔍 Testing backend health...${NC}"
if curl -f -s "${BACKEND_URL}/health" > /dev/null; then
    echo -e "${GREEN}✅ Backend health check passed${NC}"
else
    echo -e "${YELLOW}⚠️  Backend health check failed, but deployment may still be starting${NC}"
fi

# Deploy Frontend
echo -e "${BLUE}🌐 Deploying Frontend (Next.js)...${NC}"
cd ../../frontend

# Build and deploy frontend
gcloud run deploy $FRONTEND_SERVICE \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 3000 \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 5 \
    --set-env-vars="NEXT_PUBLIC_API_URL=${BACKEND_URL}"

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --region=$REGION --format="value(status.url)")
echo -e "${GREEN}✅ Frontend deployed successfully: ${FRONTEND_URL}${NC}"

# Display deployment summary
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo -e "${BLUE}📊 Deployment Summary:${NC}"
echo -e "  Backend URL:  ${BACKEND_URL}"
echo -e "  Frontend URL: ${FRONTEND_URL}"
echo -e "  Region:       ${REGION}"
echo -e "  Project:      ${PROJECT_ID}"

echo -e "${YELLOW}📝 Next Steps:${NC}"
echo -e "  1. Configure your domain (optional)"
echo -e "  2. Set up monitoring and alerts"
echo -e "  3. Configure secrets in Secret Manager"
echo -e "  4. Set up CI/CD pipeline"

echo -e "${GREEN}🚀 Your Dermalens app is now live!${NC}"
