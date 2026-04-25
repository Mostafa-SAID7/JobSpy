#!/bin/bash

# JobSpy Log Cleanup Script
# Manages log rotation, compression, and archival

set -e

# Configuration
LOG_DIR="${LOG_DIR:-.}/logs"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
ARCHIVE_DIR="${ARCHIVE_DIR:-.}/log_archives"
COMPRESS_AFTER_DAYS="${COMPRESS_AFTER_DAYS:-7}"
S3_BUCKET="${S3_BUCKET:-}"
S3_PREFIX="${S3_PREFIX:-jobspy-logs}"
LOG_FILE="${LOG_DIR}/cleanup.log"

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

# Create directories
mkdir -p "$LOG_DIR" "$ARCHIVE_DIR"

# Rotate logs
rotate_logs() {
    log "Rotating logs..."
    
    local rotated_count=0
    
    # Find all log files
    find "$LOG_DIR" -name "*.log" -type f | while read -r logfile; do
        if [ -f "$logfile" ]; then
            local rotated_file="${logfile}.$(date +%Y%m%d_%H%M%S)"
            
            # Rotate the log file
            if mv "$logfile" "$rotated_file"; then
                log "Rotated: $logfile -> $rotated_file"
                rotated_count=$((rotated_count + 1))
                
                # Create new empty log file
                touch "$logfile"
                chmod 644 "$logfile"
            fi
        fi
    done
    
    log_success "Rotated $rotated_count log files"
}

# Compress old logs
compress_logs() {
    log "Compressing logs older than $COMPRESS_AFTER_DAYS days..."
    
    local compressed_count=0
    
    find "$LOG_DIR" -name "*.log.*" -type f | while read -r logfile; do
        if [ -f "$logfile" ]; then
            local file_age=$(($(date +%s) - $(stat -f%m "$logfile" 2>/dev/null || stat -c%Y "$logfile")))
            local file_age_days=$((file_age / 86400))
            
            if [ "$file_age_days" -gt "$COMPRESS_AFTER_DAYS" ] && [ ! -f "${logfile}.gz" ]; then
                if gzip "$logfile"; then
                    log "Compressed: $logfile"
                    compressed_count=$((compressed_count + 1))
                fi
            fi
        fi
    done
    
    log_success "Compressed $compressed_count log files"
}

# Archive logs
archive_logs() {
    log "Archiving logs..."
    
    local archived_count=0
    
    find "$LOG_DIR" -name "*.log.*.gz" -type f | while read -r logfile; do
        if [ -f "$logfile" ]; then
            local filename=$(basename "$logfile")
            local archive_file="$ARCHIVE_DIR/$filename"
            
            if mv "$logfile" "$archive_file"; then
                log "Archived: $logfile -> $archive_file"
                archived_count=$((archived_count + 1))
            fi
        fi
    done
    
    log_success "Archived $archived_count log files"
}

# Upload to S3
upload_to_s3() {
    if [ -z "$S3_BUCKET" ]; then
        return
    fi
    
    log "Uploading archived logs to S3..."
    
    find "$ARCHIVE_DIR" -name "*.log.*.gz" -type f | while read -r logfile; do
        if [ -f "$logfile" ]; then
            local filename=$(basename "$logfile")
            
            if aws s3 cp "$logfile" "s3://$S3_BUCKET/$S3_PREFIX/$filename" \
                --storage-class GLACIER \
                --sse AES256; then
                log "Uploaded to S3: $filename"
            else
                log_error "Failed to upload to S3: $filename"
            fi
        fi
    done
    
    log_success "S3 upload completed"
}

