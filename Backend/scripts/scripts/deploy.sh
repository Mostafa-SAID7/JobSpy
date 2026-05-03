#!/bin/bash

################################################################################
# JobSpy Production Deployment Script
# 
# This script handles the deployment of the JobSpy application to production
# including building Docker images, pushing to registry, and deploying services
################################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-docker.io}"
BACKEND_IMAGE="${DOCKER_REGISTRY}/jobspy-backend"
FRONTEND_IMAGE="${DOCKER_REGISTRY}/jobspy-frontend"
DEPLOYMENT_ENV="${DEPLOYMENT_ENV:-production}"
LOG_FILE="${PROJECT_ROOT}/deployment.log"

################################################################################
# Utility Functions
################################################################################

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✓ $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ✗ $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠ $1${NC}" | tee -a "$LOG_FILE"
}

print_header() {
    echo -e "\n${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}\n"
}

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    log_success "Docker is installed"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    log_success "Docker Compose is installed"
    
    # Check environment file
    if [ ! -f "$PROJECT_ROOT/.env.production" ]; then
        log_error ".env.production file not found"
        log "Please copy .env.production.example to .env.production and fill in the values"
        exit 1
    fi
    log_success ".env.production file found"
    
    # Check Docker daemon
    if ! docker ps &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    log_success "Docker daemon is running"
}

build_backend() {
    print_header "Building Backend Image"
    
    log "Building backend image: $BACKEND_IMAGE"
    
    docker build \
        -f "$PROJECT_ROOT/Backend/Dockerfile" \
        -t "$BACKEND_IMAGE:latest" \
        -t "$BACKEND_IMAGE:$(date +%Y%m%d_%H%M%S)" \
        --build-arg ENVIRONMENT=production \
        "$PROJECT_ROOT/Backend"
    
    if [ $? -eq 0 ]; then
        log_success "Backend image built successfully"
    else
        log_error "Failed to build backend image"
        exit 1
    fi
}

build_frontend() {
    print_header "Building Frontend Image"
    
    log "Building frontend image: $FRONTEND_IMAGE"
    
    docker build \
        -f "$PROJECT_ROOT/Frontend/Dockerfile" \
        -t "$FRONTEND_IMAGE:latest" \
        -t "$FRONTEND_IMAGE:$(date +%Y%m%d_%H%M%S)" \
        --build-arg ENVIRONMENT=production \
        "$PROJECT_ROOT/Frontend"
    
    if [ $? -eq 0 ]; then
        log_success "Frontend image built successfully"
    else
        log_error "Failed to build frontend image"
        exit 1
    fi
}

push_images() {
    print_header "Pushing Images to Registry"
    
    if [ "$DOCKER_REGISTRY" = "docker.io" ]; then
        log_warning "Using Docker Hub. Make sure you're logged in with 'docker login'"
    fi
    
    log "Pushing backend image..."
    docker push "$BACKEND_IMAGE:latest"
    
    if [ $? -eq 0 ]; then
        log_success "Backend image pushed successfully"
    else
        log_error "Failed to push backend image"
        exit 1
    fi
    
    log "Pushing frontend image..."
    docker push "$FRONTEND_IMAGE:latest"
    
    if [ $? -eq 0 ]; then
        log_success "Frontend image pushed successfully"
    else
        log_error "Failed to push frontend image"
        exit 1
    fi
}

backup_current_deployment() {
    print_header "Backing Up Current Deployment"
    
    BACKUP_DIR="$PROJECT_ROOT/backups/deployment"
    mkdir -p "$BACKUP_DIR"
    
    BACKUP_FILE="$BACKUP_DIR/deployment_$(date +%Y%m%d_%H%M%S).tar.gz"
    
    log "Creating backup: $BACKUP_FILE"
    
    tar czf "$BACKUP_FILE" \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='__pycache__' \
        --exclude='.env.production' \
        "$PROJECT_ROOT"
    
    if [ $? -eq 0 ]; then
        log_success "Deployment backed up: $BACKUP_FILE"
    else
        log_error "Failed to create backup"
        exit 1
    fi
}

stop_services() {
    print_header "Stopping Current Services"
    
    log "Stopping services..."
    
    cd "$PROJECT_ROOT"
    docker-compose -f config/docker-compose.production.yml down
    
    if [ $? -eq 0 ]; then
        log_success "Services stopped successfully"
    else
        log_error "Failed to stop services"
        exit 1
    fi
}

start_services() {
    print_header "Starting Services"
    
    log "Starting services..."
    
    cd "$PROJECT_ROOT"
    docker-compose -f config/docker-compose.production.yml up -d
    
    if [ $? -eq 0 ]; then
        log_success "Services started successfully"
    else
        log_error "Failed to start services"
        exit 1
    fi
}

run_migrations() {
    print_header "Running Database Migrations"
    
    log "Running Alembic migrations..."
    
    docker-compose -f "$PROJECT_ROOT/config/docker-compose.production.yml" \
        exec -T backend alembic upgrade head
    
    if [ $? -eq 0 ]; then
        log_success "Migrations completed successfully"
    else
        log_error "Failed to run migrations"
        exit 1
    fi
}

