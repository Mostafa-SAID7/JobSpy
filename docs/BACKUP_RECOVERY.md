# Backup and Recovery Procedures

## Overview

This document outlines comprehensive backup and recovery procedures for the JobSpy Web Application, including database, cache, and file backups.

## Backup Strategy

### Backup Types

1. **Full Backups**: Complete database snapshot (daily)
2. **Incremental Backups**: Changes since last backup (hourly)
3. **Transaction Logs**: Point-in-time recovery (continuous)
4. **File Backups**: Application files and configurations (weekly)

### Backup Schedule

```
Daily:     02:00 UTC - Full database backup
Hourly:    Every hour - Incremental backup
Continuous: Transaction logs
Weekly:    Sunday 03:00 UTC - Full file backup
```

## Database Backups

### PostgreSQL Full Backup

```bash
#!/bin/bash
# backup_database.sh

BACKUP_DIR="/backups/database"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/jobspy_full_$TIMESTAMP.sql.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
pg_dump \
  -h $DB_HOST \
  -U $DB_USER \
  -d $DB_NAME \
  --verbose \
  --no-password \
  | gzip > $BACKUP_FILE

# Verify backup
if [ -f $BACKUP_FILE ]; then
  echo "Backup created: $BACKUP_FILE"
  
  # Upload to S3
  aws s3 cp $BACKUP_FILE s3://jobspy-backups/database/
  
  # Keep only last 30 days
  find $BACKUP_DIR -name "jobspy_full_*.sql.gz" -mtime +30 -delete
else
  echo "Backup failed!"
  exit 1
fi
```

### PostgreSQL Incremental Backup

```bash
#!/bin/bash
# backup_incremental.sh

BACKUP_DIR="/backups/database"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/jobspy_incremental_$TIMESTAMP.sql.gz"

# Create incremental backup (using WAL)
pg_basebackup \
  -h $DB_HOST \
  -U $DB_USER \
  -D $BACKUP_DIR/base_backup \
  -Ft \
  -z \
  -P

# Compress and upload
tar czf $BACKUP_FILE $BACKUP_DIR/base_backup
aws s3 cp $BACKUP_FILE s3://jobspy-backups/database/
```

### PostgreSQL Point-in-Time Recovery

```bash
#!/bin/bash
# restore_to_point_in_time.sh

RECOVERY_TIME="2024-01-01 12:00:00"
BACKUP_DIR="/backups/database"

# Stop PostgreSQL
sudo systemctl stop postgresql

# Restore from base backup
pg_basebackup \
  -h $DB_HOST \
  -U $DB_USER \
  -D /var/lib/postgresql/data \
  -Ft \
  -z

# Create recovery configuration
cat > /var/lib/postgresql/data/recovery.conf << EOF
restore_command = 'cp /backups/wal_archive/%f %p'
recovery_target_time = '$RECOVERY_TIME'
recovery_target_timeline = 'latest'
EOF

# Start PostgreSQL
sudo systemctl start postgresql

# Monitor recovery
tail -f /var/log/postgresql/postgresql.log
```

### Automated Daily Backup Script

```bash
#!/bin/bash
# daily_backup.sh

set -e

BACKUP_DIR="/backups/database"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/var/log/jobspy_backup.log"

log_message() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> $LOG_FILE
}

log_message "Starting daily backup..."

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
BACKUP_FILE="$BACKUP_DIR/jobspy_full_$TIMESTAMP.sql.gz"
pg_dump \
  -h $DB_HOST \
  -U $DB_USER \
  -d $DB_NAME \
  | gzip > $BACKUP_FILE

if [ -f $BACKUP_FILE ]; then
  log_message "Database backup created: $BACKUP_FILE"
  
  # Calculate checksum
  CHECKSUM=$(md5sum $BACKUP_FILE | awk '{print $1}')
  log_message "Checksum: $CHECKSUM"
  
  # Upload to S3
  aws s3 cp $BACKUP_FILE s3://jobspy-backups/database/
  log_message "Backup uploaded to S3"
  
  # Cleanup old backups (keep 30 days)
  find $BACKUP_DIR -name "jobspy_full_*.sql.gz" -mtime +30 -delete
  log_message "Old backups cleaned up"
else
  log_message "ERROR: Database backup failed!"
  exit 1
fi

log_message "Daily backup completed successfully"
```