# Cleanup old logs
cleanup_old_logs() {
    log "Cleaning up logs older than $RETENTION_DAYS days..."
    
    local deleted_count=0
    local freed_space=0
    
    find "$LOG_DIR" -name "*.log.*" -type f | while read -r logfile; do
        if [ -f "$logfile" ]; then
            local file_age=$(($(date +%s) - $(stat -f%m "$logfile" 2>/dev/null || stat -c%Y "$logfile")))
            local file_age_days=$((file_age / 86400))
            
            if [ "$file_age_days" -gt "$RETENTION_DAYS" ]; then
                local file_size=$(du -h "$logfile" | cut -f1)
                
                if rm -f "$logfile"; then
                    log "Deleted: $logfile ($file_size)"
                    deleted_count=$((deleted_count + 1))
                fi
            fi
        fi
    done
    
    find "$ARCHIVE_DIR" -name "*.log.*.gz" -type f | while read -r logfile; do
        if [ -f "$logfile" ]; then
            local file_age=$(($(date +%s) - $(stat -f%m "$logfile" 2>/dev/null || stat -c%Y "$logfile")))
            local file_age_days=$((file_age / 86400))
            
            if [ "$file_age_days" -gt "$RETENTION_DAYS" ]; then
                local file_size=$(du -h "$logfile" | cut -f1)
                
                if rm -f "$logfile"; then
                    log "Deleted: $logfile ($file_size)"
                    deleted_count=$((deleted_count + 1))
                fi
            fi
        fi
    done
    
    log_success "Deleted $deleted_count old log files"
}

# Generate cleanup report
generate_report() {
    local report_file="$LOG_DIR/cleanup_report_$(date +%Y%m%d).txt"
    
    log "Generating cleanup report: $report_file"
    
    {
        echo "JobSpy Log Cleanup Report"
        echo "Generated: $(date)"
        echo ""
        echo "Configuration:"
        echo "  Log Directory: $LOG_DIR"
        echo "  Archive Directory: $ARCHIVE_DIR"
        echo "  Retention: $RETENTION_DAYS days"
        echo "  Compress After: $COMPRESS_AFTER_DAYS days"
        echo ""
        echo "Log Statistics:"
        echo "  Total log files: $(find "$LOG_DIR" -name "*.log*" -type f | wc -l)"
        echo "  Total archived files: $(find "$ARCHIVE_DIR" -name "*.log*" -type f | wc -l)"
        echo "  Log directory size: $(du -sh "$LOG_DIR" | cut -f1)"
        echo "  Archive directory size: $(du -sh "$ARCHIVE_DIR" | cut -f1)"
        echo ""
        echo "Recent Log Files:"
        ls -lh "$LOG_DIR"/*.log 2>/dev/null | tail -10 || echo "  No log files found"
        echo ""
        echo "Recent Archived Files:"
        ls -lh "$ARCHIVE_DIR"/*.gz 2>/dev/null | tail -10 || echo "  No archived files found"
    } > "$report_file"
    
    log_success "Report generated: $report_file"
}

# Main execution
main() {
    log "=========================================="
    log "JobSpy Log Cleanup Script"
    log "=========================================="
    
    # Parse arguments
    case "${1:-full}" in
        rotate)
            rotate_logs
            ;;
        compress)
            compress_logs
            ;;
        archive)
            archive_logs
            ;;
        upload)
            upload_to_s3
            ;;
        cleanup)
            cleanup_old_logs
            ;;
        full)
            rotate_logs
            compress_logs
            archive_logs
            upload_to_s3
            cleanup_old_logs
            ;;
        report)
            generate_report
            ;;
        *)
            echo "Usage: $0 {rotate|compress|archive|upload|cleanup|full|report}"
            echo ""
            echo "Commands:"
            echo "  rotate              - Rotate log files"
            echo "  compress            - Compress old log files"
            echo "  archive             - Archive compressed logs"
            echo "  upload              - Upload archived logs to S3"
            echo "  cleanup             - Delete old log files"
            echo "  full                - Perform all operations"
            echo "  report              - Generate cleanup report"
            exit 1
            ;;
    esac
    
    # Generate report
    generate_report
    
    log "=========================================="
}

# Run main function
main "$@"
