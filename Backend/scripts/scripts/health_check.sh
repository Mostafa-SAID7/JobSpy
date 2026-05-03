#!/bin/bash

# JobSpy Health Check Script
# Monitors application, database, and cache health

set -e

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-jobspy}"
DB_NAME="${DB_NAME:-jobspy}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_PASSWORD="${REDIS_PASSWORD:-}"
ALERT_EMAIL="${ALERT_EMAIL:-}"
LOG_FILE="${LOG_FILE:-.}/health_check.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Health status
OVERALL_STATUS="healthy"
FAILED_CHECKS=()

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

# Check API health
check_api() {
    log "Checking API health..."
    
    local response=$(curl -s -w "\n%{http_code}" "$API_URL/health" 2>/dev/null || echo "000")
    local http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" = "200" ]; then
        log_success "API is healthy (HTTP $http_code)"
        return 0
    else
        log_error "API health check failed (HTTP $http_code)"
        OVERALL_STATUS="unhealthy"
        FAILED_CHECKS+=("API")
        return 1
    fi
}

# Check API response time
check_api_response_time() {
    log "Checking API response time..."
    
    local response_time=$(curl -s -w "%{time_total}" -o /dev/null "$API_URL/health" 2>/dev/null || echo "999")
    local threshold=2  # 2 seconds
    
    if (( $(echo "$response_time < $threshold" | bc -l) )); then
        log_success "API response time is good: ${response_time}s"
        return 0
    else
        log_warning "API response time is slow: ${response_time}s (threshold: ${threshold}s)"
        return 1
    fi
}

# Check database connectivity
check_database() {
    log "Checking database connectivity..."
    
    if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        -c "SELECT 1" > /dev/null 2>&1; then
        log_success "Database is accessible"
        return 0
    else
        log_error "Database connection failed"
        OVERALL_STATUS="unhealthy"
        FAILED_CHECKS+=("Database")
        return 1
    fi
}

# Check database size
check_database_size() {
    log "Checking database size..."
    
    local db_size=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        -t -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'))" 2>/dev/null || echo "unknown")
    
    log "Database size: $db_size"
    return 0
}

# Check database connections
check_database_connections() {
    log "Checking database connections..."
    
    local connections=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        -t -c "SELECT count(*) FROM pg_stat_activity" 2>/dev/null || echo "0")
    
    local max_connections=100
    
    if [ "$connections" -lt "$max_connections" ]; then
        log_success "Database connections: $connections/$max_connections"
        return 0
    else
        log_warning "Database connections high: $connections/$max_connections"
        return 1
    fi
}

# Check Redis connectivity
check_redis() {
    log "Checking Redis connectivity..."
    
    if [ -n "$REDIS_PASSWORD" ]; then
        local response=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" PING 2>/dev/null || echo "FAILED")
    else
        local response=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" PING 2>/dev/null || echo "FAILED")
    fi
    
    if [ "$response" = "PONG" ]; then
        log_success "Redis is accessible"
        return 0
    else
        log_error "Redis connection failed"
        OVERALL_STATUS="unhealthy"
        FAILED_CHECKS+=("Redis")
        return 1
    fi
}

# Check Redis memory usage
check_redis_memory() {
    log "Checking Redis memory usage..."
    
    if [ -n "$REDIS_PASSWORD" ]; then
        local memory=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" INFO memory 2>/dev/null | grep used_memory_human | cut -d: -f2)
    else
        local memory=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" INFO memory 2>/dev/null | grep used_memory_human | cut -d: -f2)
    fi
    
    log "Redis memory usage: $memory"
    return 0
}

# Check disk space
check_disk_space() {
    log "Checking disk space..."
    
    local disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    local threshold=80
    
    if [ "$disk_usage" -lt "$threshold" ]; then
        log_success "Disk usage: ${disk_usage}% (threshold: ${threshold}%)"
        return 0
    else
        log_warning "Disk usage high: ${disk_usage}% (threshold: ${threshold}%)"
        OVERALL_STATUS="degraded"
        return 1
    fi
}

# Check memory usage
check_memory_usage() {
    log "Checking memory usage..."
    
    local memory_usage=$(free | awk 'NR==2 {printf("%.0f", $3/$2 * 100)}')
    local threshold=80
    
    if [ "$memory_usage" -lt "$threshold" ]; then
        log_success "Memory usage: ${memory_usage}% (threshold: ${threshold}%)"
        return 0
    else
        log_warning "Memory usage high: ${memory_usage}% (threshold: ${threshold}%)"
        OVERALL_STATUS="degraded"
        return 1
    fi
}

# Check CPU usage
check_cpu_usage() {
    log "Checking CPU usage..."
    
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{printf("%.0f", 100 - $1)}')
    local threshold=80
    
    if [ "$cpu_usage" -lt "$threshold" ]; then
        log_success "CPU usage: ${cpu_usage}% (threshold: ${threshold}%)"
        return 0
    else
        log_warning "CPU usage high: ${cpu_usage}% (threshold: ${threshold}%)"
        OVERALL_STATUS="degraded"
        return 1
    fi
}

# Send alert email
send_alert() {
    if [ -z "$ALERT_EMAIL" ]; then
        return
    fi
    
    local subject="JobSpy Health Check Alert - Status: $OVERALL_STATUS"
    local body="Health check completed at $(date)\n\nStatus: $OVERALL_STATUS\n\nFailed Checks:\n"
    
    for check in "${FAILED_CHECKS[@]}"; do
        body="$body  - $check\n"
    done
    
    echo -e "$body" | mail -s "$subject" "$ALERT_EMAIL"
}

# Generate health report
generate_report() {
    local report_file="health_check_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "JobSpy Health Check Report"
        echo "Generated: $(date)"
        echo ""
        echo "Overall Status: $OVERALL_STATUS"
        echo ""
        echo "Checks Performed:"
        echo "  - API Health"
        echo "  - API Response Time"
        echo "  - Database Connectivity"
        echo "  - Database Size"
        echo "  - Database Connections"
        echo "  - Redis Connectivity"
        echo "  - Redis Memory Usage"
        echo "  - Disk Space"
        echo "  - Memory Usage"
        echo "  - CPU Usage"
        echo ""
        
        if [ ${#FAILED_CHECKS[@]} -gt 0 ]; then
            echo "Failed Checks:"
            for check in "${FAILED_CHECKS[@]}"; do
                echo "  - $check"
            done
        else
            echo "All checks passed!"
        fi
    } > "$report_file"
    
    log "Report generated: $report_file"
}

# Main execution
main() {
    log "=========================================="
    log "JobSpy Health Check"
    log "=========================================="
    
    # Run all checks
    check_api
    check_api_response_time
    check_database
    check_database_size
    check_database_connections
    check_redis
    check_redis_memory
    check_disk_space
    check_memory_usage
    check_cpu_usage
    
    # Generate report
    generate_report
    
    # Send alert if needed
    if [ "$OVERALL_STATUS" != "healthy" ]; then
        send_alert
    fi
    
    log "=========================================="
    log "Overall Status: $OVERALL_STATUS"
    log "=========================================="
    
    # Exit with appropriate code
    if [ "$OVERALL_STATUS" = "healthy" ]; then
        exit 0
    else
        exit 1
    fi
}

# Run main function
main "$@"
