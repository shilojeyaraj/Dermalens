# 🚀 Dermalens Deployment Guide

## Overview

This guide covers deploying Dermalens to production using Google Cloud Platform, including all services and integrations.

## Prerequisites

- Google Cloud Account with billing enabled
- Docker installed locally
- `gcloud` CLI installed and configured
- Domain name (optional, for custom domain)

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cloud Run     │    │   Cloud Run     │    │   Elastic Cloud │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Search)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   BigQuery      │    │   Cloud Storage │
                       │   (Analytics)   │◄──►│   (Images)      │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Fivetran      │
                       │   (Data Pipeline)│
                       └─────────────────┘
```

## Step 1: Google Cloud Setup

### 1.1 Create Project
```bash
# Create new project
gcloud projects create dermalens-production --name="Dermalens Production"

# Set as default project
gcloud config set project dermalens-production

# Enable billing (required for production)
# Go to: https://console.cloud.google.com/billing
# Link your project to a billing account
```

### 1.2 Enable Required APIs
```bash
# Enable all required APIs
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
  logging.googleapis.com
```

### 1.3 Create Service Account
```bash
# Create service account
gcloud iam service-accounts create dermalens-production \
    --display-name="Dermalens Production Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding dermalens-production \
    --member="serviceAccount:dermalens-production@dermalens-production.iam.gserviceaccount.com" \
    --role="roles/bigquery.admin"

gcloud projects add-iam-policy-binding dermalens-production \
    --member="serviceAccount:dermalens-production@dermalens-production.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding dermalens-production \
    --member="serviceAccount:dermalens-production@dermalens-production.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding dermalens-production \
    --member="serviceAccount:dermalens-production@dermalens-production.iam.gserviceaccount.com" \
    --role="roles/run.admin"

# Create and download key
gcloud iam service-accounts keys create production-key.json \
    --iam-account=dermalens-production@dermalens-production.iam.gserviceaccount.com
```

## Step 2: Database Setup

### 2.1 Create BigQuery Dataset
```bash
# Create dataset
bq mk --dataset dermalens-production:skincare_data

# Create tables
bq mk --table \
  dermalens-production:skincare_data.products \
  id:STRING,name:STRING,brand:STRING,description:STRING,ingredients:STRING,price:FLOAT,rating:FLOAT,review_count:INTEGER,product_type:STRING,skin_conditions:STRING,skin_types:STRING,url:STRING,image_url:STRING,allergen_free:BOOLEAN,fragrance_free:BOOLEAN,cruelty_free:BOOLEAN,vegan:BOOLEAN,spf_level:INTEGER,created_at:TIMESTAMP,updated_at:TIMESTAMP

bq mk --table \
  dermalens-production:skincare_data.user_analyses \
  id:STRING,user_id:STRING,image_id:STRING,conditions_detected:STRING,skin_type:STRING,health_score:FLOAT,analysis_data:STRING,created_at:TIMESTAMP
```

### 2.2 Create Cloud Storage Bucket
```bash
# Create bucket for images
gsutil mb gs://dermalens-production-images

# Set bucket permissions
gsutil iam ch allUsers:objectViewer gs://dermalens-production-images
```

## Step 3: Elasticsearch Setup

### 3.1 Elastic Cloud (Recommended)
1. Go to [https://cloud.elastic.co/](https://cloud.elastic.co/)
2. Sign up for free trial
3. Create deployment in Google Cloud region
4. Note down:
   - Elasticsearch URL
   - API Key
   - Username/Password

### 3.2 Self-Managed (Alternative)
```bash
# Create Compute Engine instance
gcloud compute instances create elasticsearch-prod \
    --zone=us-central1-a \
    --machine-type=e2-standard-4 \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=50GB \
    --boot-disk-type=pd-ssd

# Install Elasticsearch
gcloud compute ssh elasticsearch-prod --zone=us-central1-a
sudo apt-get update
sudo apt-get install openjdk-11-jdk
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.11.0-linux-x86_64.tar.gz
tar -xzf elasticsearch-8.11.0-linux-x86_64.tar.gz
cd elasticsearch-8.11.0

# Configure for production
cat > config/elasticsearch.yml << EOF
cluster.name: dermalens-production
node.name: node-1
network.host: 0.0.0.0
discovery.type: single-node
xpack.security.enabled: true
xpack.security.transport.ssl.enabled: true
xpack.security.http.ssl.enabled: true
EOF

