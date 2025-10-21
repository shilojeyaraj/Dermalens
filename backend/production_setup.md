# Production Setup Guide for Dermalens

## **1. Google Cloud Production Environment**

### **Create Production Project**
```bash
# Create production project
gcloud projects create dermalens-production --name="Dermalens Production"
gcloud config set project dermalens-production

# Enable billing (required for production)
# Go to: https://console.cloud.google.com/billing
# Link your project to a billing account

# Enable required APIs
gcloud services enable \
  bigquery.googleapis.com \
  storage.googleapis.com \
  aiplatform.googleapis.com \
  compute.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  container.googleapis.com \
  sqladmin.googleapis.com
```

### **Set Up Production Infrastructure**
```bash
# Create production service account
gcloud iam service-accounts create dermalens-production \
    --display-name="Dermalens Production Service Account"

# Grant production permissions
gcloud projects add-iam-policy-binding dermalens-production \
    --member="serviceAccount:dermalens-production@dermalens-production.iam.gserviceaccount.com" \
    --role="roles/bigquery.admin"

gcloud projects add-iam-policy-binding dermalens-production \
    --member="serviceAccount:dermalens-production@dermalens-production.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding dermalens-production \
    --member="serviceAccount:dermalens-production@dermalens-production.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Create and download production key
gcloud iam service-accounts keys create production-key.json \
    --iam-account=dermalens-production@dermalens-production.iam.gserviceaccount.com
```

## **2. Elasticsearch Production Setup**

### **Option A: Elastic Cloud (Recommended)**
```bash
# Sign up at https://cloud.elastic.co/
# Deploy cluster in Google Cloud region (us-central1)
# Choose production plan (4GB RAM minimum)

# Get connection details
ELASTICSEARCH_URL=https://your-cluster.es.us-central1.gcp.cloud.es.io:9243
ELASTICSEARCH_API_KEY=your-production-api-key
```

### **Option B: Self-Managed on Google Cloud**
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
xpack.security.authc.api_key.enabled: true
EOF

# Start Elasticsearch
./bin/elasticsearch
```

## **3. Fivetran Production Setup**

### **Set Up Production Connector**
```bash
# Install Fivetran CLI
pip install fivetran-cli

# Configure production credentials
fivetran configure --api-key=your-production-api-key --api-secret=your-production-secret

# Deploy production connector
fivetran connectors create \
    --group-id=your-group-id \
    --service=skincare_connector \
    --config='{"gcp_project_id":"dermalens-production","bigquery_dataset":"skincare_data"}'
```

## **4. Database Production Setup**

### **Set Up Cloud SQL**
```bash
# Create Cloud SQL instance
gcloud sql instances create dermalens-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --storage-type=SSD \
    --storage-size=20GB

# Create database
gcloud sql databases create dermalens --instance=dermalens-db

# Create user
gcloud sql users create dermalens-user \
    --instance=dermalens-db \
    --password=your-secure-password
```

### **Update Supabase for Production**
```bash
# Update your Supabase project settings
# Go to: https://supabase.com/dashboard
# Update API keys and database URL
# Enable Row Level Security
# Set up production environment variables
```

## **5. Application Deployment**

### **Deploy Backend to Cloud Run**
```bash
# Create Dockerfile for production
cat > Dockerfile << EOF
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Build and deploy
gcloud run deploy dermalens-backend \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10
```

### **Deploy Frontend to Cloud Run**
```bash
# Build Next.js for production
npm run build

# Create Dockerfile for frontend
cat > frontend/Dockerfile << EOF
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
EOF

# Deploy frontend
gcloud run deploy dermalens-frontend \
    --source ./frontend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 5
```

## **6. Production Environment Variables**

### **Backend (.env.production)**
```env
# Database
DATABASE_URL=postgresql://dermalens-user:password@/dermalens?host=/cloudsql/dermalens-production:us-central1:dermalens-db
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-production-supabase-key

# Elasticsearch
ELASTICSEARCH_URL=https://your-cluster.es.us-central1.gcp.cloud.es.io:9243
ELASTICSEARCH_API_KEY=your-production-api-key

# Fivetran
FIVETRAN_API_KEY=your-production-api-key
FIVETRAN_API_SECRET=your-production-api-secret

# Google Cloud
GCP_PROJECT_ID=dermalens-production
GOOGLE_APPLICATION_CREDENTIALS=/app/production-key.json
BIGQUERY_DATASET=skincare_data
GCS_BUCKET=dermalens-production-data

# OpenAI
OPENAI_API_KEY=your-production-openai-key

