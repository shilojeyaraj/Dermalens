#!/bin/bash

# Dermalens Production Deployment Script
# This script deploys the entire Dermalens application to Google Cloud

set -e  # Exit on any error

echo "🚀 Starting Dermalens Production Deployment..."

# Configuration
PROJECT_ID="dermalens-production"
REGION="us-central1"
SERVICE_ACCOUNT="dermalens-production@dermalens-production.iam.gserviceaccount.com"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    print_error "Not authenticated with gcloud. Please run 'gcloud auth login' first."
    exit 1
fi

# Set project
print_status "Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required APIs
print_status "Enabling required Google Cloud APIs..."
gcloud services enable \
    bigquery.googleapis.com \
    storage.googleapis.com \
    aiplatform.googleapis.com \
    compute.googleapis.com \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    container.googleapis.com \
    sqladmin.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com

# Create service account if it doesn't exist
print_status "Creating service account..."
if ! gcloud iam service-accounts describe $SERVICE_ACCOUNT &> /dev/null; then
    gcloud iam service-accounts create dermalens-production \
        --display-name="Dermalens Production Service Account"
    print_status "Service account created."
else
    print_warning "Service account already exists."
fi

# Grant necessary permissions
print_status "Granting permissions to service account..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/bigquery.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/run.admin"

# Create and download service account key
print_status "Creating service account key..."
gcloud iam service-accounts keys create production-key.json \
    --iam-account=$SERVICE_ACCOUNT

# Create BigQuery dataset
print_status "Creating BigQuery dataset..."
bq mk --dataset $PROJECT_ID:skincare_data

# Create Cloud Storage bucket
print_status "Creating Cloud Storage bucket..."
gsutil mb gs://$PROJECT_ID-data

# Create Cloud SQL instance
print_status "Creating Cloud SQL instance..."
if ! gcloud sql instances describe dermalens-db &> /dev/null; then
    gcloud sql instances create dermalens-db \
        --database-version=POSTGRES_15 \
        --tier=db-f1-micro \
        --region=$REGION \
        --storage-type=SSD \
        --storage-size=20GB
    
    # Create database
    gcloud sql databases create dermalens --instance=dermalens-db
    
    # Create user
    gcloud sql users create dermalens-user \
        --instance=dermalens-db \
        --password=$(openssl rand -base64 32)
    
    print_status "Cloud SQL instance created."
else
    print_warning "Cloud SQL instance already exists."
fi

# Deploy backend to Cloud Run
print_status "Deploying backend to Cloud Run..."
gcloud run deploy dermalens-backend \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID,GOOGLE_APPLICATION_CREDENTIALS=/app/production-key.json"

# Get backend URL
BACKEND_URL=$(gcloud run services describe dermalens-backend --region=$REGION --format="value(status.url)")
print_status "Backend deployed at: $BACKEND_URL"

# Deploy frontend to Cloud Run
print_status "Deploying frontend to Cloud Run..."
cd ../frontend

# Build frontend
npm install
npm run build

# Deploy frontend
gcloud run deploy dermalens-frontend \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 5 \
    --set-env-vars="NEXT_PUBLIC_API_URL=$BACKEND_URL"

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe dermalens-frontend --region=$REGION --format="value(status.url)")
print_status "Frontend deployed at: $FRONTEND_URL"

# Set up monitoring
print_status "Setting up monitoring..."
gcloud monitoring dashboards create --config-from-file=../monitoring-dashboard.json

# Create budget alert
print_status "Creating budget alert..."
gcloud billing budgets create \
    --billing-account=$(gcloud billing accounts list --format="value(name)" | head -1) \
    --display-name="Dermalens Production Budget" \
    --budget-amount=500USD \
    --threshold-rule=percent=80 \
    --threshold-rule=percent=100

# Seed production data
print_status "Seeding production data..."
cd ../backend
python seed_production_data.py

# Test deployment
print_status "Testing deployment..."
curl -f $BACKEND_URL/health || print_error "Backend health check failed"
curl -f $FRONTEND_URL || print_error "Frontend health check failed"

# Print deployment summary
echo ""
echo "🎉 Deployment Complete!"
echo "========================"
echo "Frontend URL: $FRONTEND_URL"
echo "Backend URL: $BACKEND_URL"
echo "BigQuery Dataset: $PROJECT_ID:skincare_data"
echo "Cloud Storage: gs://$PROJECT_ID-data"
echo "Cloud SQL: dermalens-db"
echo ""
echo "Next steps:"
echo "1. Update your domain DNS to point to the frontend URL"
echo "2. Set up SSL certificates"
echo "3. Configure monitoring alerts"
echo "4. Test all functionality"
echo "5. Set up automated backups"
echo ""
echo "🔐 Important: Keep your production-key.json file secure!"
echo "   Consider using Google Secret Manager for production."
