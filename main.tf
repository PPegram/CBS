# Terraform configuration for Cultural Bias Shield infrastructure
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
      filter         = "resource.type="cloud_run_revision""
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
