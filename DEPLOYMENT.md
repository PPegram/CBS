# 🚀 Cultural Bias Shield - Deployment Guide

Complete guide to deploy Cultural Bias Shield to Google Cloud Platform for your hackathon.

## Prerequisites

- Google Cloud Platform account with billing enabled
- `gcloud` CLI installed ([Install guide](https://cloud.google.com/sdk/docs/install))
- Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Git installed
- Node.js 18+ and Python 3.11+ (for local development)

## 🎯 Quick Deploy (10 minutes)

### Step 1: Setup GCP Project
```bash
# Create new project (or use existing)
gcloud projects create cultural-bias-shield-demo --name="Cultural Bias Shield Demo"

# Set as default project
gcloud config set project cultural-bias-shield-demo

# Enable billing (required for Cloud Run)
# Go to: https://console.cloud.google.com/billing/projects

# Authenticate with your Google account
gcloud auth login
gcloud auth application-default login
```

### Step 2: Get Your Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API key"
3. Copy the key - you'll need it for deployment

### Step 3: Deploy Application
```bash
# Clone the repository
git clone https://github.com/yourorg/cultural-bias-shield.git
cd cultural-bias-shield

# Set environment variables
export PROJECT_ID="cultural-bias-shield-demo"  # Your actual project ID
export GEMINI_API_KEY="your-gemini-api-key-here"
export REGION="us-central1"

# One-command deployment
gcloud builds submit --config=deployment/cloudbuild.yaml \
  --substitutions=_GEMINI_API_KEY="$GEMINI_API_KEY",_REGION="$REGION"
```

### Step 4: Access Your Application
After deployment (5-8 minutes), get your URLs:
```bash
# Get frontend URL
gcloud run services list --filter="SERVICE:cultural-bias-shield-frontend" --format="value(STATUS.URL)"

# Get backend URL  
gcloud run services list --filter="SERVICE:cultural-bias-shield-backend" --format="value(STATUS.URL)"
```

**🎉 Your application is now live!**

## 🔧 Manual Deployment (Advanced)

### Step 1: Infrastructure Setup
```bash
# Navigate to Terraform directory
cd deployment/terraform

# Initialize Terraform
terraform init

# Plan infrastructure changes
terraform plan -var="project_id=$PROJECT_ID" -var="region=$REGION"

# Apply infrastructure
terraform apply -auto-approve -var="project_id=$PROJECT_ID" -var="region=$REGION"
```

### Step 2: Build and Deploy Backend
```bash
# Build backend Docker image
cd ../../backend
gcloud builds submit --tag gcr.io/$PROJECT_ID/cultural-bias-shield-backend

# Deploy to Cloud Run
gcloud run deploy cultural-bias-shield-backend \
  --image gcr.io/$PROJECT_ID/cultural-bias-shield-backend \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 100 \
  --set-env-vars GEMINI_API_KEY="$GEMINI_API_KEY",GOOGLE_CLOUD_PROJECT="$PROJECT_ID"
```

### Step 3: Build and Deploy Frontend
```bash
# Build frontend
cd ../frontend
npm install
npm run build

# Build Docker image
gcloud builds submit --tag gcr.io/$PROJECT_ID/cultural-bias-shield-frontend

# Deploy to Cloud Run
gcloud run deploy cultural-bias-shield-frontend \
  --image gcr.io/$PROJECT_ID/cultural-bias-shield-frontend \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 50
```

## 🌐 Custom Domain Setup (Optional)

```bash
# Map custom domain to frontend
gcloud run domain-mappings create \
  --service cultural-bias-shield-frontend \
  --domain your-domain.com \
  --region $REGION

# Map API subdomain to backend
gcloud run domain-mappings create \
  --service cultural-bias-shield-backend \
  --domain api.your-domain.com \
  --region $REGION
```

## 🔍 Monitoring & Logging

### View Application Logs
```bash
# Backend logs
gcloud logs tail "resource.type=cloud_run_revision resource.labels.service_name=cultural-bias-shield-backend"

# Frontend logs  
gcloud logs tail "resource.type=cloud_run_revision resource.labels.service_name=cultural-bias-shield-frontend"
```

### Monitoring Dashboard
1. Go to [Cloud Console Monitoring](https://console.cloud.google.com/monitoring)
2. Create dashboard for Cultural Bias Shield
3. Add widgets for:
   - Request count
   - Response latency
   - Error rate
   - Memory usage
   - CPU utilization

### Custom Alerts
```bash
# Create alert for high error rate
gcloud alpha monitoring policies create \
  --policy-from-file=deployment/monitoring/high-error-rate-policy.yaml
```

## 🔒 Security Configuration

### API Key Security
```bash
# Store Gemini API key in Secret Manager
gcloud secrets create gemini-api-key --data-file=<(echo -n "$GEMINI_API_KEY")

# Grant access to Cloud Run service
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:cultural-bias-shield-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Update Cloud Run to use secret
gcloud run services update cultural-bias-shield-backend \
  --update-secrets=GEMINI_API_KEY=gemini-api-key:latest \
  --region $REGION
```

### Network Security
```bash
# Create VPC connector (optional, for private resources)
gcloud compute networks vpc-access connectors create cultural-bias-connector \
  --region $REGION \
  --subnet default \
  --subnet-project $PROJECT_ID \
  --min-instances 2 \
  --max-instances 10

# Update Cloud Run to use VPC connector
gcloud run services update cultural-bias-shield-backend \
  --vpc-connector cultural-bias-connector \
  --region $REGION
```

## 📈 Performance Optimization

### Auto-scaling Configuration
```bash
# Configure auto-scaling
gcloud run services update cultural-bias-shield-backend \
  --min-instances 1 \
  --max-instances 100 \
  --concurrency 80 \
  --cpu-throttling \
  --region $REGION
```

### CDN Setup (for Frontend)
```bash
# Create Cloud Storage bucket for static assets
gsutil mb gs://$PROJECT_ID-cultural-bias-shield-static

# Enable CDN
gcloud compute backend-buckets create cultural-bias-static \
  --gcs-bucket-name $PROJECT_ID-cultural-bias-shield-static

# Create load balancer for CDN
gcloud compute url-maps create cultural-bias-lb \
  --default-backend-bucket cultural-bias-static
```

## 🧪 Testing Deployment

### Health Checks
```bash
# Test backend health
BACKEND_URL=$(gcloud run services list --filter="cultural-bias-shield-backend" --format="value(status.url)")
curl "$BACKEND_URL/api/health"

# Test frontend
FRONTEND_URL=$(gcloud run services list --filter="cultural-bias-shield-frontend" --format="value(status.url)")
curl -I "$FRONTEND_URL"
```

### Load Testing
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test API endpoint
ab -n 100 -c 10 -H "Content-Type: application/json" \
  -p test-payload.json \
  "$BACKEND_URL/api/analyze"
```

### Test Payload (test-payload.json)
```json
{
  "campaign_content": "Revolutionary fitness app for busy professionals",
  "target_countries": ["US", "UK", "JP"],
  "campaign_type": "social_media",
  "industry": "fitness"
}
```

## 🔄 CI/CD Pipeline

### Automatic Deployment
```bash
# Connect repository to Cloud Build
gcloud builds triggers create github \
  --repo-name cultural-bias-shield \
  --repo-owner yourorg \
  --branch-pattern "^main$" \
  --build-config deployment/cloudbuild.yaml \
  --substitutions _GEMINI_API_KEY="$GEMINI_API_KEY",_REGION="$REGION"
```

### Staging Environment
```bash
# Create staging deployment
gcloud run deploy cultural-bias-shield-backend-staging \
  --image gcr.io/$PROJECT_ID/cultural-bias-shield-backend \
  --region $REGION \
  --tag staging \
  --no-traffic
```

## 🛠️ Troubleshooting

### Common Issues

**1. Permission Denied Errors**
```bash
# Ensure proper IAM roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:your-email@domain.com" \
  --role="roles/run.admin"
```

**2. API Key Issues**
```bash
# Verify Gemini API key
curl -H "x-goog-api-key: $GEMINI_API_KEY" \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
  -d '{"contents":[{"parts":[{"text":"test"}]}]}'
```

**3. Build Failures**
```bash
# Check build logs
gcloud builds log $(gcloud builds list --limit=1 --format="value(id)")
```

**4. Service Not Accessible**
```bash
# Check IAM policy
gcloud run services get-iam-policy cultural-bias-shield-backend --region $REGION

# Make public if needed
gcloud run services add-iam-policy-binding cultural-bias-shield-backend \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --region $REGION
```

## 💰 Cost Optimization

### Estimated Monthly Costs (1000 analyses/day)
- **Cloud Run Backend:** ~$30/month
- **Cloud Run Frontend:** ~$15/month  
- **Cloud Storage:** ~$5/month
- **Gemini API Calls:** ~$50/month
- **Total:** ~$100/month

### Cost Reduction Tips
```bash
# Set CPU limits
gcloud run services update cultural-bias-shield-backend \
  --cpu=1 \
  --memory=1Gi \
  --region $REGION

# Enable CPU throttling
gcloud run services update cultural-bias-shield-backend \
  --cpu-throttling \
  --region $REGION

# Set up budget alerts
gcloud billing budgets create \
  --billing-account=$BILLING_ACCOUNT \
  --display-name="Cultural Bias Shield Budget" \
  --budget-amount=100USD
```

## 🎭 Demo Environment

For hackathon demos, use these optimized settings:

```bash
# Demo-optimized deployment
gcloud run deploy cultural-bias-shield-backend \
  --image gcr.io/$PROJECT_ID/cultural-bias-shield-backend \
  --region us-central1 \
  --memory 1Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10 \
  --concurrency 10 \
  --timeout 300 \
  --set-env-vars DEMO_MODE=true
```

## 📞 Support

- **Issues:** Check Cloud Console logs first
- **Performance:** Use Cloud Monitoring dashboards
- **API Problems:** Test with curl commands above
- **Deployment:** Verify all prerequisites are met

**Happy deploying! 🚀**