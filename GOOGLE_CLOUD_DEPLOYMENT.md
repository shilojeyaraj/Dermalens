# 🚀 Google Cloud Deployment Guide for Dermalens

This guide provides step-by-step instructions for deploying the Dermalens AI skincare application to Google Cloud Platform.

## 📋 **Prerequisites**

- Google Cloud Platform account
- Google Cloud CLI installed locally
- Docker installed (for containerized deployment)
- Domain name (optional, for custom domain)
- All environment variables configured

## 🏗️ **Architecture Overview**

```
Google Cloud Platform
├── 🌐 Cloud Run (Frontend - Next.js)
├── 🔧 Cloud Run (Backend - FastAPI)
├── 🗄️ Cloud SQL (PostgreSQL/Supabase)
├── 🔍 Elasticsearch Service
├── 📊 Cloud Storage (Models & Assets)
├── 🔐 Secret Manager (API Keys)
└── 🌍 Cloud CDN (Static Assets)
```

## 📦 **Step 1: Prepare Your Application**

### 1.1 **Backend Preparation**

Create `apps/api/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Set environment variables
ENV PORT=8080
ENV PYTHONPATH=/app

# Run the application
CMD ["python", "main.py"]
```

### 1.2 **Frontend Preparation**

Create `frontend/Dockerfile`:
```dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build the application
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

### 1.3 **Update Next.js Configuration**

Update `frontend/next.config.js`:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    domains: ['localhost', 'your-cloud-run-url'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
}

module.exports = nextConfig
```

## 🔧 **Step 2: Google Cloud Setup**

### 2.1 **Enable Required APIs**

```bash
# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 2.2 **Create Google Cloud Project**

```bash
# Create new project (replace with your project name)
gcloud projects create dermalens-production --name="Dermalens Production"

# Set the project
gcloud config set project dermalens-production

# Enable billing (you'll need to do this in the console)
```

### 2.3 **Configure Authentication**

```bash
# Authenticate with Google Cloud
gcloud auth login

# Set default region
gcloud config set run/region us-central1
gcloud config set compute/region us-central1
```

## 🗄️ **Step 3: Database Setup**

### 3.1 **Cloud SQL Setup**

```bash
# Create Cloud SQL instance
gcloud sql instances create dermalens-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --storage-type=SSD \
    --storage-size=10GB

# Create database
gcloud sql databases create dermalens --instance=dermalens-db

# Create user
gcloud sql users create dermalens-user \
    --instance=dermalens-db \
    --password=YOUR_SECURE_PASSWORD
```

### 3.2 **Supabase Alternative (Recommended)**

If using Supabase (easier setup):
1. Create Supabase project at https://supabase.com
2. Get connection string from Supabase dashboard
3. Use Supabase's built-in features

## 🔐 **Step 4: Secrets Management**

### 4.1 **Store Secrets in Secret Manager**

```bash
# Store API keys
echo -n "your-supabase-url" | gcloud secrets create supabase-url --data-file=-
echo -n "your-supabase-key" | gcloud secrets create supabase-key --data-file=-
echo -n "your-google-cloud-project-id" | gcloud secrets create google-cloud-project --data-file=-
echo -n "your-elasticsearch-url" | gcloud secrets create elasticsearch-url --data-file=-
echo -n "your-elasticsearch-username" | gcloud secrets create elasticsearch-username --data-file=-

echo -n "your-elasticsearch-password" | gcloud secrets create elasticsearch-password --data-file=-
```

### 4.2 **Grant Access to Secrets**

```bash
# Get your service account email
gcloud iam service-accounts list

# Grant access to secrets
gcloud secrets add-iam-policy-binding supabase-url \
    --member="serviceAccount:YOUR_SERVICE_ACCOUNT_EMAIL" \
    --role="roles/secretmanager.secretAccessor"
```

## 🚀 **Step 5: Deploy Backend (FastAPI)**

### 5.1 **Build and Deploy Backend**

```bash
# Navigate to backend directory
cd apps/api

# Build and deploy to Cloud Run
gcloud run deploy dermalens-backend \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=dermalens-production" \
    --set-secrets="SUPABASE_URL=supabase-url:latest,SUPABASE_KEY=supabase-key:latest"
```

### 5.2 **Test Backend Deployment**

```bash
# Get the service URL
gcloud run services describe dermalens-backend --region=us-central1 --format="value(status.url)"

# Test the health endpoint
curl https://YOUR_BACKEND_URL/health
```

## 🌐 **Step 6: Deploy Frontend (Next.js)**

### 6.1 **Build and Deploy Frontend**

```bash
# Navigate to frontend directory
cd frontend

# Build and deploy to Cloud Run
gcloud run deploy dermalens-frontend \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 3000 \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 5 \
    --set-env-vars="NEXT_PUBLIC_API_URL=https://YOUR_BACKEND_URL"
```

### 6.2 **Test Frontend Deployment**

```bash
# Get the service URL
gcloud run services describe dermalens-frontend --region=us-central1 --format="value(status.url)"
```

## 🔧 **Step 7: Configure Custom Domain (Optional)**

### 7.1 **Map Custom Domain**

```bash
# Map custom domain to Cloud Run service
gcloud run domain-mappings create \
    --service dermalens-frontend \
    --domain your-domain.com \
    --region us-central1
```

### 7.2 **Update DNS Records**

In your domain registrar:
- Add CNAME record: `www` → `ghs.googlehosted.com`
- Add A record: `@` → `216.58.220.35`

## 📊 **Step 8: Monitoring and Logging**

### 8.1 **Enable Monitoring**

```bash
# Enable Cloud Monitoring
gcloud services enable monitoring.googleapis.com

# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

### 8.2 **Set Up Alerts**

1. Go to Cloud Console → Monitoring → Alerting
2. Create alerting policies for:
   - High error rates
   - High latency
   - Resource usage

## 🔄 **Step 9: CI/CD Pipeline (Optional)**

### 9.1 **Create Cloud Build Configuration**

Create `cloudbuild.yaml`:
```yaml
steps:
  # Build and deploy backend
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/dermalens-backend', './apps/api']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/dermalens-backend']
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['run', 'deploy', 'dermalens-backend', '--image', 'gcr.io/$PROJECT_ID/dermalens-backend', '--region', 'us-central1']

  # Build and deploy frontend
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/dermalens-frontend', './frontend']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/dermalens-frontend']
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['run', 'deploy', 'dermalens-frontend', '--image', 'gcr.io/$PROJECT_ID/dermalens-frontend', '--region', 'us-central1']
```

### 9.2 **Set Up GitHub Integration**

```bash
# Connect GitHub repository
gcloud builds triggers create github \
    --repo-name=YOUR_GITHUB_REPO \
    --repo-owner=YOUR_GITHUB_USERNAME \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml
```

## 💰 **Step 10: Cost Optimization**

### 10.1 **Optimize Resource Usage**

```bash
# Set minimum instances to 0 (for cost savings)
gcloud run services update dermalens-backend \
    --region=us-central1 \
    --min-instances=0 \
    --max-instances=5

gcloud run services update dermalens-frontend \
    --region=us-central1 \
    --min-instances=0 \
    --max-instances=3
```

### 10.2 **Monitor Costs**

1. Go to Cloud Console → Billing
2. Set up budget alerts
3. Monitor usage in Cloud Monitoring

## 🧪 **Step 11: Testing Deployment**

### 11.1 **Health Checks**

```bash
# Test backend health
curl https://YOUR_BACKEND_URL/health

# Test frontend
curl https://YOUR_FRONTEND_URL/
```

### 11.2 **End-to-End Testing**

1. **Sign Up**: Test user registration
2. **Face Scan**: Test the face scan functionality
3. **Dashboard**: Verify analysis results display
4. **Product Search**: Test product recommendations

## 🚨 **Step 12: Security Configuration**

### 12.1 **Enable Security Features**

```bash
# Enable Cloud Armor (DDoS protection)
gcloud services enable compute.googleapis.com

# Configure CORS for API
# Add CORS headers in your FastAPI app
```

### 12.2 **SSL/TLS Configuration**

```bash
# SSL is automatically handled by Cloud Run
# No additional configuration needed
```

## 📋 **Step 13: Environment Variables Reference**

### 13.1 **Backend Environment Variables**

```bash
# Required for backend deployment
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
GOOGLE_CLOUD_PROJECT=your-project-id
ELASTICSEARCH_URL=your-elasticsearch-url
ELASTICSEARCH_USERNAME=your-username
ELASTICSEARCH_PASSWORD=your-password
JWT_SECRET=your-jwt-secret
```

### 13.2 **Frontend Environment Variables**

```bash
# Required for frontend deployment
NEXT_PUBLIC_API_URL=https://your-backend-url
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

## 🔧 **Step 14: Troubleshooting**

### 14.1 **Common Issues**

**Backend won't start:**
```bash
# Check logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=dermalens-backend" --limit 50

# Check environment variables
gcloud run services describe dermalens-backend --region=us-central1
```

**Frontend build fails:**
```bash
# Check build logs
gcloud builds log YOUR_BUILD_ID
```

**Database connection issues:**
```bash
# Test database connectivity
gcloud sql connect dermalens-db --user=dermalens-user
```

### 14.2 **Performance Optimization**

```bash
# Enable CDN for static assets
gcloud run services update dermalens-frontend \
    --region=us-central1 \
    --add-cloudsql-instances=dermalens-db
```

## 📊 **Step 15: Monitoring Dashboard**

### 15.1 **Create Monitoring Dashboard**

1. Go to Cloud Console → Monitoring → Dashboards
2. Create dashboard with:
   - Request count
   - Response time
   - Error rate
   - CPU/Memory usage

### 15.2 **Set Up Alerts**

```bash
# Create uptime check
gcloud monitoring uptime create https://YOUR_FRONTEND_URL/health
```

## 🎯 **Final Checklist**

- [ ] Backend deployed and accessible
- [ ] Frontend deployed and accessible
- [ ] Database connected and working
- [ ] Secrets properly configured
- [ ] SSL certificates active
- [ ] Monitoring configured
- [ ] Alerts set up
- [ ] Cost monitoring enabled
- [ ] CI/CD pipeline working (optional)
- [ ] Custom domain configured (optional)

## 📞 **Support Resources**

- **Google Cloud Documentation**: https://cloud.google.com/docs
- **Cloud Run Documentation**: https://cloud.google.com/run/docs
- **Cloud SQL Documentation**: https://cloud.google.com/sql/docs
- **Secret Manager Documentation**: https://cloud.google.com/secret-manager/docs

## 💡 **Pro Tips**

1. **Start Small**: Deploy with minimal resources and scale up
2. **Use Secrets**: Never hardcode API keys in your code
3. **Monitor Costs**: Set up budget alerts early
4. **Test Thoroughly**: Test all functionality before going live
5. **Backup Data**: Regular database backups are essential
6. **Security First**: Enable all security features
7. **Performance**: Monitor and optimize based on usage patterns

---

**🚀 Your Dermalens application should now be successfully deployed to Google Cloud Platform!**
