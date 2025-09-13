# Create GCP Cloud Build configuration
cloudbuild_yaml = '''# Cloud Build Configuration for Cultural Bias Shield
# Builds and deploys the full-stack application to Google Cloud Platform

steps:
  # Build the backend Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'gcr.io/$PROJECT_ID/cultural-bias-shield-backend:$BUILD_ID'
      - '-f'
      - 'backend/Dockerfile'
      - './backend'

  # Push the backend image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'gcr.io/$PROJECT_ID/cultural-bias-shield-backend:$BUILD_ID'

  # Build the frontend
  - name: 'node:18'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        cd frontend
        npm install
        npm run build

  # Build the frontend Docker image  
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'gcr.io/$PROJECT_ID/cultural-bias-shield-frontend:$BUILD_ID'
      - '-f'
      - 'frontend/Dockerfile'
      - './frontend'

  # Push the frontend image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'gcr.io/$PROJECT_ID/cultural-bias-shield-frontend:$BUILD_ID'

  # Deploy backend to Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'cultural-bias-shield-backend'
      - '--image'
      - 'gcr.io/$PROJECT_ID/cultural-bias-shield-backend:$BUILD_ID'
      - '--region'
      - '${_REGION}'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--memory'
      - '2Gi'
      - '--cpu'
      - '2'
      - '--max-instances'
      - '100'
      - '--set-env-vars'
      - 'GEMINI_API_KEY=${_GEMINI_API_KEY},GOOGLE_CLOUD_PROJECT=$PROJECT_ID'

  # Deploy frontend to Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'cultural-bias-shield-frontend'
      - '--image'
      - 'gcr.io/$PROJECT_ID/cultural-bias-shield-frontend:$BUILD_ID'
      - '--region'
      - '${_REGION}'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--memory'
      - '1Gi'
      - '--cpu'
      - '1'
      - '--max-instances'
      - '50'

  # Apply Terraform infrastructure (if needed)
  - name: 'hashicorp/terraform:1.6'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        cd deployment/terraform
        terraform init
        terraform plan -var="project_id=$PROJECT_ID" -var="region=${_REGION}"
        terraform apply -auto-approve -var="project_id=$PROJECT_ID" -var="region=${_REGION}"

# Substitutions for flexible deployment
substitutions:
  _REGION: 'us-central1'
  _GEMINI_API_KEY: 'your-gemini-api-key-here'

# Build options
options:
  machineType: 'E2_HIGHCPU_8'
  substitutionOption: 'ALLOW_LOOSE'

# Build timeout (30 minutes)
timeout: '1800s'

# Images to store in Container Registry
images:
  - 'gcr.io/$PROJECT_ID/cultural-bias-shield-backend:$BUILD_ID'
  - 'gcr.io/$PROJECT_ID/cultural-bias-shield-frontend:$BUILD_ID'
'''

with open('cloudbuild.yaml', 'w') as f:
    f.write(cloudbuild_yaml)

print("✅ Created cloudbuild.yaml - GCP Cloud Build configuration")

# Create Terraform infrastructure configuration
terraform_main = '''# Terraform configuration for Cultural Bias Shield infrastructure
# Creates necessary GCP resources for the application

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = "us-central1-a"
}

# Configure the Google Cloud Provider
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "containerregistry.googleapis.com",
    "aiplatform.googleapis.com",
    "storage.googleapis.com",
    "secretmanager.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com"
  ])
  
  service = each.value
  disable_on_destroy = false
}

# Cloud Storage bucket for data storage
resource "google_storage_bucket" "data_bucket" {
  name     = "${var.project_id}-cultural-bias-shield-data"
  location = var.region
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }

  depends_on = [google_project_service.apis]
}

# Secret Manager for API keys
resource "google_secret_manager_secret" "gemini_api_key" {
  secret_id = "gemini-api-key"
  
  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}

# Cloud Run IAM for backend service
resource "google_cloud_run_service_iam_binding" "backend_public" {
  location = var.region
  service  = "cultural-bias-shield-backend"
  role     = "roles/run.invoker"
  members  = ["allUsers"]

  depends_on = [google_project_service.apis]
}

# Cloud Run IAM for frontend service
resource "google_cloud_run_service_iam_binding" "frontend_public" {
  location = var.region
  service  = "cultural-bias-shield-frontend"
  role     = "roles/run.invoker"
  members  = ["allUsers"]

  depends_on = [google_project_service.apis]
}

# Service Account for the application
resource "google_service_account" "app_service_account" {
  account_id   = "cultural-bias-shield-sa"
  display_name = "Cultural Bias Shield Service Account"
  description  = "Service account for Cultural Bias Shield application"
}

# Grant necessary permissions to service account
resource "google_project_iam_member" "app_sa_permissions" {
  for_each = toset([
    "roles/aiplatform.user",
    "roles/storage.objectViewer", 
    "roles/secretmanager.secretAccessor",
    "roles/logging.logWriter",
    "roles/monitoring.writer"
  ])
  
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.app_service_account.email}"
}

# Cloud Monitoring alert policy for high error rates
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "Cultural Bias Shield - High Error Rate"
  combiner     = "OR"
  
  conditions {
    display_name = "Cloud Run error rate"
    
    condition_threshold {
      filter         = "resource.type=\"cloud_run_revision\""
      comparison     = "COMPARISON_GREATER_THAN"
      threshold_value = 0.05
      duration       = "300s"
      
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  
  notification_channels = []
  
  alert_strategy {
    auto_close = "1800s"
  }

  depends_on = [google_project_service.apis]
}

# Outputs
output "project_id" {
  value = var.project_id
}

output "region" {
  value = var.region
}

output "data_bucket_name" {
  value = google_storage_bucket.data_bucket.name
}

output "service_account_email" {
  value = google_service_account.app_service_account.email
}
'''

with open('main.tf', 'w') as f:
    f.write(terraform_main)

print("✅ Created main.tf - Terraform infrastructure configuration")

# Create Dockerfile for backend
backend_dockerfile = '''# Backend Dockerfile for Cultural Bias Shield
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:8080/api/health || exit 1

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--timeout", "300", "app:app"]
'''

with open('backend_Dockerfile', 'w') as f:
    f.write(backend_dockerfile)

print("✅ Created backend_Dockerfile - Docker configuration for Flask backend")

# Create Dockerfile for frontend
frontend_dockerfile = '''# Frontend Dockerfile for Cultural Bias Shield
FROM node:18-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built application
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
'''

with open('frontend_Dockerfile', 'w') as f:
    f.write(frontend_dockerfile)

print("✅ Created frontend_Dockerfile - Docker configuration for React frontend")