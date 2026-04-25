# Monitoring Setup Guide

## Overview

This guide covers setting up comprehensive monitoring for the JobSpy application including error tracking, performance monitoring, uptime monitoring, and logging.

## Error Tracking with Sentry

### Setup Sentry

1. **Create Sentry Account**
   - Visit [sentry.io](https://sentry.io)
   - Sign up for a free account
   - Create a new organization

2. **Create Project**
   - Select "Python" as the platform
   - Name the project "JobSpy Backend"
   - Create the project

3. **Get DSN**
   - Copy the DSN (Data Source Name)
   - Add to `.env.production`:
     ```
     SENTRY_DSN=your_sentry_dsn_url
     SENTRY_ENVIRONMENT=production
     SENTRY_TRACES_SAMPLE_RATE=0.1
     ```

### Configure Sentry in Backend

```python
# Backend/app/core/config.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
            CeleryIntegration(),
        ],
    )
```

### Sentry Features

- **Error Tracking**: Automatically capture and report errors
- **Performance Monitoring**: Track slow transactions
- **Release Tracking**: Monitor errors by release
- **Alerts**: Get notified of critical errors
- **Source Maps**: Map minified code to source

### Sentry Dashboard

1. **Issues**: View all errors and exceptions
2. **Performance**: Monitor transaction performance
3. **Releases**: Track errors by release
4. **Alerts**: Configure alert rules
5. **Integrations**: Connect with Slack, GitHub, etc.

## Performance Monitoring

### Option 1: DataDog

#### Setup DataDog

1. **Create Account**
   - Visit [datadoghq.com](https://datadoghq.com)
   - Sign up for a free trial
   - Create organization

2. **Install Agent**
   ```bash
   # Install DataDog agent
   DD_AGENT_MAJOR_VERSION=7 DD_API_KEY=your_api_key \
   DD_SITE="datadoghq.com" bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_agent.sh)"
   ```

3. **Configure Backend**
   ```python
   # Backend/app/core/config.py
   from ddtrace import patch_all
   
   patch_all()
   ```

4. **Environment Variables**
   ```bash
   DD_API_KEY=your_api_key
   DD_SITE=datadoghq.com
   DD_SERVICE=jobspy-backend
   DD_ENV=production
   DD_VERSION=1.0.0
   ```

#### DataDog Metrics

- **Response Time**: Track API response times
- **Error Rate**: Monitor error percentage
- **Throughput**: Track requests per second
- **Database Performance**: Monitor query performance
- **Resource Usage**: Track CPU, memory, disk

### Option 2: New Relic

#### Setup New Relic

1. **Create Account**
   - Visit [newrelic.com](https://newrelic.com)
   - Sign up for free
   - Create application

2. **Install Agent**
   ```bash
   pip install newrelic
   ```

3. **Configure Backend**
   ```bash
   # Generate config file
   newrelic-admin generate-config your_license_key newrelic.ini
   
   # Run with agent
   NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program gunicorn app.main:app
   ```

4. **Environment Variables**
   ```bash
   NEW_RELIC_LICENSE_KEY=your_license_key
   NEW_RELIC_APP_NAME=JobSpy Backend
   NEW_RELIC_ENVIRONMENT=production
   ```

## Uptime Monitoring

### UptimeRobot Setup

1. **Create Account**
   - Visit [uptimerobot.com](https://uptimerobot.com)
   - Sign up for free account
   - Create organization

2. **Add Monitors**
   - Click "Add New Monitor"
   - Select "HTTP(s)"
   - Enter URL: `https://api.yourdomain.com/health`
   - Set interval: 5 minutes
   - Click "Create Monitor"

3. **Configure Alerts**
   - Go to "Alert Contacts"
   - Add email address
   - Add Slack webhook (optional)
   - Configure notification rules

### Health Check Endpoint

```python
# Backend/app/routers/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
import redis

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint for monitoring"""
    
    health_status = {
        "status": "healthy",
        "database": "unknown",
        "redis": "unknown",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Check database
    try:
        db.execute("SELECT 1")
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Redis
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        health_status["redis"] = "connected"
    except Exception as e:
        health_status["redis"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status
```

## Logging Setup

### Centralized Logging with ELK Stack

#### Setup Elasticsearch

```bash
# Docker Compose service
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
  environment:
    - discovery.type=single-node
    - xpack.security.enabled=false
  ports:
    - "9200:9200"
  volumes:
    - elasticsearch_data:/usr/share/elasticsearch/data
```

#### Setup Kibana

```bash
# Docker Compose service
kibana:
  image: docker.elastic.co/kibana/kibana:8.0.0
  ports:
    - "5601:5601"
  environment:
    - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
  depends_on:
    - elasticsearch
```

#### Setup Logstash

```bash
# Docker Compose service
logstash:
  image: docker.elastic.co/logstash/logstash:8.0.0
  volumes:
    - ./config/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
  ports:
    - "5000:5000"
  depends_on:
    - elasticsearch
```

### Application Logging Configuration

```python
# Backend/app/core/logging.py
import logging
import json
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configure JSON logging for production"""
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Console handler with JSON formatter
    console_handler = logging.StreamHandler()
    json_formatter = jsonlogger.JsonFormatter()
    console_handler.setFormatter(json_formatter)
    logger.addHandler(console_handler)
    
    return logger
```

### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical errors requiring immediate attention

### Log Rotation

```python
# Backend/app/core/logging.py
from logging.handlers import RotatingFileHandler

def setup_file_logging():
    """Setup file logging with rotation"""
    
    handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.addHandler(handler)
```

## Alerting Configuration

### Alert Rules

#### High Error Rate

```
Alert when error rate > 5% for 5 minutes
Severity: High
Notification: Slack, Email
```

#### Slow Response Time

```
Alert when response time > 1000ms for 10 minutes
Severity: Medium
Notification: Slack
```

#### Database Connection Error

```
Alert when database connection fails
Severity: Critical
Notification: Slack, Email, PagerDuty
```

#### High Memory Usage

```
Alert when memory usage > 80% for 5 minutes
Severity: Medium
Notification: Slack
```

### Slack Integration

#### Setup Slack Webhook

1. Go to Slack App Directory
2. Search for "Incoming Webhooks"
3. Click "Add to Slack"
4. Select channel
5. Copy webhook URL

#### Configure Alerts

```python
# Backend/app/core/alerts.py
import requests

def send_slack_alert(message: str, severity: str = "warning"):
    """Send alert to Slack"""
    
    webhook_url = settings.SLACK_WEBHOOK_URL
    
    color_map = {
        "critical": "#FF0000",
        "high": "#FF6600",
        "medium": "#FFCC00",
        "low": "#00CC00"
    }
    
    payload = {
        "attachments": [
            {
                "color": color_map.get(severity, "#808080"),
                "title": f"JobSpy Alert - {severity.upper()}",
                "text": message,
                "ts": int(time.time())
            }
        ]
    }
    
    requests.post(webhook_url, json=payload)
```

### Email Alerts

```python
# Backend/app/core/alerts.py
from app.services.email_service import send_email

def send_email_alert(subject: str, message: str, recipients: List[str]):
    """Send alert via email"""
    
    send_email(
        subject=subject,
        body=message,
        recipients=recipients,
        template="alert"
    )
```

## Monitoring Dashboard

### Key Metrics to Monitor

1. **Application Metrics**
   - Request rate
   - Response time
   - Error rate
   - Active users

2. **System Metrics**
   - CPU usage
   - Memory usage
   - Disk usage
   - Network I/O

3. **Database Metrics**
   - Query performance
   - Connection pool usage
   - Slow queries
   - Replication lag

4. **Cache Metrics**
   - Hit rate
   - Miss rate
   - Memory usage
   - Eviction rate

### Creating Custom Dashboards

#### Grafana Setup

```bash
# Docker Compose service
grafana:
  image: grafana/grafana:latest
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
  volumes:
    - grafana_data:/var/lib/grafana
```

#### Dashboard Panels

1. **Request Rate**: Requests per second
2. **Response Time**: P50, P95, P99 latencies
3. **Error Rate**: Percentage of failed requests
4. **Active Users**: Concurrent users
5. **Database Performance**: Query times
6. **Cache Hit Rate**: Cache effectiveness

## Monitoring Best Practices

1. **Set Appropriate Thresholds**
   - Don't alert on every spike
   - Use baseline metrics
   - Adjust based on experience

2. **Reduce Alert Fatigue**
   - Combine related alerts
   - Use alert aggregation
   - Implement alert deduplication

3. **Document Runbooks**
   - Create runbooks for each alert
   - Document troubleshooting steps
   - Keep runbooks updated

4. **Regular Review**
   - Review alerts weekly
   - Adjust thresholds based on data
   - Remove obsolete alerts

5. **Test Alerts**
   - Test alert notifications
   - Verify escalation paths
   - Document alert procedures

## Monitoring Checklist

- [ ] Sentry configured for error tracking
- [ ] Performance monitoring setup (DataDog or New Relic)
- [ ] Uptime monitoring configured
- [ ] Health check endpoint implemented
- [ ] Centralized logging setup
- [ ] Alert rules configured
- [ ] Slack integration enabled
- [ ] Email alerts configured
- [ ] Monitoring dashboard created
- [ ] Runbooks documented
- [ ] Team trained on monitoring tools
- [ ] On-call rotation established

## Resources

- [Sentry Documentation](https://docs.sentry.io/)
- [DataDog Documentation](https://docs.datadoghq.com/)
- [New Relic Documentation](https://docs.newrelic.com/)
- [ELK Stack Documentation](https://www.elastic.co/guide/index.html)
- [Grafana Documentation](https://grafana.com/docs/)
