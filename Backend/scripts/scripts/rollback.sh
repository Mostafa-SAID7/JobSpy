#!/bin/bash

################################################################################
# JobSpy Production Rollback Script
# 
# This script handles rolling back to a previous deployment version
# Supports both application and database rollback
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
LOG_FILE="${PROJECT_ROOT}/rollback.log"
BACKUP_DIR="${PROJECT_ROOT}/backups"
DB_BACKUP_DIR="${BACKUP_DIR}/database"
DEPLOYMENT_BACKUP_DIR="${BACKUP_DIR}/deployment"

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

confirm() {
    local prompt="$1"
    local response
    
    read -p "$(echo -e ${YELLOW}$prompt${NC}) (yes/no): " response
    
    if [ "$response" = "yes" ]; then
        return 0
    else
        return 1
    fi
}

list_backups() {
    print_header "Available Backups"
    
    echo "Deployment Backups:"
    ls -lh "$DEPLOYMENT_BACKUP_DIR"/*.tar.gz 2>/dev/null | tail -10 || echo "No deployment backups found"
    
    echo ""
    echo "Database Backups:"
    ls -lh "$DB_BACKUP_DIR"/*.sql.gz 2>/dev/null | tail -10 || echo "No database backups found"
}

rollback_application() {
    print_header "Rolling Back Application"
    
    # Find latest deployment backup
    LATEST_BACKUP=$(ls -t "$DEPLOYMENT_BACKUP_DIR"/*.tar.gz 2>/dev/null | head -1)
    
    if [ -z "$LATEST_BACKUP" ]; then
        log_error "No deployment backups found"
        return 1
    fi
    
    log "Latest backup: $LATEST_BACKUP"
    log "Backup size: $(du -h $LATEST_BACKUP | cut -f1)"
    log "Backup date: $(stat -f%Sm -t '%Y-%m-%d %H:%M:%S' $LATEST_BACKUP 2>/dev/null || stat -c%y $LATEST_BACKUP)"
    
    if ! confirm "Rollback to this backup?"; then
        log_warning "Rollback cancelled"
        return 1
    fi
    
    # Stop services
    log "Stopping services..."
    cd "$PROJECT_ROOT"
    docker-compose -f config/docker-compose.production.yml down
    
    if [ $? -ne 0 ]; then
        log_error "Failed to stop services"
        return 1
    fi
    log_success "Services stopped"
    
    # Restore from backup
    log "Restoring from backup..."
    tar xzf "$LATEST_BACKUP" -C "$PROJECT_ROOT"
    
    if [ $? -ne 0 ]; then
        log_error "Failed to restore from backup"
        return 1
    fi
    log_success "Backup restored"
    
    # Start services
    log "Starting services..."
    docker-compose -f config/docker-compose.production.yml up -d
    
    if [ $? -ne 0 ]; then
        log_error "Failed to start services"
        return 1
    fi
    log_success "Services started"
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 10
    
    # Health check
    log "Performing health check..."
    HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
    
    if [ "$HEALTH" = "200" ]; then
        log_success "Application rollback completed successfully"
        return 0
    else
        log_error "Health check failed (HTTP $HEALTH)"
        return 1
    fi
}

rollback_database() {
    print_header "Rolling Back Database"
    
    # Find latest database backup
    LATEST_BACKUP=$(ls -t "$DB_BACKUP_DIR"/*.sql.gz 2>/dev/null | head -1)
    
    if [ -z "$LATEST_BACKUP" ]; then
        log_error "No database backups found"
        return 1
    fi
    
    log "Latest backup: $LATEST_BACKUP"
    log "Backup size: $(du -h $LATEST_BACKUP | cut -f1)"
    log "Backup date: $(stat -f%Sm -t '%Y-%m-%d %H:%M:%S' $LATEST_BACKUP 2>/dev/null || stat -c%y $LATEST_BACKUP)"
    
    if ! confirm "Rollback database to this backup?"; then
        log_warning "Database rollback cancelled"
        return 1
    fi
    
    log_warning "This will restore the database to the backup point"
    log_warning "All data changes since the backup will be lost"
    
    if ! confirm "Are you absolutely sure?"; then
        log_warning "Database rollback cancelled"
        return 1
    fi
    
    # Load environment variables
    if [ ! -f "$PROJECT_ROOT/.env.production" ]; then
        log_error ".env.production file not found"
        return 1
    fi
    
    source "$PROJECT_ROOT/.env.production"
    
    # Create backup of current database before restoring
    log "Creating backup of current database..."
    CURRENT_BACKUP="$DB_BACKUP_DIR/pre_rollback_$(date +%Y%m%d_%H%M%S).sql.gz"
    
    pg_dump \
        -h ${DATABASE_HOST:-postgres} \
        -U ${DATABASE_USER:-jobspy_user} \
        -d ${DATABASE_NAME:-jobspy_prod} \
        | gzip > "$CURRENT_BACKUP"
    
    if [ $? -eq 0 ]; then
        log_success "Current database backed up: $CURRENT_BACKUP"
    else
        log_error "Failed to backup current database"
        return 1
    fi
    
    # Drop existing database
    log "Dropping existing database..."
    psql -h ${DATABASE_HOST:-postgres} \
        -U postgres \
        -c "DROP DATABASE IF EXISTS ${DATABASE_NAME:-jobspy_prod};"
    
    if [ $? -ne 0 ]; then
        log_error "Failed to drop database"
        return 1
    fi
    log_success "Database dropped"
    
    # Create new database
    log "Creating new database..."
    psql -h ${DATABASE_HOST:-postgres} \
        -U postgres \
        -c "CREATE DATABASE ${DATABASE_NAME:-jobspy_prod} OWNER ${DATABASE_USER:-jobspy_user};"
    
    if [ $? -ne 0 ]; then
        log_error "Failed to create database"
        return 1
    fi
    log_success "Database created"
    
    # Restore from backup
    log "Restoring database from backup..."
    gunzip -c "$LATEST_BACKUP" | psql -h ${DATABASE_HOST:-postgres} \
        -U ${DATABASE_USER:-jobspy_user} \
        -d ${DATABASE_NAME:-jobspy_prod}
    
    if [ $? -ne 0 ]; then
        log_error "Failed to restore database"
        return 1
    fi
    log_success "Database restored"
    
    # Verify restoration
    log "Verifying database restoration..."
    JOBS_COUNT=$(psql -h ${DATABASE_HOST:-postgres} \
        -U ${DATABASE_USER:-jobspy_user} \
        -d ${DATABASE_NAME:-jobspy_prod} \
        -t -c "SELECT COUNT(*) FROM jobs;")
    
    log "Jobs in restored database: $JOBS_COUNT"
    log_success "Database rollback completed successfully"
}

rollback_to_point_in_time() {
    print_header "Rolling Back Database to Point-in-Time"
    
    log "This feature requires WAL archiving to be enabled"
    
    read -p "Enter recovery time (YYYY-MM-DD HH:MM:SS): " RECOVERY_TIME
    
    if [ -z "$RECOVERY_TIME" ]; then
        log_error "Recovery time not provided"
        return 1
    fi
    
    log "Recovery time: $RECOVERY_TIME"
    
    if ! confirm "Rollback database to this point in time?"; then
        log_warning "Point-in-time recovery cancelled"
        return 1
    fi
    
    # Load environment variables
    if [ ! -f "$PROJECT_ROOT/.env.production" ]; then
        log_error ".env.production file not found"
        return 1
    fi
    
    source "$PROJECT_ROOT/.env.production"
    
    # Stop PostgreSQL
    log "Stopping PostgreSQL..."
    docker-compose -f "$PROJECT_ROOT/config/docker-compose.production.yml" \
        exec -T postgres pg_ctl stop -D /var/lib/postgresql/data
    
    # Create recovery configuration
    log "Creating recovery configuration..."
    docker-compose -f "$PROJECT_ROOT/config/docker-compose.production.yml" \
        exec -T postgres bash -c "cat > /var/lib/postgresql/data/recovery.conf << EOF
restore_command = 'cp /backups/wal_archive/%f %p'
recovery_target_time = '$RECOVERY_TIME'
recovery_target_timeline = 'latest'
EOF"
    
    # Start PostgreSQL
    log "Starting PostgreSQL for recovery..."
    docker-compose -f "$PROJECT_ROOT/config/docker-compose.production.yml" \
        exec -T postgres pg_ctl start -D /var/lib/postgresql/data
    
    # Monitor recovery
    log "Monitoring recovery process..."
    sleep 5
    
    docker-compose -f "$PROJECT_ROOT/config/docker-compose.production.yml" \
        logs postgres | tail -20
    
    log_success "Point-in-time recovery initiated"
    log "Monitor the recovery process with: docker-compose logs postgres"
}

generate_rollback_report() {
    print_header "Generating Rollback Report"
    
    REPORT_FILE="$PROJECT_ROOT/rollback_report_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$REPORT_FILE" << EOF
================================================================================
JobSpy Rollback Report
================================================================================
Rollback Date: $(date)
Rollback Type: $ROLLBACK_TYPE

Services Status:
$(docker-compose -f "$PROJECT_ROOT/config/docker-compose.production.yml" ps 2>/dev/null || echo "Services not running")

Docker Images:
$(docker images | grep jobspy)

Rollback Log: $LOG_FILE

================================================================================
EOF
    
    log_success "Rollback report generated: $REPORT_FILE"
}

main() {
    print_header "JobSpy Production Rollback"
    
    log "Starting rollback process..."
    log "Project Root: $PROJECT_ROOT"
    
    # Initialize log file
    echo "Rollback started at $(date)" > "$LOG_FILE"
    
    # Show available backups
    list_backups
    
    # Ask what to rollback
    echo ""
    echo "What would you like to rollback?"
    echo "1) Application (Docker images and configuration)"
    echo "2) Database (from backup)"
    echo "3) Database (point-in-time recovery)"
    echo "4) Both application and database"
    echo "5) Cancel"
    
    read -p "Enter your choice (1-5): " CHOICE
    
    case $CHOICE in
        1)
            ROLLBACK_TYPE="Application"
            rollback_application
            ;;
        2)
            ROLLBACK_TYPE="Database"
            rollback_database
            ;;
        3)
            ROLLBACK_TYPE="Database (Point-in-Time)"
            rollback_to_point_in_time
            ;;
        4)
            ROLLBACK_TYPE="Application and Database"
            rollback_application && rollback_database
            ;;
        5)
            log_warning "Rollback cancelled"
            exit 0
            ;;
        *)
            log_error "Invalid choice"
            exit 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        generate_rollback_report
        print_header "Rollback Completed Successfully"
        log_success "JobSpy has been rolled back"
    else
        log_error "Rollback failed"
        exit 1
    fi
}

# Handle errors
trap 'log_error "Rollback failed"; exit 1' ERR

main