## Redis Backups

### Redis RDB Backup

```bash
#!/bin/bash
# backup_redis.sh

BACKUP_DIR="/backups/redis"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/redis_$TIMESTAMP.rdb"

mkdir -p $BACKUP_DIR

# Trigger RDB save
redis-cli -h $REDIS_HOST -a $REDIS_PASSWORD BGSAVE

# Wait for save to complete
while [ $(redis-cli -h $REDIS_HOST -a $REDIS_PASSWORD LASTSAVE) -eq $(redis-cli -h $REDIS_HOST -a $REDIS_PASSWORD LASTSAVE) ]; do
  sleep 1
done

# Copy dump file
cp /var/lib/redis/dump.rdb $BACKUP_FILE

# Upload to S3
aws s3 cp $BACKUP_FILE s3://jobspy-backups/redis/

# Cleanup old backups
find $BACKUP_DIR -name "redis_*.rdb" -mtime +7 -delete
```

### Redis AOF Backup

```bash
#!/bin/bash
# backup_redis_aof.sh

BACKUP_DIR="/backups/redis"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/redis_aof_$TIMESTAMP.aof"

mkdir -p $BACKUP_DIR

# Trigger AOF rewrite
redis-cli -h $REDIS_HOST -a $REDIS_PASSWORD BGREWRITEAOF

# Wait for rewrite to complete
while [ $(redis-cli -h $REDIS_HOST -a $REDIS_PASSWORD LASTSAVE) -eq $(redis-cli -h $REDIS_HOST -a $REDIS_PASSWORD LASTSAVE) ]; do
  sleep 1
done

# Copy AOF file
cp /var/lib/redis/appendonly.aof $BACKUP_FILE

# Upload to S3
aws s3 cp $BACKUP_FILE s3://jobspy-backups/redis/
```

## File Backups

### Application Files Backup

```bash
#!/bin/bash
# backup_files.sh

BACKUP_DIR="/backups/files"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/jobspy_files_$TIMESTAMP.tar.gz"

mkdir -p $BACKUP_DIR

# Backup application files
tar czf $BACKUP_FILE \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='__pycache__' \
  --exclude='.env' \
  /opt/jobspy/

# Upload to S3
aws s3 cp $BACKUP_FILE s3://jobspy-backups/files/

# Cleanup old backups
find $BACKUP_DIR -name "jobspy_files_*.tar.gz" -mtime +30 -delete
```

## Recovery Procedures

### Database Recovery from Full Backup

```bash
#!/bin/bash
# restore_database.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup_file>"
  exit 1
fi

# Stop application
docker-compose down

# Drop existing database
psql -h $DB_HOST -U postgres -c "DROP DATABASE IF EXISTS jobspy_prod;"

# Create new database
psql -h $DB_HOST -U postgres -c "CREATE DATABASE jobspy_prod OWNER jobspy_user;"

# Restore from backup
gunzip -c $BACKUP_FILE | psql -h $DB_HOST -U jobspy_user -d jobspy_prod

# Verify restoration
psql -h $DB_HOST -U jobspy_user -d jobspy_prod -c "SELECT COUNT(*) FROM jobs;"

# Start application
docker-compose up -d

# Verify health
sleep 10
curl http://localhost:8000/health
```

### Database Recovery to Point-in-Time

```bash
#!/bin/bash
# restore_to_time.sh

RECOVERY_TIME=$1

if [ -z "$RECOVERY_TIME" ]; then
  echo "Usage: $0 'YYYY-MM-DD HH:MM:SS'"
  exit 1
fi

# Stop application
docker-compose down

# Stop PostgreSQL
sudo systemctl stop postgresql

# Create recovery configuration
cat > /var/lib/postgresql/data/recovery.conf << EOF
restore_command = 'cp /backups/wal_archive/%f %p'
recovery_target_time = '$RECOVERY_TIME'
recovery_target_timeline = 'latest'
EOF

# Start PostgreSQL
sudo systemctl start postgresql

# Monitor recovery
tail -f /var/log/postgresql/postgresql.log

# Once recovery is complete, start application
docker-compose up -d
```

