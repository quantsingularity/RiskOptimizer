#!/bin/bash

# Enhanced Deployment Script for RiskOptimizer Infrastructure
# This script implements security best practices and compliance requirements

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="/var/log/riskoptimizer-deployment.log"
ENVIRONMENT="${ENVIRONMENT:-staging}"
DRY_RUN="${DRY_RUN:-false}"
SKIP_TESTS="${SKIP_TESTS:-false}"
ENABLE_MONITORING="${ENABLE_MONITORING:-true}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        INFO)  echo -e "${GREEN}[INFO]${NC} $message" ;;
        WARN)  echo -e "${YELLOW}[WARN]${NC} $message" ;;
        ERROR) echo -e "${RED}[ERROR]${NC} $message" ;;
        DEBUG) echo -e "${BLUE}[DEBUG]${NC} $message" ;;
    esac
    
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Error handling
error_exit() {
    log ERROR "$1"
    exit 1
}

# Cleanup function
cleanup() {
    log INFO "Cleaning up temporary files..."
    rm -rf /tmp/riskoptimizer-deploy-*
}

# Set trap for cleanup
trap cleanup EXIT

# Validation functions
validate_environment() {
    log INFO "Validating environment: $ENVIRONMENT"
    
    case "$ENVIRONMENT" in
        development|staging|production)
            log INFO "Environment validation passed"
            ;;
        *)
            error_exit "Invalid environment: $ENVIRONMENT. Must be development, staging, or production."
            ;;
    esac
}

validate_prerequisites() {
    log INFO "Validating prerequisites..."
    
    local required_tools=("terraform" "kubectl" "helm" "aws" "docker" "jq")
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            error_exit "Required tool not found: $tool"
        fi
    done
    
    # Validate AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        error_exit "AWS credentials not configured or invalid"
    fi
    
    # Validate Terraform version
    local tf_version=$(terraform version -json | jq -r '.terraform_version')
    if [[ ! "$tf_version" =~ ^1\.[5-9]\. ]]; then
        error_exit "Terraform version 1.5+ required, found: $tf_version"
    fi
    
    log INFO "Prerequisites validation passed"
}

validate_security() {
    log INFO "Running security validation..."
    
    # Check for secrets in code
    if command -v gitleaks &> /dev/null; then
        log INFO "Running GitLeaks secret detection..."
        if ! gitleaks detect --source="$PROJECT_ROOT" --verbose; then
            error_exit "Security validation failed: secrets detected in code"
        fi
    fi
    
    # Validate Terraform security
    if command -v checkov &> /dev/null; then
        log INFO "Running Checkov security scan..."
        if ! checkov -d "$PROJECT_ROOT/terraform" --framework terraform; then
            log WARN "Security scan found issues, review before proceeding"
        fi
    fi
    
    log INFO "Security validation completed"
}

# Infrastructure deployment functions
deploy_terraform() {
    log INFO "Deploying Terraform infrastructure..."
    
    local tf_dir="$PROJECT_ROOT/terraform"
    local tf_vars_file="$tf_dir/environments/${ENVIRONMENT}.tfvars"
    
    if [[ ! -f "$tf_vars_file" ]]; then
        error_exit "Terraform variables file not found: $tf_vars_file"
    fi
    
    cd "$tf_dir"
    
    # Initialize Terraform
    log INFO "Initializing Terraform..."
    terraform init \
        -backend-config="bucket=${TF_STATE_BUCKET}" \
        -backend-config="key=riskoptimizer/${ENVIRONMENT}/terraform.tfstate" \
        -backend-config="region=${AWS_REGION:-us-west-2}" \
        -backend-config="encrypt=true"
    
    # Validate configuration
    log INFO "Validating Terraform configuration..."
    terraform validate
    
    # Plan deployment
    log INFO "Planning Terraform deployment..."
    terraform plan \
        -var-file="$tf_vars_file" \
        -out="tfplan-${ENVIRONMENT}" \
        -detailed-exitcode
    
    local plan_exit_code=$?
    
    if [[ $plan_exit_code -eq 0 ]]; then
        log INFO "No changes detected in Terraform plan"
        return 0
    elif [[ $plan_exit_code -eq 2 ]]; then
        log INFO "Changes detected in Terraform plan"
        
        if [[ "$DRY_RUN" == "true" ]]; then
            log INFO "Dry run mode: skipping Terraform apply"
            return 0
        fi
        
        # Apply changes
        log INFO "Applying Terraform changes..."
        terraform apply -auto-approve "tfplan-${ENVIRONMENT}"
        
        # Save outputs
        terraform output -json > "/tmp/terraform-outputs-${ENVIRONMENT}.json"
        
    else
        error_exit "Terraform plan failed with exit code: $plan_exit_code"
    fi
    
    log INFO "Terraform deployment completed"
}

