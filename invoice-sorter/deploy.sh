#!/bin/bash
# Deployment script for Invoice Sorter to Google Cloud Run

set -e

echo "========================================="
echo "Invoice Sorter - Cloud Run Deployment"
echo "========================================="

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
REGION=${GCP_REGION:-"us-central1"}
SERVICE_NAME=${SERVICE_NAME:-"invoice-sorter"}
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service Name: $SERVICE_NAME"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project
echo "Setting GCP project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    vision.googleapis.com \
    drive.googleapis.com \
    sheets.googleapis.com

# Build container image
echo "Building container image..."
gcloud builds submit --tag $IMAGE_NAME

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --region $REGION \
    --platform managed \
    --no-allow-unauthenticated \
    --set-env-vars "GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/credentials.json" \
    --set-env-vars "INPUT_FOLDER_ID=${INPUT_FOLDER_ID}" \
    --set-env-vars "REVIEW_FOLDER_ID=${REVIEW_FOLDER_ID}" \
    --set-env-vars "LOG_SHEET_ID=${LOG_SHEET_ID}" \
    --set-env-vars "VENDOR_MAPPING_SHEET_ID=${VENDOR_MAPPING_SHEET_ID}" \
    --set-env-vars "USE_VISION_API=${USE_VISION_API:-true}" \
    --memory 512Mi \
    --timeout 600

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "To set up a scheduled job (cron):"
echo "1. Create a Cloud Scheduler job"
echo "2. Set the target to your Cloud Run service"
echo "3. Configure the schedule (e.g., '0 */6 * * *' for every 6 hours)"
echo ""
echo "Example Cloud Scheduler command:"
echo "gcloud scheduler jobs create http invoice-sorter-cron \\"
echo "  --schedule='0 */6 * * *' \\"
echo "  --uri='https://${SERVICE_NAME}-<hash>-${REGION}.a.run.app' \\"
echo "  --http-method=GET \\"
echo "  --oidc-service-account-email='<service-account>@${PROJECT_ID}.iam.gserviceaccount.com'"
echo ""