### Redis Recovery

```bash
#!/bin/bash
# restore_redis.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup_file>"
  exit 1
fi

# Stop Redis
redis-cli -h $REDIS_HOST -a $REDIS_PASSWORD SHUTDOWN

# Restore dump file
cp $BACKUP_FILE /var/lib/redis/dump.rdb

# Start Redis
redis-server /etc/redis/redis.conf

# Verify restoration
redis-cli -h $REDIS_HOST -a $REDIS_PASSWORD DBSIZE
```

## Backup Verification

### Backup Integrity Check

```bash
#!/bin/bash
# verify_backup.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup_file>"
  exit 1
fi

# Check file size
SIZE=$(du -h $BACKUP_FILE | cut -f1)
echo "Backup size: $SIZE"

# Check if gzip file is valid
if gzip -t $BACKUP_FILE 2>/dev/null; then
  echo "✓ Backup file is valid"
else
  echo "✗ Backup file is corrupted"
  exit 1
fi

# Test restore to temporary database
TEMP_DB="jobspy_test_$(date +%s)"
psql -h $DB_HOST -U postgres -c "CREATE DATABASE $TEMP_DB;"
gunzip -c $BACKUP_FILE | psql -h $DB_HOST -U jobspy_user -d $TEMP_DB

# Verify data
JOBS_COUNT=$(psql -h $DB_HOST -U jobspy_user -d $TEMP_DB -t -c "SELECT COUNT(*) FROM jobs;")
USERS_COUNT=$(psql -h $DB_HOST -U jobspy_user -d $TEMP_DB -t -c "SELECT COUNT(*) FROM users;")

echo "Jobs in backup: $JOBS_COUNT"
echo "Users in backup: $USERS_COUNT"

# Cleanup
psql -h $DB_HOST -U postgres -c "DROP DATABASE $TEMP_DB;"

echo "✓ Backup verification completed"
```

## Disaster Recovery Plan

### Recovery Time Objectives (RTO)

- **Critical Data Loss**: 1 hour
- **Database Corruption**: 4 hours
- **Complete System Failure**: 8 hours

### Recovery Point Objectives (RPO)

- **Database**: 1 hour (hourly backups)
- **Redis Cache**: 24 hours (daily backups)
- **Application Files**: 7 days (weekly backups)

### Disaster Recovery Steps

1. **Assess Damage**
   - Identify what was lost
   - Determine recovery point needed
   - Notify stakeholders

2. **Prepare Recovery Environment**
   - Provision new infrastructure
   - Configure networking
   - Setup security groups

3. **Restore Data**
   - Restore database from backup
   - Restore Redis cache
   - Restore application files

4. **Verify Recovery**
   - Run health checks
   - Verify data integrity
   - Test critical functions

5. **Resume Operations**
   - Switch traffic to recovered system
   - Monitor for issues
   - Document recovery process

## Backup Monitoring

### Backup Status Dashboard

```bash
#!/bin/bash
# backup_status.sh

echo "=== Backup Status Report ==="
echo ""

# Database backups
echo "Database Backups:"
ls -lh /backups/database/jobspy_full_*.sql.gz | tail -5

echo ""
echo "Latest backup:"
LATEST=$(ls -t /backups/database/jobspy_full_*.sql.gz | head -1)
echo "File: $LATEST"
echo "Size: $(du -h $LATEST | cut -f1)"
echo "Age: $(find $LATEST -type f -printf '%T@ %Tc\n' | cut -d' ' -f2-)"

echo ""
echo "Redis Backups:"
ls -lh /backups/redis/redis_*.rdb | tail -5

echo ""
echo "File Backups:"
ls -lh /backups/files/jobspy_files_*.tar.gz | tail -5
```

