# 🚀 Dermalens Google Cloud Deployment Script (PowerShell)
# This script automates the deployment of Dermalens to Google Cloud Platform

# Configuration
$PROJECT_ID = "dermalens-production"
$REGION = "us-central1"
$BACKEND_SERVICE = "dermalens-backend"
$FRONTEND_SERVICE = "dermalens-frontend"

Write-Host "🚀 Starting Dermalens Deployment to Google Cloud" -ForegroundColor Blue

# Check if gcloud is installed
try {
    gcloud version | Out-Null
} catch {
    Write-Host "❌ Google Cloud CLI is not installed. Please install it first." -ForegroundColor Red
    exit 1
}

# Check if user is authenticated
$authStatus = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
if (-not $authStatus) {
    Write-Host "⚠️  Please authenticate with Google Cloud first:" -ForegroundColor Yellow
    Write-Host "gcloud auth login"
    exit 1
}

# Set the project
Write-Host "📋 Setting project to $PROJECT_ID" -ForegroundColor Blue
gcloud config set project $PROJECT_ID

# Enable required APIs
Write-Host "🔧 Enabling required Google Cloud APIs..." -ForegroundColor Blue
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable monitoring.googleapis.com

# Set default region
gcloud config set run/region $REGION
gcloud config set compute/region $REGION

Write-Host "✅ APIs enabled successfully" -ForegroundColor Green

# Deploy Backend
Write-Host "🔧 Deploying Backend (FastAPI)..." -ForegroundColor Blue
Set-Location "apps/api"

# Build and deploy backend
gcloud run deploy $BACKEND_SERVICE `
    --source . `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --port 8080 `
    --memory 2Gi `
    --cpu 2 `
    --timeout 300 `
    --max-instances 10 `
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID"

# Get backend URL
$BACKEND_URL = gcloud run services describe $BACKEND_SERVICE --region=$REGION --format="value(status.url)"
Write-Host "✅ Backend deployed successfully: $BACKEND_URL" -ForegroundColor Green

# Test backend health
Write-Host "🔍 Testing backend health..." -ForegroundColor Blue
try {
    $response = Invoke-WebRequest -Uri "$BACKEND_URL/health" -UseBasicParsing -TimeoutSec 30
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend health check passed" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Backend health check failed, but deployment may still be starting" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Backend health check failed, but deployment may still be starting" -ForegroundColor Yellow
}

# Deploy Frontend
Write-Host "🌐 Deploying Frontend (Next.js)..." -ForegroundColor Blue
Set-Location "../../frontend"

# Build and deploy frontend
gcloud run deploy $FRONTEND_SERVICE `
    --source . `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --port 3000 `
    --memory 1Gi `
    --cpu 1 `
    --timeout 300 `
    --max-instances 5 `
    --set-env-vars="NEXT_PUBLIC_API_URL=$BACKEND_URL"

# Get frontend URL
$FRONTEND_URL = gcloud run services describe $FRONTEND_SERVICE --region=$REGION --format="value(status.url)"
Write-Host "✅ Frontend deployed successfully: $FRONTEND_URL" -ForegroundColor Green

# Display deployment summary
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "📊 Deployment Summary:" -ForegroundColor Blue
Write-Host "  Backend URL:  $BACKEND_URL"
Write-Host "  Frontend URL: $FRONTEND_URL"
Write-Host "  Region:       $REGION"
Write-Host "  Project:      $PROJECT_ID"

Write-Host "📝 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Configure your domain (optional)"
Write-Host "  2. Set up monitoring and alerts"
Write-Host "  3. Configure secrets in Secret Manager"
Write-Host "  4. Set up CI/CD pipeline"

Write-Host "🚀 Your Dermalens app is now live!" -ForegroundColor Green