# Google Search
GOOGLE_SEARCH_API_KEY=your-production-google-search-key
GOOGLE_SEARCH_ENGINE_ID=your-production-search-engine-id

# CORS
ALLOWED_ORIGINS=https://dermalens-frontend-xxx-uc.a.run.app
```

### **Frontend (.env.production)**
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-production-supabase-anon-key
NEXT_PUBLIC_API_URL=https://dermalens-backend-xxx-uc.a.run.app
```

## **7. Production Data Setup**

### **Seed Production Database**
```python
# backend/seed_production_data.py
from elasticsearch_service import elasticsearch_service
from fivetran_connector import skincare_connector
import json

def seed_production_data():
    """Seed production database with real data"""
    
    # Load real product data
    with open('production_products.json', 'r') as f:
        products = json.load(f)
    
    # Index in Elasticsearch
    elasticsearch_service.bulk_index_products(products)
    
    # Load in Fivetran
    skincare_connector.load_data({"products": products}, "bigquery")
    
    print(f"Seeded {len(products)} products to production")

if __name__ == "__main__":
    seed_production_data()
```

## **8. Monitoring and Logging**

### **Set Up Cloud Monitoring**
```bash
# Enable monitoring
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com

# Create monitoring dashboard
gcloud monitoring dashboards create --config-from-file=monitoring-dashboard.json
```

### **Set Up Alerts**
```bash
# Create alerting policy
gcloud alpha monitoring policies create --policy-from-file=alert-policy.yaml
```

## **9. Security Configuration**

### **Set Up VPC and Firewall**
```bash
# Create VPC
gcloud compute networks create dermalens-vpc --subnet-mode=auto

# Create firewall rules
gcloud compute firewall-rules create allow-elasticsearch \
    --network=dermalens-vpc \
    --allow=tcp:9200 \
    --source-ranges=0.0.0.0/0

gcloud compute firewall-rules create allow-https \
    --network=dermalens-vpc \
    --allow=tcp:443 \
    --source-ranges=0.0.0.0/0
```

### **Enable Security Features**
```bash
# Enable Cloud Security Command Center
gcloud services enable securitycenter.googleapis.com

# Enable Cloud Asset Inventory
gcloud services enable cloudasset.googleapis.com
```

## **10. Cost Optimization**

### **Set Up Budget Alerts**
```bash
# Create budget
gcloud billing budgets create \
    --billing-account=your-billing-account \
    --display-name="Dermalens Production Budget" \
    --budget-amount=500USD \
    --threshold-rule=percent=80 \
    --threshold-rule=percent=100
```

### **Optimize Resources**
```bash
# Use preemptible instances for non-critical workloads
gcloud compute instances create elasticsearch-prod \
    --preemptible \
    --zone=us-central1-a

# Set up auto-scaling
gcloud run services update dermalens-backend \
    --min-instances=1 \
    --max-instances=10 \
    --cpu-throttling
```

## **11. Production Checklist**

### **Before Launch:**
- [ ] All services deployed and running
- [ ] Database migrations completed
- [ ] SSL certificates configured
- [ ] Monitoring and alerts set up
- [ ] Security policies enforced
- [ ] Performance testing completed
- [ ] Backup strategy implemented
- [ ] Disaster recovery plan ready

### **Post-Launch:**
- [ ] Monitor performance metrics
- [ ] Check error rates and logs
- [ ] Verify data pipeline is working
- [ ] Test user authentication
- [ ] Validate AI analysis accuracy
- [ ] Monitor costs and usage

## **12. Production URLs**

After deployment, your production URLs will be:
- **Frontend**: `https://dermalens-frontend-xxx-uc.a.run.app`
- **Backend**: `https://dermalens-backend-xxx-uc.a.run.app`
- **Elasticsearch**: `https://your-cluster.es.us-central1.gcp.cloud.es.io:9243`
- **BigQuery**: `https://console.cloud.google.com/bigquery`

## **13. Maintenance Commands**

### **Update Services**
```bash
# Update backend
gcloud run deploy dermalens-backend --source .

# Update frontend
gcloud run deploy dermalens-frontend --source ./frontend

# Restart Elasticsearch
gcloud compute ssh elasticsearch-prod --zone=us-central1-a --command="sudo systemctl restart elasticsearch"
```

### **Backup and Restore**
```bash
# Backup database
gcloud sql export sql dermalens-db gs://dermalens-backups/db-backup-$(date +%Y%m%d).sql

# Backup Elasticsearch
curl -X POST "localhost:9200/_snapshot/backup/snapshot_1?wait_for_completion=true"
```

This production setup will make your Dermalens project enterprise-ready and perfect for the hackathon demo! 🚀