### Backup Alerts

```bash
#!/bin/bash
# check_backup_health.sh

ALERT_EMAIL="admin@yourdomain.com"
BACKUP_DIR="/backups/database"

# Check if backup exists
LATEST_BACKUP=$(ls -t $BACKUP_DIR/jobspy_full_*.sql.gz 2>/dev/null | head -1)

if [ -z "$LATEST_BACKUP" ]; then
  echo "ALERT: No backup found!" | mail -s "Backup Alert" $ALERT_EMAIL
  exit 1
fi

# Check backup age
BACKUP_AGE=$(($(date +%s) - $(stat -f%m $LATEST_BACKUP)))
MAX_AGE=$((25 * 3600))  # 25 hours

if [ $BACKUP_AGE -gt $MAX_AGE ]; then
  echo "ALERT: Backup is older than 25 hours!" | mail -s "Backup Alert" $ALERT_EMAIL
  exit 1
fi

# Check backup size
BACKUP_SIZE=$(du -b $LATEST_BACKUP | cut -f1)
MIN_SIZE=$((100 * 1024 * 1024))  # 100 MB

if [ $BACKUP_SIZE -lt $MIN_SIZE ]; then
  echo "ALERT: Backup size is suspiciously small!" | mail -s "Backup Alert" $ALERT_EMAIL
  exit 1
fi

echo "✓ Backup health check passed"
```

## Cron Jobs Setup

### Add to Crontab

```bash
# Edit crontab
crontab -e

# Add backup jobs
0 2 * * * /scripts/daily_backup.sh
0 * * * * /scripts/backup_incremental.sh
0 3 * * 0 /scripts/backup_files.sh
0 4 * * * /scripts/check_backup_health.sh
```

## S3 Backup Configuration

### AWS S3 Setup

```bash
# Create S3 bucket
aws s3 mb s3://jobspy-backups

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket jobspy-backups \
  --versioning-configuration Status=Enabled

# Set lifecycle policy
aws s3api put-bucket-lifecycle-configuration \
  --bucket jobspy-backups \
  --lifecycle-configuration file://lifecycle.json
```

### Lifecycle Policy (lifecycle.json)

```json
{
  "Rules": [
    {
      "Id": "DeleteOldBackups",
      "Status": "Enabled",
      "Prefix": "database/",
      "Expiration": {
        "Days": 90
      },
      "NoncurrentVersionExpiration": {
        "NoncurrentDays": 30
      }
    },
    {
      "Id": "TransitionToGlacier",
      "Status": "Enabled",
      "Prefix": "database/",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "GLACIER"
        }
      ]
    }
  ]
}
```

## Testing Recovery

### Monthly Recovery Test

```bash
#!/bin/bash
# test_recovery.sh

echo "Starting monthly recovery test..."

# Select random backup
BACKUP=$(ls -t /backups/database/jobspy_full_*.sql.gz | shuf | head -1)

echo "Testing recovery from: $BACKUP"

# Create test database
TEST_DB="jobspy_recovery_test_$(date +%s)"
psql -h $DB_HOST -U postgres -c "CREATE DATABASE $TEST_DB;"

# Restore backup
gunzip -c $BACKUP | psql -h $DB_HOST -U jobspy_user -d $TEST_DB

# Run verification queries
echo "Verifying data integrity..."
psql -h $DB_HOST -U jobspy_user -d $TEST_DB << EOF
SELECT COUNT(*) as jobs_count FROM jobs;
SELECT COUNT(*) as users_count FROM users;
SELECT COUNT(*) as saved_jobs_count FROM saved_jobs;
SELECT COUNT(*) as alerts_count FROM alerts;
EOF

# Cleanup
psql -h $DB_HOST -U postgres -c "DROP DATABASE $TEST_DB;"

echo "✓ Recovery test completed successfully"
```

## Documentation

- Keep backup procedures documented
- Update recovery procedures when infrastructure changes
- Test recovery procedures monthly
- Document all backup locations and credentials securely