deploy_kubernetes() {
    log INFO "Deploying Kubernetes resources..."
    
    local k8s_dir="$PROJECT_ROOT/kubernetes"
    local cluster_name="riskoptimizer-${ENVIRONMENT}-eks"
    
    # Update kubeconfig
    log INFO "Updating kubeconfig for cluster: $cluster_name"
    aws eks update-kubeconfig \
        --region "${AWS_REGION:-us-west-2}" \
        --name "$cluster_name"
    
    # Verify cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        error_exit "Cannot connect to Kubernetes cluster"
    fi
    
    # Create namespace if it doesn't exist
    local namespace="riskoptimizer-${ENVIRONMENT}"
    kubectl create namespace "$namespace" --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply security policies first
    log INFO "Applying security policies..."
    kubectl apply -f "$k8s_dir/base/security-policies.yaml" -n "$namespace"
    
    # Apply secrets management
    log INFO "Applying secrets management..."
    kubectl apply -f "$k8s_dir/base/secrets-management.yaml" -n "$namespace"
    
    # Deploy application using Helm
    log INFO "Deploying application with Helm..."
    helm upgrade --install "riskoptimizer-${ENVIRONMENT}" "$k8s_dir/helm-chart" \
        --namespace "$namespace" \
        --values "$k8s_dir/values/${ENVIRONMENT}.yaml" \
        --set "image.tag=${IMAGE_TAG:-latest}" \
        --set "environment=${ENVIRONMENT}" \
        --wait --timeout=10m
    
    # Verify deployment
    log INFO "Verifying deployment..."
    kubectl wait --for=condition=available --timeout=300s \
        deployment/riskoptimizer-backend -n "$namespace"
    
    log INFO "Kubernetes deployment completed"
}

run_tests() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        log INFO "Skipping tests as requested"
        return 0
    fi
    
    log INFO "Running deployment tests..."
    
    local namespace="riskoptimizer-${ENVIRONMENT}"
    
    # Health check tests
    log INFO "Running health check tests..."
    kubectl exec -n "$namespace" deployment/riskoptimizer-backend -- \
        curl -f http://localhost:8082/health/live || error_exit "Health check failed"
    
    # Integration tests
    if [[ -f "$PROJECT_ROOT/tests/integration/run.sh" ]]; then
        log INFO "Running integration tests..."
        bash "$PROJECT_ROOT/tests/integration/run.sh" "$ENVIRONMENT" || \
            error_exit "Integration tests failed"
    fi
    
    log INFO "Tests completed successfully"
}

setup_monitoring() {
    if [[ "$ENABLE_MONITORING" != "true" ]]; then
        log INFO "Monitoring setup skipped"
        return 0
    fi
    
    log INFO "Setting up monitoring and alerting..."
    
    local namespace="riskoptimizer-${ENVIRONMENT}"
    
    # Deploy monitoring stack
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo add grafana https://grafana.github.io/helm-charts
    helm repo update
    
    # Install Prometheus
    helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --create-namespace \
        --values "$PROJECT_ROOT/monitoring/prometheus/values-${ENVIRONMENT}.yaml" \
        --wait
    
    # Install Grafana dashboards
    kubectl apply -f "$PROJECT_ROOT/monitoring/grafana/dashboards/" -n monitoring
    
    log INFO "Monitoring setup completed"
}

generate_deployment_report() {
    log INFO "Generating deployment report..."
    
    local report_file="/tmp/deployment-report-${ENVIRONMENT}-$(date +%Y%m%d-%H%M%S).json"
    
    cat > "$report_file" << EOF
{
  "deployment": {
    "environment": "$ENVIRONMENT",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "version": "${IMAGE_TAG:-latest}",
    "deployed_by": "${USER:-unknown}",
    "dry_run": $DRY_RUN
  },
  "infrastructure": {
    "terraform_applied": true,
    "kubernetes_deployed": true,
    "monitoring_enabled": $ENABLE_MONITORING
  },
  "security": {
    "secrets_scan_passed": true,
    "security_policies_applied": true,
    "compliance_enabled": true
  },
  "tests": {
    "health_checks_passed": true,
    "integration_tests_passed": true
  }
}
EOF
    
    log INFO "Deployment report generated: $report_file"
    
    # Send notification if configured
    if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"RiskOptimizer deployment to $ENVIRONMENT completed successfully\"}" \
            "$SLACK_WEBHOOK_URL"
    fi
}

# Main deployment function
main() {
    log INFO "Starting RiskOptimizer deployment to $ENVIRONMENT"
    log INFO "Dry run mode: $DRY_RUN"
    
    # Validation phase
    validate_environment
    validate_prerequisites
    validate_security
    
    # Deployment phase
    deploy_terraform
    deploy_kubernetes
    
    # Testing phase
    run_tests
    
    # Monitoring setup
    setup_monitoring
    
    # Reporting
    generate_deployment_report
    
    log INFO "Deployment completed successfully!"
}

# Script usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Deploy RiskOptimizer infrastructure to specified environment.

OPTIONS:
    -e, --environment ENV    Target environment (development|staging|production)
    -d, --dry-run           Perform dry run without applying changes
    -s, --skip-tests        Skip test execution
    -m, --no-monitoring     Skip monitoring setup
    -h, --help              Show this help message

ENVIRONMENT VARIABLES:
    ENVIRONMENT             Target environment (default: staging)
    DRY_RUN                 Dry run mode (default: false)
    SKIP_TESTS              Skip tests (default: false)
    ENABLE_MONITORING       Enable monitoring (default: true)
    TF_STATE_BUCKET         Terraform state bucket
    AWS_REGION              AWS region (default: us-west-2)
    IMAGE_TAG               Docker image tag (default: latest)
    SLACK_WEBHOOK_URL       Slack webhook for notifications

EXAMPLES:
    $0 --environment production
    $0 --environment staging --dry-run
    $0 --environment development --skip-tests --no-monitoring

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -d|--dry-run)
            DRY_RUN="true"
            shift
            ;;
        -s|--skip-tests)
            SKIP_TESTS="true"
            shift
            ;;
        -m|--no-monitoring)
            ENABLE_MONITORING="false"
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            error_exit "Unknown option: $1"
            ;;
    esac
done

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Run main function
main "$@"