# Start Elasticsearch
./bin/elasticsearch
```

## Step 4: Fivetran Setup

### 4.1 Create Fivetran Account
1. Go to [https://fivetran.com/](https://fivetran.com/)
2. Sign up for free trial
3. Get API credentials

### 4.2 Deploy Custom Connector
```bash
# Install Fivetran CLI
pip install fivetran-cli

# Configure credentials
fivetran configure --api-key=your-api-key --api-secret=your-api-secret

# Deploy connector
fivetran connectors create \
    --group-id=your-group-id \
    --service=skincare_connector \
    --config='{"gcp_project_id":"dermalens-production","bigquery_dataset":"skincare_data"}'
```

## Step 5: Backend Deployment

### 5.1 Create Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5.2 Deploy to Cloud Run
```bash
# Build and deploy
gcloud run deploy dermalens-backend \
    --source backend/ \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --min-instances 1 \
    --set-env-vars="GCP_PROJECT_ID=dermalens-production,GOOGLE_APPLICATION_CREDENTIALS=/app/production-key.json" \
    --set-secrets="GEMINI_API_KEY=gemini-api-key:latest,ELASTICSEARCH_API_KEY=elasticsearch-api-key:latest"

# Get backend URL
BACKEND_URL=$(gcloud run services describe dermalens-backend --region=us-central1 --format="value(status.url)")
echo "Backend URL: $BACKEND_URL"
```

## Step 6: Frontend Deployment

### 6.1 Create Dockerfile
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Change ownership
RUN chown -R nextjs:nodejs /app
USER nextjs

# Expose port
EXPOSE 3000

# Start application
CMD ["npm", "start"]
```

### 6.2 Deploy to Cloud Run
```bash
# Build and deploy
gcloud run deploy dermalens-frontend \
    --source frontend/ \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 5 \
    --min-instances 1 \
    --set-env-vars="NEXT_PUBLIC_API_URL=$BACKEND_URL"

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe dermalens-frontend --region=us-central1 --format="value(status.url)")
echo "Frontend URL: $FRONTEND_URL"
```

## Step 7: Environment Configuration

### 7.1 Create Production Environment
```bash
# Create production environment file
cat > backend/.env.production << EOF
# Google Cloud
GCP_PROJECT_ID=dermalens-production
GOOGLE_APPLICATION_CREDENTIALS=/app/production-key.json
BIGQUERY_DATASET=skincare_data
GCS_BUCKET=dermalens-production-images

# Gemini
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-1.5-pro
GEMINI_ENABLED=true

# Elasticsearch
ELASTICSEARCH_URL=https://your-cluster.es.us-central1.gcp.cloud.es.io:9243
ELASTICSEARCH_API_KEY=your-elasticsearch-api-key
ELASTICSEARCH_SSL_VERIFY=true

# Fivetran
FIVETRAN_API_KEY=your-fivetran-api-key
FIVETRAN_API_SECRET=your-fivetran-api-secret
FIVETRAN_GROUP_ID=your-group-id

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# Google Search
GOOGLE_API_KEY=your-google-search-key
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id

# CORS
ALLOWED_ORIGINS=https://dermalens-frontend-xxx-uc.a.run.app,https://dermalens.com
EOF
```

### 7.2 Store Secrets in Google Secret Manager
```bash
# Create secrets
echo -n "your-gemini-api-key" | gcloud secrets create gemini-api-key --data-file=-
echo -n "your-elasticsearch-api-key" | gcloud secrets create elasticsearch-api-key --data-file=-
echo -n "your-fivetran-api-key" | gcloud secrets create fivetran-api-key --data-file=-
echo -n "your-fivetran-api-secret" | gcloud secrets create fivetran-api-secret --data-file=-

# Grant access to service account
gcloud secrets add-iam-policy-binding gemini-api-key \
    --member="serviceAccount:dermalens-production@dermalens-production.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

## Step 8: Data Seeding

### 8.1 Seed Elasticsearch
```bash
# Run data seeding script
cd backend
python seed_elasticsearch_data.py
```

### 8.2 Test Data Pipeline
```bash
# Test Fivetran connector
python -c "
from fivetran_connector import skincare_connector
data = skincare_connector.extract_data({})
print(f'Extracted {sum(len(records) for records in data.values())} records')
"
```

## Step 9: Monitoring and Logging

### 9.1 Set Up Monitoring
```bash
# Create monitoring dashboard
gcloud monitoring dashboards create --config-from-file=monitoring-dashboard.json

# Create alerting policy
gcloud alpha monitoring policies create --policy-from-file=alert-policy.yaml
```

### 9.2 Set Up Logging
```bash
# Enable logging
gcloud logging sinks create dermalens-logs \
    bigquery.googleapis.com/projects/dermalens-production/datasets/logs \
    --log-filter="resource.type=cloud_run_revision"
