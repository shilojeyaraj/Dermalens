# 🚀 Dermalens Deployment Checklist

## Pre-Deployment Setup

### 1. Google Cloud Setup
- [ ] Create Google Cloud Project: `dermalens-production`
- [ ] Enable billing for the project
- [ ] Install Google Cloud CLI locally
- [ ] Authenticate with Google Cloud: `gcloud auth login`
- [ ] Set default project: `gcloud config set project dermalens-production`

### 2. Environment Variables & Secrets
- [ ] Set up Supabase project and get credentials
- [ ] Configure Elasticsearch (or use Supabase's built-in search)
- [ ] Get Google AI Platform credentials
- [ ] Set up Google Custom Search API
- [ ] Store all secrets in Google Cloud Secret Manager

### 3. Database Setup
- [ ] Set up Supabase database
- [ ] Run database migrations
- [ ] Seed initial data (products, etc.)

## Deployment Steps

### 4. Backend Deployment
- [ ] Ensure `apps/api/Dockerfile` exists
- [ ] Ensure `apps/api/requirements.txt` is up to date
- [ ] Deploy backend: `gcloud run deploy dermalens-backend --source ./apps/api`
- [ ] Test backend health endpoint
- [ ] Configure environment variables for backend

### 5. Frontend Deployment
- [ ] Ensure `frontend/Dockerfile` exists
- [ ] Ensure `frontend/next.config.js` has `output: 'standalone'`
- [ ] Deploy frontend: `gcloud run deploy dermalens-frontend --source ./frontend`
- [ ] Test frontend URL
- [ ] Configure CORS for frontend-backend communication

### 6. Domain & SSL Setup (Optional)
- [ ] Purchase domain name
- [ ] Configure DNS records
- [ ] Set up SSL certificates
- [ ] Map custom domain to Cloud Run services

## Post-Deployment

### 7. Monitoring & Logging
- [ ] Set up Cloud Monitoring
- [ ] Configure alerting policies
- [ ] Set up log aggregation
- [ ] Monitor performance metrics

### 8. Security
- [ ] Review IAM permissions
- [ ] Set up firewall rules
- [ ] Configure CORS properly
- [ ] Enable security scanning

### 9. Performance Optimization
- [ ] Set up CDN for static assets
- [ ] Configure caching strategies
- [ ] Optimize database queries
- [ ] Set up auto-scaling

## Testing

### 10. End-to-End Testing
- [ ] Test user registration/login
- [ ] Test face scan functionality
- [ ] Test product recommendations
- [ ] Test payment processing (if applicable)
- [ ] Test mobile responsiveness

### 11. Load Testing
- [ ] Test with multiple concurrent users
- [ ] Monitor resource usage
- [ ] Test auto-scaling behavior
- [ ] Optimize based on results

## Maintenance

### 12. Backup & Recovery
- [ ] Set up database backups
- [ ] Test recovery procedures
- [ ] Document recovery steps

### 13. Updates & Maintenance
- [ ] Set up CI/CD pipeline
- [ ] Plan update schedule
- [ ] Monitor for security updates
- [ ] Plan maintenance windows

## Quick Commands

```bash
# Deploy everything
./deploy.ps1

# Deploy backend only
cd apps/api
gcloud run deploy dermalens-backend --source .

# Deploy frontend only
cd frontend
gcloud run deploy dermalens-frontend --source .

# Check deployment status
gcloud run services list

# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

## Troubleshooting

### Common Issues
1. **Build failures**: Check Dockerfile syntax and dependencies
2. **Runtime errors**: Check environment variables and secrets
3. **CORS issues**: Verify frontend-backend URL configuration
4. **Database connection**: Check Supabase credentials and network access
5. **Memory issues**: Increase Cloud Run memory allocation

### Useful Commands
```bash
# Check service status
gcloud run services describe dermalens-backend --region=us-central1

# View service logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=dermalens-backend" --limit 50

# Update service configuration
gcloud run services update dermalens-backend --region=us-central1 --memory=2Gi
```
