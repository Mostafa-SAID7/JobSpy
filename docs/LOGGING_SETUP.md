# Logging Setup Guide

## Overview

This guide covers setting up comprehensive logging for the JobSpy application including centralized logging, log rotation, and debug vs production logging levels.

## Logging Architecture

### Log Flow

```
Application
    ↓
Log Handler
    ↓
Formatter
    ↓
┌─────────────────────────────────────┐
│  Console (stdout)                   │
│  File (rotating)                    │
│  Syslog                             │
│  Centralized (ELK, CloudWatch)      │
└─────────────────────────────────────┘
```

## Application Logging Configuration

### Python Logging Setup

```python
# Backend/app/core/logging.py
import logging
import logging.config
from pythonjsonlogger import jsonlogger
from app.core.config import settings

def setup_logging():
    """Configure application logging"""
    
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL_CONSOLE,
                "formatter": "json" if settings.ENVIRONMENT == "production" else "standard",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": settings.LOG_LEVEL_FILE,
                "formatter": "json",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "json",
                "filename": "logs/error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10
            }
        },
        "loggers": {
            "": {
                "handlers": ["console", "file", "error_file"],
                "level": settings.LOG_LEVEL,
                "propagate": True
            },
            "app": {
                "handlers": ["console", "file", "error_file"],
                "level": settings.LOG_LEVEL,
                "propagate": False
            },
            "sqlalchemy": {
                "handlers": ["file"],
                "level": "WARNING",
                "propagate": False
            },
            "celery": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False
            }
        }
    }
    
    logging.config.dictConfig(logging_config)
    return logging.getLogger(__name__)
```

### Environment Configuration

```bash
# .env.production
LOG_LEVEL=info
LOG_LEVEL_CONSOLE=info
LOG_LEVEL_FILE=debug
LOG_FORMAT=json
LOG_OUTPUT=stdout
```

## Log Levels

### Development Environment

```python
# Development logging levels
LOG_LEVEL=debug
LOG_LEVEL_CONSOLE=debug
LOG_LEVEL_FILE=debug
```

**Includes:**
- DEBUG: Detailed debugging information
- INFO: General informational messages
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical errors

### Production Environment

```python
# Production logging levels
LOG_LEVEL=info
LOG_LEVEL_CONSOLE=info
LOG_LEVEL_FILE=debug
```

**Includes:**
- INFO: General informational messages
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical errors

**Excludes:**
- DEBUG: Detailed debugging information (only in file)

## Structured Logging

### JSON Logging Format

```python
# Backend/app/core/logging.py
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, logger):
        self.logger = logger
    
    def log_event(self, event_type: str, **kwargs):
        """Log structured event"""
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "environment": settings.ENVIRONMENT,
            "version": settings.APP_VERSION,
            **kwargs
        }
        
        self.logger.info(json.dumps(log_entry))
    
    def log_request(self, method: str, path: str, status_code: int, duration_ms: float):
        """Log HTTP request"""
        
        self.log_event(
            "http_request",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms
        )
    
    def log_database_query(self, query: str, duration_ms: float, rows_affected: int):
        """Log database query"""
        
        self.log_event(
            "database_query",
            query=query,
            duration_ms=duration_ms,
            rows_affected=rows_affected
        )
    
    def log_error(self, error_type: str, message: str, traceback: str):
        """Log error"""
        
        self.log_event(
            "error",
            error_type=error_type,
            message=message,
            traceback=traceback
        )
```

### Example Log Entries

```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "event_type": "http_request",
  "environment": "production",
  "version": "1.0.0",
  "method": "GET",
  "path": "/api/v1/jobs",
  "status_code": 200,
  "duration_ms": 125
}
```

```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "event_type": "database_query",
  "environment": "production",
  "version": "1.0.0",
  "query": "SELECT * FROM jobs WHERE id = ?",
  "duration_ms": 45,
  "rows_affected": 1
}
```

## Log Rotation

### File Rotation Configuration

```python
# Backend/app/core/logging.py
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

# Size-based rotation
size_handler = RotatingFileHandler(
    filename="logs/app.log",
    maxBytes=10485760,  # 10MB
    backupCount=10
)

# Time-based rotation
time_handler = TimedRotatingFileHandler(
    filename="logs/app.log",
    when="midnight",
    interval=1,
    backupCount=30
)
```

### Rotation Policies

**Development:**
- Size: 10MB
- Backup Count: 5
- Retention: 7 days

**Production:**
- Size: 100MB
- Backup Count: 30
- Retention: 90 days

### Cleanup Script

```bash
#!/bin/bash
# scripts/cleanup_logs.sh

LOG_DIR="logs"
RETENTION_DAYS=90

# Remove old log files
find $LOG_DIR -name "*.log.*" -mtime +$RETENTION_DAYS -delete

# Compress old logs
find $LOG_DIR -name "*.log.*" -mtime +7 -exec gzip {} \;

# Archive to S3
aws s3 sync $LOG_DIR s3://jobspy-logs/archive/
```

## Centralized Logging

### ELK Stack Setup

#### Elasticsearch Configuration

```yaml
# config/elasticsearch.yml
cluster.name: jobspy-cluster
node.name: node-1
discovery.type: single-node
xpack.security.enabled: false

# Performance tuning
indices.memory.index_buffer_size: 30%
thread_pool.write.queue_size: 1000
```

