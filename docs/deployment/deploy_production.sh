#!/bin/bash

# 🚀 Dermalens Production Deployment Script
# This script deploys the entire Dermalens application to Google Cloud

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_header() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Configuration
PROJECT_ID="dermalens-production"
REGION="us-central1"
SERVICE_ACCOUNT="dermalens-production@dermalens-production.iam.gserviceaccount.com"

# Check if gcloud is installed
check_gcloud() {
    print_header "Checking Google Cloud CLI..."
    
    if ! command -v gcloud &> /dev/null; then
        print_error "Google Cloud CLI is not installed. Please install it first."
        print_status "Installation guide: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    print_status "Google Cloud CLI found"
}

# Check if user is authenticated
check_auth() {
    print_header "Checking authentication..."
    
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "Not authenticated with Google Cloud. Please run: gcloud auth login"
        exit 1
    fi
    
    print_status "Authentication verified"
}

# Set up project
setup_project() {
    print_header "Setting up Google Cloud project..."
    
    # Create project if it doesn't exist
    if ! gcloud projects describe $PROJECT_ID &> /dev/null; then
        print_status "Creating project: $PROJECT_ID"
        gcloud projects create $PROJECT_ID --name="Dermalens Production"
    else
        print_status "Project $PROJECT_ID already exists"
    fi
    
    # Set as default project
    gcloud config set project $PROJECT_ID
    
    print_status "Project setup completed"
}

# Enable required APIs
enable_apis() {
    print_header "Enabling required APIs..."
    
    gcloud services enable \
        run.googleapis.com \
        bigquery.googleapis.com \
        storage.googleapis.com \
        aiplatform.googleapis.com \
        compute.googleapis.com \
        cloudbuild.googleapis.com \
        container.googleapis.com \
        sqladmin.googleapis.com \
        monitoring.googleapis.com \
        logging.googleapis.com \
        secretmanager.googleapis.com
    
    print_status "APIs enabled"
}

# Create service account
create_service_account() {
    print_header "Creating service account..."
    
    # Create service account if it doesn't exist
    if ! gcloud iam service-accounts describe $SERVICE_ACCOUNT &> /dev/null; then
        print_status "Creating service account: $SERVICE_ACCOUNT"
        gcloud iam service-accounts create dermalens-production \
            --display-name="Dermalens Production Service Account"
    else
        print_status "Service account already exists"
    fi
    
    # Grant necessary permissions
    print_status "Granting permissions..."
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
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/secretmanager.secretAccessor"
    
    print_status "Service account configured"
}

# Create BigQuery dataset
create_bigquery_dataset() {
    print_header "Creating BigQuery dataset..."
    
    # Create dataset
    bq mk --dataset $PROJECT_ID:skincare_data
    
    # Create products table
    bq mk --table \
        $PROJECT_ID:skincare_data.products \
        id:STRING,name:STRING,brand:STRING,description:STRING,ingredients:STRING,price:FLOAT,rating:FLOAT,review_count:INTEGER,product_type:STRING,skin_conditions:STRING,skin_types:STRING,url:STRING,image_url:STRING,allergen_free:BOOLEAN,fragrance_free:BOOLEAN,cruelty_free:BOOLEAN,vegan:BOOLEAN,spf_level:INTEGER,created_at:TIMESTAMP,updated_at:TIMESTAMP
    
    # Create user_analyses table
    bq mk --table \
        $PROJECT_ID:skincare_data.user_analyses \
        id:STRING,user_id:STRING,image_id:STRING,conditions_detected:STRING,skin_type:STRING,health_score:FLOAT,analysis_data:STRING,created_at:TIMESTAMP
    
    print_status "BigQuery dataset created"
}

# Create Cloud Storage bucket
create_storage_bucket() {
    print_header "Creating Cloud Storage bucket..."
    
    BUCKET_NAME="$PROJECT_ID-images"
    
    # Create bucket
    gsutil mb gs://$BUCKET_NAME
    
    # Set bucket permissions
    gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME
    
    print_status "Cloud Storage bucket created: gs://$BUCKET_NAME"
}

# Store secrets
store_secrets() {
    print_header "Storing secrets..."
    
    # Check if secrets exist
    if [ -f "secrets/gemini-api-key.txt" ]; then
        gcloud secrets create gemini-api-key --data-file=secrets/gemini-api-key.txt
    else
        print_warning "Gemini API key not found. Please create secrets/gemini-api-key.txt"
    fi
    
    if [ -f "secrets/elasticsearch-api-key.txt" ]; then
        gcloud secrets create elasticsearch-api-key --data-file=secrets/elasticsearch-api-key.txt
    else
        print_warning "Elasticsearch API key not found. Please create secrets/elasticsearch-api-key.txt"
    fi
    
    if [ -f "secrets/supabase-url.txt" ]; then
        gcloud secrets create supabase-url --data-file=secrets/supabase-url.txt
    else
        print_warning "Supabase URL not found. Please create secrets/supabase-url.txt"
    fi
    
    if [ -f "secrets/supabase-key.txt" ]; then
        gcloud secrets create supabase-key --data-file=secrets/supabase-key.txt
    else
        print_warning "Supabase key not found. Please create secrets/supabase-key.txt"
    fi
    
    # Grant access to service account
    gcloud secrets add-iam-policy-binding gemini-api-key \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/secretmanager.secretAccessor"
    
    gcloud secrets add-iam-policy-binding elasticsearch-api-key \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/secretmanager.secretAccessor"
    
    gcloud secrets add-iam-policy-binding supabase-url \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/secretmanager.secretAccessor"
    
    gcloud secrets add-iam-policy-binding supabase-key \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/secretmanager.secretAccessor"
    
    print_status "Secrets stored"
}

