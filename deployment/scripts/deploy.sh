#!/bin/bash

###############################################################################
# YAGO Deployment Script
# One-click deployment for various environments
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="${YAGO_NAMESPACE:-yago}"
RELEASE_NAME="${YAGO_RELEASE:-yago}"
HELM_CHART_PATH="$(dirname "$0")/../kubernetes/helm/yago"
VALUES_FILE=""
ENVIRONMENT="production"

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl not found. Please install kubectl."
        exit 1
    fi
    print_success "kubectl found: $(kubectl version --client --short 2>/dev/null | head -1)"

    # Check helm
    if ! command -v helm &> /dev/null; then
        print_error "helm not found. Please install helm 3.0+."
        exit 1
    fi
    print_success "helm found: $(helm version --short)"

    # Check cluster connection
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot connect to Kubernetes cluster."
        exit 1
    fi
    print_success "Connected to Kubernetes cluster"

    echo ""
}

create_namespace() {
    print_header "Creating Namespace"

    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        print_info "Namespace $NAMESPACE already exists"
    else
        kubectl create namespace "$NAMESPACE"
        print_success "Namespace $NAMESPACE created"
    fi

    echo ""
}

setup_secrets() {
    print_header "Setting Up Secrets"

    print_warning "IMPORTANT: Update secrets in values file or use external secrets manager!"
    print_info "For production, use:"
    print_info "  - AWS Secrets Manager"
    print_info "  - Google Secret Manager"
    print_info "  - Azure Key Vault"
    print_info "  - HashiCorp Vault"

    echo ""
}

deploy_with_helm() {
    print_header "Deploying YAGO with Helm"

    # Build helm command
    HELM_CMD="helm upgrade --install $RELEASE_NAME $HELM_CHART_PATH"
    HELM_CMD="$HELM_CMD --namespace $NAMESPACE"
    HELM_CMD="$HELM_CMD --create-namespace"

    # Add values file if specified
    if [ -n "$VALUES_FILE" ]; then
        HELM_CMD="$HELM_CMD -f $VALUES_FILE"
    fi

    # Add wait flag
    HELM_CMD="$HELM_CMD --wait --timeout=10m"

    # Execute deployment
    print_info "Executing: $HELM_CMD"
    eval "$HELM_CMD"

    print_success "YAGO deployed successfully"
    echo ""
}

wait_for_pods() {
    print_header "Waiting for Pods to be Ready"

    print_info "Waiting for backend pods..."
    kubectl wait --for=condition=ready pod \
        -l app=yago,component=backend \
        -n "$NAMESPACE" \
        --timeout=5m

    print_info "Waiting for frontend pods..."
    kubectl wait --for=condition=ready pod \
        -l app=yago,component=frontend \
        -n "$NAMESPACE" \
        --timeout=5m

    print_success "All pods are ready"
    echo ""
}

check_deployment() {
    print_header "Checking Deployment Status"

    # Get pods
    echo "Pods:"
    kubectl get pods -n "$NAMESPACE"
    echo ""

    # Get services
    echo "Services:"
    kubectl get svc -n "$NAMESPACE"
    echo ""

    # Get ingress
    echo "Ingress:"
    kubectl get ingress -n "$NAMESPACE"
    echo ""
}

health_check() {
    print_header "Running Health Checks"

    # Get backend service
    BACKEND_SVC=$(kubectl get svc -n "$NAMESPACE" -l component=backend -o jsonpath='{.items[0].metadata.name}')

    if [ -z "$BACKEND_SVC" ]; then
        print_error "Backend service not found"
        return 1
    fi

    # Port forward and check health
    print_info "Port forwarding to backend service..."
    kubectl port-forward -n "$NAMESPACE" "svc/$BACKEND_SVC" 8000:8000 &
    PF_PID=$!

    sleep 5

    # Check health endpoint
    if curl -s http://localhost:8000/api/v1/monitoring/health > /dev/null; then
        print_success "Backend health check passed"
    else
        print_error "Backend health check failed"
    fi

    # Kill port forward
    kill $PF_PID 2>/dev/null || true

    echo ""
}

print_access_info() {
    print_header "Access Information"

    # Get ingress info
    INGRESS_HOST=$(kubectl get ingress -n "$NAMESPACE" -o jsonpath='{.items[0].spec.rules[0].host}' 2>/dev/null)

    if [ -n "$INGRESS_HOST" ]; then
        echo -e "${GREEN}Application URL: https://$INGRESS_HOST${NC}"
    else
        print_info "No ingress configured. Use port forwarding:"
        echo "  kubectl port-forward -n $NAMESPACE svc/$RELEASE_NAME-frontend 3000:3000"
        echo "  kubectl port-forward -n $NAMESPACE svc/$RELEASE_NAME-backend 8000:8000"
    fi

    echo ""
    print_info "Useful commands:"
    echo "  - View logs: kubectl logs -f deployment/$RELEASE_NAME-backend -n $NAMESPACE"
    echo "  - Get pods: kubectl get pods -n $NAMESPACE"
    echo "  - Describe pod: kubectl describe pod <pod-name> -n $NAMESPACE"
    echo "  - Shell into pod: kubectl exec -it <pod-name> -n $NAMESPACE -- /bin/bash"

    echo ""
}

rollback() {
    print_header "Rolling Back Deployment"

    helm rollback "$RELEASE_NAME" -n "$NAMESPACE"

    print_success "Rollback completed"
}

usage() {
    cat <<EOF
YAGO Deployment Script

Usage: $0 [OPTIONS]

Options:
    -h, --help              Show this help message
    -e, --environment ENV   Environment (production|staging|development) [default: production]
    -f, --values FILE       Custom values file
    -n, --namespace NS      Kubernetes namespace [default: yago]
    -r, --release NAME      Helm release name [default: yago]
    --rollback              Rollback to previous release
    --health-check          Run health check only
    --uninstall             Uninstall YAGO

Examples:
    # Deploy to production
    $0 --environment production

    # Deploy with custom values
    $0 -f my-values.yaml

    # Deploy to custom namespace
    $0 -n yago-prod -r yago-prod

    # Rollback deployment
    $0 --rollback

    # Uninstall
    $0 --uninstall

EOF
}

uninstall() {
    print_header "Uninstalling YAGO"

    helm uninstall "$RELEASE_NAME" -n "$NAMESPACE"

    print_success "YAGO uninstalled successfully"

    print_warning "Note: PVCs are not deleted automatically."
    print_info "To delete PVCs: kubectl delete pvc -n $NAMESPACE -l app=yago"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -f|--values)
            VALUES_FILE="$2"
            shift 2
            ;;
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -r|--release)
            RELEASE_NAME="$2"
            shift 2
            ;;
        --rollback)
            check_prerequisites
            rollback
            exit 0
            ;;
        --health-check)
            health_check
            exit 0
            ;;
        --uninstall)
            uninstall
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_header "YAGO Deployment - $ENVIRONMENT"

    check_prerequisites
    create_namespace
    setup_secrets
    deploy_with_helm
    wait_for_pods
    check_deployment
    health_check
    print_access_info

    print_success "Deployment completed successfully! 🚀"
}

# Run main
main