#### Logstash Configuration

```conf
# config/logstash.conf
input {
  tcp {
    port => 5000
    codec => json
  }
  
  file {
    path => "/var/log/jobspy/app.log"
    start_position => "beginning"
    codec => json
  }
}

filter {
  if [type] == "app" {
    mutate {
      add_field => { "[@metadata][index_name]" => "jobspy-app-%{+YYYY.MM.dd}" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "%{[@metadata][index_name]}"
  }
}
```

#### Kibana Configuration

```yaml
# config/kibana.yml
server.port: 5601
elasticsearch.hosts: ["http://elasticsearch:9200"]
kibana.defaultAppId: "discover"
```

### Docker Compose Setup

```yaml
# config/docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:8.0.0
    volumes:
      - ./config/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5000:5000"
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.0.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  elasticsearch_data:
```

### AWS CloudWatch Logging

```python
# Backend/app/core/logging.py
import watchtower

def setup_cloudwatch_logging():
    """Setup CloudWatch logging"""
    
    cloudwatch_handler = watchtower.CloudWatchLogHandler(
        log_group="jobspy-app",
        stream_name="backend",
        boto3_session=boto3.Session(
            region_name=settings.AWS_REGION
        )
    )
    
    logger = logging.getLogger()
    logger.addHandler(cloudwatch_handler)
```

## Log Analysis

### Kibana Queries

#### Find Errors

```
level: "ERROR"
```

#### Find Slow Requests

```
event_type: "http_request" AND duration_ms > 1000
```

#### Find Database Errors

```
event_type: "database_query" AND error: *
```

#### Find Specific User Activity

```
user_id: "12345"
```

### Log Dashboards

#### Application Health Dashboard

```
- Request Rate (requests/sec)
- Error Rate (%)
- Response Time (P50, P95, P99)
- Active Users
- Database Query Time
```

#### Performance Dashboard

```
- CPU Usage
- Memory Usage
- Disk I/O
- Network I/O
- Database Connections
```

#### Error Dashboard

```
- Error Count by Type
- Error Rate Over Time
- Top Errors
- Error Trends
```

## Log Retention Policies

### Development Environment

```
Console Logs: Real-time
File Logs: 7 days
Centralized: 30 days
```

### Production Environment

```
Console Logs: Real-time
File Logs: 90 days
Centralized: 1 year
Archive: S3 (indefinite)
```

### Compliance Requirements

```
PII Data: Masked in logs
Sensitive Data: Encrypted
Audit Logs: 7 years retention
```

## Debug Logging

### Enable Debug Logging

```python
# Development only
if settings.ENVIRONMENT == "development":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger("sqlalchemy").setLevel(logging.DEBUG)
    logging.getLogger("celery").setLevel(logging.DEBUG)
```

### Debug Log Examples

```python
# Database query logging
logger.debug(f"Executing query: {query}")
logger.debug(f"Query parameters: {params}")
logger.debug(f"Query result: {result}")

# API request logging
logger.debug(f"Request: {method} {path}")
logger.debug(f"Request headers: {headers}")
logger.debug(f"Request body: {body}")
logger.debug(f"Response status: {status_code}")
logger.debug(f"Response body: {response}")

# Cache logging
logger.debug(f"Cache hit: {key}")
logger.debug(f"Cache miss: {key}")
logger.debug(f"Cache set: {key} = {value}")
```

## Performance Considerations

### Log Performance Impact

- **Synchronous Logging**: Blocks application
- **Asynchronous Logging**: Non-blocking
- **Batch Logging**: Reduces I/O

### Optimization Strategies

```python
# Use async handlers
async_handler = logging.handlers.QueueHandler(
    queue=queue.Queue()
)

# Batch logs
batch_handler = BatchingHandler(
    batch_size=100,
    flush_interval=5
)

# Sample logs
if random.random() < 0.1:  # Log 10% of requests
    logger.info("Request logged")
```

## Logging Best Practices

1. **Use Structured Logging**
   - JSON format for easy parsing
   - Include context information
   - Use consistent field names

2. **Log Appropriate Levels**
   - DEBUG: Detailed information
   - INFO: General information
   - WARNING: Potential issues
   - ERROR: Errors
   - CRITICAL: Critical errors

3. **Include Context**
   - Request ID
   - User ID
   - Session ID
   - Timestamp

4. **Avoid Logging Sensitive Data**
   - Passwords
   - API keys
   - Credit card numbers
   - Personal information

5. **Monitor Log Volume**
   - Track log size
   - Implement rotation
   - Archive old logs
   - Clean up regularly

## Logging Checklist

- [ ] Logging configuration setup
- [ ] Log levels configured
- [ ] Structured logging implemented
- [ ] Log rotation configured
- [ ] Centralized logging setup
- [ ] Kibana dashboards created
- [ ] Log retention policies defined
- [ ] Debug logging enabled for development
- [ ] Sensitive data masked
- [ ] Performance optimized
- [ ] Team trained on logging
- [ ] Monitoring alerts configured

## Resources

- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [ELK Stack Documentation](https://www.elastic.co/guide/index.html)
- [Kibana Documentation](https://www.elastic.co/guide/en/kibana/current/index.html)
- [AWS CloudWatch Logs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/)