# Deploy backend
deploy_backend() {
    print_header "Deploying backend..."
    
    cd backend
    
    # Build and deploy
    gcloud run deploy dermalens-backend \
        --source . \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory 2Gi \
        --cpu 2 \
        --max-instances 10 \
        --min-instances 1 \
        --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID,GOOGLE_APPLICATION_CREDENTIALS=/app/production-key.json" \
        --set-secrets="GEMINI_API_KEY=gemini-api-key:latest,ELASTICSEARCH_API_KEY=elasticsearch-api-key:latest,SUPABASE_URL=supabase-url:latest,SUPABASE_KEY=supabase-key:latest"
    
    # Get backend URL
    BACKEND_URL=$(gcloud run services describe dermalens-backend --region=$REGION --format="value(status.url)")
    echo "Backend URL: $BACKEND_URL"
    
    cd ..
    print_status "Backend deployed"
}

# Deploy frontend
deploy_frontend() {
    print_header "Deploying frontend..."
    
    cd frontend
    
    # Build and deploy
    gcloud run deploy dermalens-frontend \
        --source . \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory 1Gi \
        --cpu 1 \
        --max-instances 5 \
        --min-instances 1 \
        --set-env-vars="NEXT_PUBLIC_API_URL=$BACKEND_URL"
    
    # Get frontend URL
    FRONTEND_URL=$(gcloud run services describe dermalens-frontend --region=$REGION --format="value(status.url)")
    echo "Frontend URL: $FRONTEND_URL"
    
    cd ..
    print_status "Frontend deployed"
}

# Test deployment
test_deployment() {
    print_header "Testing deployment..."
    
    # Test backend
    if curl -s $BACKEND_URL/health > /dev/null; then
        print_status "✅ Backend is healthy"
    else
        print_error "❌ Backend health check failed"
    fi
    
    # Test frontend
    if curl -s $FRONTEND_URL > /dev/null; then
        print_status "✅ Frontend is accessible"
    else
        print_error "❌ Frontend health check failed"
    fi
    
    # Test services status
    if curl -s $BACKEND_URL/api/services-status > /dev/null; then
        print_status "✅ Services status endpoint working"
    else
        print_warning "⚠️ Services status endpoint not accessible"
    fi
    
    print_status "Deployment testing completed"
}

# Create monitoring dashboard
create_monitoring() {
    print_header "Creating monitoring dashboard..."
    
    # Create monitoring dashboard
    gcloud monitoring dashboards create --config-from-file=monitoring-dashboard.json
    
    # Create alerting policy
    gcloud alpha monitoring policies create --policy-from-file=alert-policy.yaml
    
    print_status "Monitoring configured"
}

# Main deployment function
main() {
    echo "🚀 Dermalens Production Deployment"
    echo "=================================="
    echo ""
    
    check_gcloud
    check_auth
    setup_project
    enable_apis
    create_service_account
    create_bigquery_dataset
    create_storage_bucket
    store_secrets
    deploy_backend
    deploy_frontend
    test_deployment
    create_monitoring
    
    echo ""
    print_status "🎉 Deployment completed successfully!"
    echo ""
    echo "🌐 Frontend: $FRONTEND_URL"
    echo "🔧 Backend API: $BACKEND_URL"
    echo "📚 API Docs: $BACKEND_URL/docs"
    echo "📊 BigQuery: https://console.cloud.google.com/bigquery?project=$PROJECT_ID"
    echo "🗄️ Cloud Storage: https://console.cloud.google.com/storage?project=$PROJECT_ID"
    echo ""
    echo "Next steps:"
    echo "1. Configure your domain (optional)"
    echo "2. Set up SSL certificates"
    echo "3. Configure monitoring alerts"
    echo "4. Test all functionality"
    echo "5. Set up backup procedures"
}

# Show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  --backend-only Deploy only the backend"
    echo "  --frontend-only Deploy only the frontend"
    echo "  --no-secrets   Skip secret storage"
    echo "  --no-monitoring Skip monitoring setup"
    echo ""
    echo "Examples:"
    echo "  $0                    # Full deployment"
    echo "  $0 --backend-only     # Deploy only backend"
    echo "  $0 --no-secrets       # Deploy without storing secrets"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --backend-only)
            check_gcloud
            check_auth
            setup_project
            enable_apis
            create_service_account
            store_secrets
            deploy_backend
            test_deployment
            exit 0
            ;;
        --frontend-only)
            check_gcloud
            check_auth
            setup_project
            deploy_frontend
            test_deployment
            exit 0
            ;;
        --no-secrets)
            SKIP_SECRETS=true
            shift
            ;;
        --no-monitoring)
            SKIP_MONITORING=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Run main function
main