health_check() {
    print_header "Performing Health Checks"
    
    log "Waiting for services to be ready..."
    sleep 10
    
    # Check backend health
    log "Checking backend health..."
    BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
    
    if [ "$BACKEND_HEALTH" = "200" ]; then
        log_success "Backend is healthy"
    else
        log_error "Backend health check failed (HTTP $BACKEND_HEALTH)"
        return 1
    fi
    
    # Check frontend health
    log "Checking frontend health..."
    FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/)
    
    if [ "$FRONTEND_HEALTH" = "200" ]; then
        log_success "Frontend is healthy"
    else
        log_error "Frontend health check failed (HTTP $FRONTEND_HEALTH)"
        return 1
    fi
    
    # Check database connection
    log "Checking database connection..."
    docker-compose -f "$PROJECT_ROOT/config/docker-compose.production.yml" \
        exec -T backend python -c "from app.core.database import engine; engine.connect()"
    
    if [ $? -eq 0 ]; then
        log_success "Database connection is healthy"
    else
        log_error "Database connection failed"
        return 1
    fi
    
    log_success "All health checks passed"
}

smoke_tests() {
    print_header "Running Smoke Tests"
    
    log "Running basic API tests..."
    
    # Test authentication endpoint
    log "Testing authentication endpoint..."
    AUTH_TEST=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
        -H "Content-Type: application/json" \
        -d '{"email":"test@example.com","password":"test"}' \
        -o /dev/null -w "%{http_code}")
    
    if [ "$AUTH_TEST" = "422" ] || [ "$AUTH_TEST" = "401" ]; then
        log_success "Authentication endpoint is responding"
    else
        log_warning "Authentication endpoint returned unexpected status: $AUTH_TEST"
    fi
    
    # Test jobs endpoint
    log "Testing jobs endpoint..."
    JOBS_TEST=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/jobs)
    
    if [ "$JOBS_TEST" = "200" ] || [ "$JOBS_TEST" = "401" ]; then
        log_success "Jobs endpoint is responding"
    else
        log_error "Jobs endpoint returned unexpected status: $JOBS_TEST"
        return 1
    fi
    
    log_success "Smoke tests completed"
}

rollback() {
    print_header "Rolling Back Deployment"
    
    log_warning "Rolling back to previous deployment..."
    
    # Stop current services
    docker-compose -f "$PROJECT_ROOT/config/docker-compose.production.yml" down
    
    # Restore from backup
    LATEST_BACKUP=$(ls -t "$PROJECT_ROOT/backups/deployment"/*.tar.gz 2>/dev/null | head -1)
    
    if [ -z "$LATEST_BACKUP" ]; then
        log_error "No backup found for rollback"
        return 1
    fi
    
    log "Restoring from backup: $LATEST_BACKUP"
    tar xzf "$LATEST_BACKUP" -C "$PROJECT_ROOT"
    
    # Start services
    docker-compose -f "$PROJECT_ROOT/config/docker-compose.production.yml" up -d
    
    log_success "Rollback completed"
}

generate_deployment_report() {
    print_header "Generating Deployment Report"
    
    REPORT_FILE="$PROJECT_ROOT/deployment_report_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$REPORT_FILE" << EOF
================================================================================
JobSpy Deployment Report
================================================================================
Deployment Date: $(date)
Environment: $DEPLOYMENT_ENV
Docker Registry: $DOCKER_REGISTRY

Backend Image: $BACKEND_IMAGE:latest
Frontend Image: $FRONTEND_IMAGE:latest

Services Status:
$(docker-compose -f "$PROJECT_ROOT/config/docker-compose.production.yml" ps)

Docker Images:
$(docker images | grep jobspy)

Deployment Log: $LOG_FILE

================================================================================
EOF
    
    log_success "Deployment report generated: $REPORT_FILE"
}

main() {
    print_header "JobSpy Production Deployment"
    
    log "Starting deployment process..."
    log "Project Root: $PROJECT_ROOT"
    log "Environment: $DEPLOYMENT_ENV"
    
    # Initialize log file
    echo "Deployment started at $(date)" > "$LOG_FILE"
    
    # Run deployment steps
    check_prerequisites
    build_backend
    build_frontend
    push_images
    backup_current_deployment
    stop_services
    start_services
    run_migrations
    health_check
    smoke_tests
    generate_deployment_report
    
    print_header "Deployment Completed Successfully"
    log_success "JobSpy has been deployed to production"
    log "Access the application at: https://yourdomain.com"
    log "API Documentation: https://api.yourdomain.com/docs"
}

# Handle errors
trap 'log_error "Deployment failed"; exit 1' ERR

# Parse command line arguments
case "${1:-deploy}" in
    deploy)
        main
        ;;
    rollback)
        rollback
        ;;
    *)
        echo "Usage: $0 {deploy|rollback}"
        exit 1
        ;;
esac
