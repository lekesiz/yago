#!/bin/bash

# YAGO v8.0 - Google Cloud Platform Deployment Script
# This script automates the deployment to Google Cloud Run + Firestore

set -e  # Exit on error

echo "🚀 YAGO v8.0 - Google Cloud Deployment"
echo "======================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-""}
REGION=${GCP_REGION:-"europe-west1"}

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Validate prerequisites
print_info "Step 1: Validating prerequisites..."

if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI not found. Please install it: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

if [ -z "$PROJECT_ID" ]; then
    print_error "GCP_PROJECT_ID environment variable not set"
    echo "Please set it: export GCP_PROJECT_ID=your-project-id"
    exit 1
fi

print_info "✓ Prerequisites validated"

# Step 2: Set GCP project
print_info "Step 2: Setting GCP project to $PROJECT_ID..."
gcloud config set project "$PROJECT_ID"

# Step 3: Enable required APIs
print_info "Step 3: Enabling required Google Cloud APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    firestore.googleapis.com \
    containerregistry.googleapis.com \
    secretmanager.googleapis.com

print_info "✓ APIs enabled"

# Step 4: Create Firestore database
print_info "Step 4: Creating Firestore database..."
if ! gcloud firestore databases describe --format="value(name)" &> /dev/null; then
    gcloud firestore databases create --region="$REGION"
    print_info "✓ Firestore database created"
else
    print_warning "Firestore database already exists, skipping..."
fi

# Step 5: Deploy Firestore security rules
print_info "Step 5: Deploying Firestore security rules..."
gcloud firestore deploy --rules=deployment/firestore.rules

# Step 6: Deploy Firestore indexes
print_info "Step 6: Deploying Firestore indexes..."
gcloud firestore deploy --index=deployment/firestore.indexes.json

print_info "✓ Firestore configuration deployed"

# Step 7: Build and deploy using Cloud Build
print_info "Step 7: Building and deploying containers with Cloud Build..."
gcloud builds submit --config=deployment/cloudbuild.yaml .

print_info "✓ Containers built and deployed"

# Step 8: Get service URLs
print_info "Step 8: Retrieving service URLs..."
BACKEND_URL=$(gcloud run services describe yago-backend --region="$REGION" --format="value(status.url)")
FRONTEND_URL=$(gcloud run services describe yago-frontend --region="$REGION" --format="value(status.url)")

# Step 9: Update frontend environment variables
print_info "Step 9: Updating frontend with backend URL..."
gcloud run services update yago-frontend \
    --region="$REGION" \
    --set-env-vars="REACT_APP_API_URL=$BACKEND_URL"

print_info "✓ Frontend environment updated"

# Success message
echo ""
echo "=========================================="
echo -e "${GREEN}✓ DEPLOYMENT SUCCESSFUL!${NC}"
echo "=========================================="
echo ""
echo "📊 Service URLs:"
echo "   Backend:  $BACKEND_URL"
echo "   Frontend: $FRONTEND_URL"
echo ""
echo "🔗 Next Steps:"
echo "   1. Visit $FRONTEND_URL to access YAGO"
echo "   2. Check logs: gcloud run logs read --service=yago-backend"
echo "   3. Monitor metrics in Google Cloud Console"
echo ""
echo "📚 Documentation: https://github.com/lekesiz/yago"
echo "=========================================="
