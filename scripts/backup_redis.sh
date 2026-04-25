#!/bin/bash

# JobSpy Redis Backup Script
# Performs RDB and AOF backups of Redis cache

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-.}/backups"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_PASSWORD="${REDIS_PASSWORD:-}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
S3_BUCKET="${S3_BUCKET:-}"
S3_PREFIX="${S3_PREFIX:-jobspy-redis-backups}"
LOG_FILE="${BACKUP_DIR}/redis_backup.log"

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

# Build redis-cli command with authentication
redis_cli() {
    if [ -n "$REDIS_PASSWORD" ]; then
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" "$@"
    else
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" "$@"
    fi
}

# RDB backup function
rdb_backup() {
    local backup_file="$BACKUP_DIR/redis_rdb_$(date +%Y%m%d_%H%M%S).rdb"
    
    log "Starting RDB backup..."
    
    # Trigger BGSAVE
    if redis_cli BGSAVE > /dev/null 2>&1; then
        log "BGSAVE triggered, waiting for completion..."
        
        # Wait for save to complete
        local max_wait=300  # 5 minutes
        local elapsed=0
        
        while [ $elapsed -lt $max_wait ]; do
            local save_status=$(redis_cli LASTSAVE)
            sleep 2
            elapsed=$((elapsed + 2))
            
            # Check if save is complete
            if redis_cli BGSAVE 2>&1 | grep -q "Background save already in progress"; then
                continue
            else
                break
            fi
        done
        
        # Copy RDB file
        if redis_cli CONFIG GET dir | tail -1 | xargs -I {} cp {}/dump.rdb "$backup_file"; then
            local size=$(du -h "$backup_file" | cut -f1)
            log_success "RDB backup completed: $backup_file ($size)"
            
            # Upload to S3 if configured
            if [ -n "$S3_BUCKET" ]; then
                upload_to_s3 "$backup_file"
            fi
            
            echo "$backup_file"
        else
            log_error "Failed to copy RDB file"
            return 1
        fi
    else
        log_error "BGSAVE command failed"
        return 1
    fi
}

# AOF backup function
aof_backup() {
    local backup_file="$BACKUP_DIR/redis_aof_$(date +%Y%m%d_%H%M%S).aof"
    
    log "Starting AOF backup..."
    
    # Trigger BGREWRITEAOF
    if redis_cli BGREWRITEAOF > /dev/null 2>&1; then
        log "BGREWRITEAOF triggered, waiting for completion..."
        
        # Wait for rewrite to complete
        local max_wait=300  # 5 minutes
        local elapsed=0
        
        while [ $elapsed -lt $max_wait ]; do
            sleep 2
            elapsed=$((elapsed + 2))
            
            # Check if rewrite is complete
            if redis_cli INFO persistence | grep -q "aof_rewrite_in_progress:0"; then
                break
            fi
        done
        
        # Copy AOF file
        if redis_cli CONFIG GET dir | tail -1 | xargs -I {} cp {}/appendonly.aof "$backup_file"; then
            local size=$(du -h "$backup_file" | cut -f1)
            log_success "AOF backup completed: $backup_file ($size)"
            
            # Upload to S3 if configured
            if [ -n "$S3_BUCKET" ]; then
                upload_to_s3 "$backup_file"
            fi
            
            echo "$backup_file"
        else
            log_error "Failed to copy AOF file"
            return 1
        fi
    else
        log_error "BGREWRITEAOF command failed"
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
    
    find "$BACKUP_DIR" -name "redis_*.rdb" -o -name "redis_*.aof" | while read -r file; do
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
    
    # Check file exists and is readable
    if [ -f "$backup_file" ] && [ -r "$backup_file" ]; then
        # For RDB files, check magic number
        if [[ "$backup_file" == *.rdb ]]; then
            local magic=$(head -c 5 "$backup_file")
            if [ "$magic" = "REDIS" ]; then
                log_success "RDB backup integrity verified"
                return 0
            else
                log_error "Invalid RDB file format"
                return 1
            fi
        fi
        
        # For AOF files, check if valid
        if [[ "$backup_file" == *.aof ]]; then
            log_success "AOF backup integrity verified"
            return 0
        fi
    else
        log_error "Backup file not found or not readable: $backup_file"
        return 1
    fi
}

# Get Redis statistics
get_redis_stats() {
    log "Redis Statistics:"
    
    local info=$(redis_cli INFO)
    
    echo "$info" | grep -E "used_memory|connected_clients|total_commands_processed|keyspace" | while read -r line; do
        log "  $line"
    done
}

# Generate backup report
generate_report() {
    local report_file="$BACKUP_DIR/redis_backup_report_$(date +%Y%m%d).txt"
    
    log "Generating backup report: $report_file"
    
    {
        echo "JobSpy Redis Backup Report"
        echo "Generated: $(date)"
        echo ""
        echo "Configuration:"
        echo "  Redis Host: $REDIS_HOST:$REDIS_PORT"
        echo "  Backup Directory: $BACKUP_DIR"
        echo "  Retention: $RETENTION_DAYS days"
        echo ""
        echo "Recent Backups:"
        ls -lh "$BACKUP_DIR"/redis_*.{rdb,aof} 2>/dev/null | tail -10 || echo "  No backups found"
        echo ""
        echo "Redis Statistics:"
        redis_cli INFO | grep -E "used_memory|connected_clients|total_commands_processed|keyspace" || echo "  Unable to retrieve"
        echo ""
        echo "Backup Statistics:"
        echo "  Total RDB backups: $(find "$BACKUP_DIR" -name "redis_*.rdb" | wc -l)"
        echo "  Total AOF backups: $(find "$BACKUP_DIR" -name "redis_*.aof" | wc -l)"
        echo "  Total size: $(du -sh "$BACKUP_DIR" | cut -f1)"
    } > "$report_file"
    
    log_success "Report generated: $report_file"
}

# Main execution
main() {
    log "=========================================="
    log "JobSpy Redis Backup Script"
    log "=========================================="
    
    # Check Redis connectivity
    if ! redis_cli PING > /dev/null 2>&1; then
        log_error "Cannot connect to Redis at $REDIS_HOST:$REDIS_PORT"
        exit 1
    fi
    
    # Parse arguments
    case "${1:-full}" in
        rdb)
            rdb_backup
            ;;
        aof)
            aof_backup
            ;;
        full)
            rdb_backup
            aof_backup
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
        stats)
            get_redis_stats
            ;;
        report)
            generate_report
            ;;
        *)
            echo "Usage: $0 {rdb|aof|full|cleanup|verify|stats|report}"
            echo ""
            echo "Commands:"
            echo "  rdb               - Perform RDB backup"
            echo "  aof               - Perform AOF backup"
            echo "  full              - Perform both RDB and AOF backups"
            echo "  cleanup           - Remove old backups"
            echo "  verify <file>     - Verify backup integrity"
            echo "  stats             - Display Redis statistics"
            echo "  report            - Generate backup report"
            exit 1
            ;;
    esac
    
    log "=========================================="
}

# Run main function
main "$@"
