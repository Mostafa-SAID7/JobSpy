#!/bin/bash

# JobSpy Database Backup Script
# Performs full and incremental backups of PostgreSQL database

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-.}/backups"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-jobspy}"
DB_NAME="${DB_NAME:-jobspy}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
S3_BUCKET="${S3_BUCKET:-}"
S3_PREFIX="${S3_PREFIX:-jobspy-backups}"
LOG_FILE="${BACKUP_DIR}/backup.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Full backup function
full_backup() {
    local backup_file="$BACKUP_DIR/full_backup_$(date +%Y%m%d_%H%M%S).sql.gz"
    
    log "Starting full database backup..."
    
    if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        --verbose --no-password 2>&1 | gzip > "$backup_file"; then
        
        local size=$(du -h "$backup_file" | cut -f1)
        log_success "Full backup completed: $backup_file ($size)"
        
        # Upload to S3 if configured
        if [ -n "$S3_BUCKET" ]; then
            upload_to_s3 "$backup_file"
        fi
        
        echo "$backup_file"
    else
        log_error "Full backup failed"
        return 1
    fi
}

# Incremental backup function (using WAL archiving)
incremental_backup() {
    local backup_file="$BACKUP_DIR/incremental_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    
    log "Starting incremental backup..."
    
    # Create backup label
    local backup_label="$BACKUP_DIR/backup_label_$(date +%Y%m%d_%H%M%S)"
    
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        -c "SELECT pg_start_backup('incremental_backup');" > "$backup_label"; then
        
        # Backup data directory
        if tar -czf "$backup_file" -C /var/lib/postgresql/data . 2>/dev/null; then
            psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
                -c "SELECT pg_stop_backup();" > /dev/null
            
            local size=$(du -h "$backup_file" | cut -f1)
            log_success "Incremental backup completed: $backup_file ($size)"
            
            # Upload to S3 if configured
            if [ -n "$S3_BUCKET" ]; then
                upload_to_s3 "$backup_file"
            fi
            
            echo "$backup_file"
        else
            log_error "Incremental backup failed"
            return 1
        fi
    else
        log_error "Failed to start backup"
        return 1
    fi
}

# Upload to S3
upload_to_s3() {
    local file="$1"
    local filename=$(basename "$file")
    
    log "Uploading to S3: s3://$S3_BUCKET/$S3_PREFIX/$filename"
    
    if aws s3 cp "$file" "s3://$S3_BUCKET/$S3_PREFIX/$filename" \
        --storage-class STANDARD_IA \
        --sse AES256; then
        log_success "S3 upload completed"
    else
        log_error "S3 upload failed"
        return 1
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days..."
    
    find "$BACKUP_DIR" -name "*.sql.gz" -o -name "*.tar.gz" | while read -r file; do
        if [ -f "$file" ]; then
            local file_age=$(($(date +%s) - $(stat -f%m "$file" 2>/dev/null || stat -c%Y "$file")))
            local file_age_days=$((file_age / 86400))
            
            if [ "$file_age_days" -gt "$RETENTION_DAYS" ]; then
                log "Removing old backup: $file (age: $file_age_days days)"
                rm -f "$file"
            fi
        fi
    done
    
    log_success "Cleanup completed"
}

# Verify backup integrity
verify_backup() {
    local backup_file="$1"
    
    log "Verifying backup integrity: $backup_file"
    
    if gunzip -t "$backup_file" 2>/dev/null; then
        log_success "Backup integrity verified"
        return 0
    else
        log_error "Backup integrity check failed"
        return 1
    fi
}

# Restore from backup
restore_backup() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    log "Restoring from backup: $backup_file"
    
    # Create temporary database
    local temp_db="${DB_NAME}_restore_$(date +%s)"
    
    if createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$temp_db"; then
        if gunzip -c "$backup_file" | psql -h "$DB_HOST" -p "$DB_PORT" \
            -U "$DB_USER" -d "$temp_db" > /dev/null 2>&1; then
            
            log_success "Restore completed to temporary database: $temp_db"
            log "To complete restore, run:"
            log "  dropdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME"
            log "  alterdb -h $DB_HOST -p $DB_PORT -U $DB_USER $temp_db $DB_NAME"
            
            return 0
        else
            log_error "Restore failed"
            dropdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$temp_db"
            return 1
        fi
    else
        log_error "Failed to create temporary database"
        return 1
    fi
}

# Generate backup report
generate_report() {
    local report_file="$BACKUP_DIR/backup_report_$(date +%Y%m%d).txt"
    
    log "Generating backup report: $report_file"
    
    {
        echo "JobSpy Database Backup Report"
        echo "Generated: $(date)"
        echo ""
        echo "Configuration:"
        echo "  Database: $DB_NAME"
        echo "  Host: $DB_HOST:$DB_PORT"
        echo "  Backup Directory: $BACKUP_DIR"
        echo "  Retention: $RETENTION_DAYS days"
        echo ""
        echo "Recent Backups:"
        ls -lh "$BACKUP_DIR"/*.sql.gz 2>/dev/null | tail -10 || echo "  No backups found"
        echo ""
        echo "Database Size:"
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
            -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));" 2>/dev/null || echo "  Unable to determine"
        echo ""
        echo "Backup Statistics:"
        echo "  Total backups: $(find "$BACKUP_DIR" -name "*.sql.gz" -o -name "*.tar.gz" | wc -l)"
        echo "  Total size: $(du -sh "$BACKUP_DIR" | cut -f1)"
    } > "$report_file"
    
    log_success "Report generated: $report_file"
}

# Main execution
main() {
    log "=========================================="
    log "JobSpy Database Backup Script"
    log "=========================================="
    
    # Parse arguments
    case "${1:-full}" in
        full)
            full_backup
            ;;
        incremental)
            incremental_backup
            ;;
        cleanup)
            cleanup_old_backups
            ;;
        verify)
            if [ -z "$2" ]; then
                log_error "Usage: $0 verify <backup_file>"
                exit 1
            fi
            verify_backup "$2"
            ;;
        restore)
            if [ -z "$2" ]; then
                log_error "Usage: $0 restore <backup_file>"
                exit 1
            fi
            restore_backup "$2"
            ;;
        report)
            generate_report
            ;;
        *)
            echo "Usage: $0 {full|incremental|cleanup|verify|restore|report}"
            echo ""
            echo "Commands:"
            echo "  full              - Perform full database backup"
            echo "  incremental       - Perform incremental backup"
            echo "  cleanup           - Remove old backups"
            echo "  verify <file>     - Verify backup integrity"
            echo "  restore <file>    - Restore from backup"
            echo "  report            - Generate backup report"
            exit 1
            ;;
    esac
    
    log "=========================================="
}

# Run main function
main "$@"