```

## Step 10: Domain and SSL

### 10.1 Custom Domain (Optional)
```bash
# Map custom domain
gcloud run domain-mappings create \
    --service=dermalens-frontend \
    --domain=dermalens.com \
    --region=us-central1
```

### 10.2 SSL Certificate
```bash
# SSL is automatically provisioned by Google Cloud
# No additional configuration needed
```

## Step 11: Testing

### 11.1 Health Checks
```bash
# Test backend
curl https://dermalens-backend-xxx-uc.a.run.app/health

# Test frontend
curl https://dermalens-frontend-xxx-uc.a.run.app

# Test services status
curl https://dermalens-backend-xxx-uc.a.run.app/api/services-status
```

### 11.2 Load Testing
```bash
# Install artillery
npm install -g artillery

# Run load test
artillery run load-test.yml
```

## Step 12: Production Checklist

### 12.1 Pre-Launch
- [ ] All services deployed and running
- [ ] Database migrations completed
- [ ] SSL certificates configured
- [ ] Monitoring and alerts set up
- [ ] Security policies enforced
- [ ] Performance testing completed
- [ ] Backup strategy implemented
- [ ] Disaster recovery plan ready

### 12.2 Post-Launch
- [ ] Monitor performance metrics
- [ ] Check error rates and logs
- [ ] Verify data pipeline is working
- [ ] Test user authentication
- [ ] Validate AI analysis accuracy
- [ ] Monitor costs and usage

## Troubleshooting

### Common Issues

#### Backend Not Starting
```bash
# Check logs
gcloud logs read --service=dermalens-backend --limit=50

# Check service status
gcloud run services describe dermalens-backend --region=us-central1
```

#### Database Connection Issues
```bash
# Check BigQuery permissions
bq query --use_legacy_sql=false "SELECT 1"

# Check Cloud Storage access
gsutil ls gs://dermalens-production-images
```

#### Elasticsearch Connection Issues
```bash
# Test Elasticsearch connection
curl -X GET "https://your-cluster.es.us-central1.gcp.cloud.es.io:9243/"

# Check API key
curl -X GET "https://your-cluster.es.us-central1.gcp.cloud.es.io:9243/" \
  -H "Authorization: ApiKey your-api-key"
```

## Cost Optimization

### 12.1 Resource Optimization
```bash
# Set appropriate resource limits
gcloud run services update dermalens-backend \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 5

# Use preemptible instances for non-critical workloads
gcloud compute instances create elasticsearch-prod \
    --preemptible
```

### 12.2 Budget Alerts
```bash
# Create budget alert
gcloud billing budgets create \
    --billing-account=your-billing-account \
    --display-name="Dermalens Production Budget" \
    --budget-amount=500USD \
    --threshold-rule=percent=80 \
    --threshold-rule=percent=100
```

## Security

### 12.1 Security Best Practices
- Use Google Secret Manager for sensitive data
- Enable Cloud Armor for DDoS protection
- Implement proper CORS policies
- Use HTTPS everywhere
- Regular security updates

### 12.2 Compliance
- GDPR compliance for EU users
- CCPA compliance for California users
- HIPAA compliance for health data (if applicable)

## Backup and Recovery

### 12.1 Database Backups
```bash
# Backup BigQuery dataset
bq extract dermalens-production:skincare_data gs://dermalens-backups/skincare_data_backup_$(date +%Y%m%d).json

# Backup Cloud Storage
gsutil -m cp -r gs://dermalens-production-images gs://dermalens-backups/images_backup_$(date +%Y%m%d)
```

### 12.2 Disaster Recovery
- Multi-region deployment
- Automated backups
- Point-in-time recovery
- Cross-region replication

## Maintenance

### 12.1 Regular Maintenance
- Monitor resource usage
- Update dependencies
- Security patches
- Performance optimization
- Cost optimization

### 12.2 Updates
```bash
# Update backend
gcloud run deploy dermalens-backend --source backend/

# Update frontend
gcloud run deploy dermalens-frontend --source frontend/
```

## Support

- **Documentation**: [https://docs.dermalens.com](https://docs.dermalens.com)
- **Status Page**: [https://status.dermalens.com](https://status.dermalens.com)
- **Support Email**: support@dermalens.com
- **GitHub Issues**: [https://github.com/dermalens/deployment/issues](https://github.com/dermalens/deployment/issues)

---

**Your Dermalens application is now deployed and ready for production! 🚀**
