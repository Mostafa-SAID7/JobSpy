# Alerting Setup Guide

## Overview

This guide covers setting up comprehensive alerting for the JobSpy application including alert rules, notification channels, and escalation policies.

## Alert Rules and Thresholds

### Critical Alerts

#### 1. Database Connection Failure

**Condition**: Database connection fails

**Threshold**: Immediate

**Severity**: Critical

**Notification**: Slack, Email, PagerDuty

**Runbook**: 
1. Check database service status
2. Verify network connectivity
3. Check database credentials
4. Review database logs
5. Restart database if necessary

```yaml
alert: DatabaseConnectionFailure
expr: up{job="postgres"} == 0
for: 1m
annotations:
  summary: "Database connection failed"
  description: "PostgreSQL database is not responding"
```

#### 2. Application Crash

**Condition**: Application process exits unexpectedly

**Threshold**: Immediate

**Severity**: Critical

**Notification**: Slack, Email, PagerDuty

**Runbook**:
1. Check application logs
2. Review recent deployments
3. Check system resources
4. Restart application
5. Investigate root cause

```yaml
alert: ApplicationCrash
expr: rate(process_resident_memory_bytes[5m]) == 0
for: 1m
annotations:
  summary: "Application crashed"
  description: "JobSpy backend application is not running"
```

#### 3. High Error Rate

**Condition**: Error rate exceeds 5%

**Threshold**: 5% for 5 minutes

**Severity**: High

**Notification**: Slack, Email

**Runbook**:
1. Check error logs in Sentry
2. Identify error pattern
3. Check recent code changes
4. Review database performance
5. Rollback if necessary

```yaml
alert: HighErrorRate
expr: (rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])) > 0.05
for: 5m
annotations:
  summary: "High error rate detected"
  description: "Error rate is {{ $value | humanizePercentage }}"
```

#### 4. High Response Time

**Condition**: P95 response time exceeds 1000ms

**Threshold**: 1000ms for 10 minutes

**Severity**: High

**Notification**: Slack

**Runbook**:
1. Check database query performance
2. Review slow query logs
3. Check cache hit rate
4. Monitor CPU and memory usage
5. Scale resources if necessary

```yaml
alert: HighResponseTime
expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
for: 10m
annotations:
  summary: "High response time detected"
  description: "P95 response time is {{ $value }}s"
```

### High Priority Alerts

#### 5. High Memory Usage

**Condition**: Memory usage exceeds 80%

**Threshold**: 80% for 5 minutes

**Severity**: High

**Notification**: Slack

**Runbook**:
1. Check memory usage by process
2. Identify memory leaks
3. Review application logs
4. Restart services if necessary
5. Scale resources

```yaml
alert: HighMemoryUsage
expr: (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) < 0.2
for: 5m
annotations:
  summary: "High memory usage detected"
  description: "Memory usage is {{ $value | humanizePercentage }}"
```

#### 6. High CPU Usage

**Condition**: CPU usage exceeds 80%

**Threshold**: 80% for 10 minutes

**Severity**: High

**Notification**: Slack

**Runbook**:
1. Check CPU usage by process
2. Identify resource-intensive queries
3. Review application performance
4. Scale resources if necessary

```yaml
alert: HighCPUUsage
expr: (100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)) > 80
for: 10m
annotations:
  summary: "High CPU usage detected"
  description: "CPU usage is {{ $value }}%"
```

#### 7. Disk Space Low

**Condition**: Disk usage exceeds 85%

**Threshold**: 85% for 5 minutes

**Severity**: High

**Notification**: Slack, Email

**Runbook**:
1. Check disk usage by directory
2. Identify large files
3. Clean up old logs
4. Archive old data
5. Expand disk if necessary

```yaml
alert: DiskSpaceLow
expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.15
for: 5m
annotations:
  summary: "Disk space low"
  description: "Disk usage is {{ $value | humanizePercentage }}"
```

#### 8. Redis Connection Failure

**Condition**: Redis connection fails

**Threshold**: Immediate

**Severity**: High

**Notification**: Slack, Email

**Runbook**:
1. Check Redis service status
2. Verify network connectivity
3. Check Redis credentials
4. Review Redis logs
5. Restart Redis if necessary

```yaml
alert: RedisConnectionFailure
expr: up{job="redis"} == 0
for: 1m
annotations:
  summary: "Redis connection failed"
  description: "Redis cache is not responding"
```

### Medium Priority Alerts

#### 9. Slow Database Queries

**Condition**: Slow queries detected

**Threshold**: Query time > 1000ms

**Severity**: Medium

**Notification**: Slack

**Runbook**:
1. Check slow query logs
2. Analyze query execution plan
3. Add indexes if necessary
4. Optimize query
5. Monitor performance

```yaml
alert: SlowDatabaseQueries
expr: rate(pg_slow_queries_total[5m]) > 0
for: 5m
annotations:
  summary: "Slow database queries detected"
  description: "{{ $value }} slow queries per second"
```

#### 10. Cache Hit Rate Low

**Condition**: Cache hit rate below 70%

**Threshold**: 70% for 10 minutes

**Severity**: Medium

**Notification**: Slack

**Runbook**:
1. Check cache configuration
2. Review cache TTL settings
3. Analyze cache usage patterns
4. Increase cache size if necessary
5. Optimize cache keys

```yaml
alert: LowCacheHitRate
expr: (rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m]))) < 0.7
for: 10m
annotations:
  summary: "Low cache hit rate"
  description: "Cache hit rate is {{ $value | humanizePercentage }}"
```

#### 11. High Queue Depth

**Condition**: Celery queue has many pending tasks

**Threshold**: > 1000 tasks for 5 minutes

**Severity**: Medium

**Notification**: Slack

**Runbook**:
1. Check Celery worker status
2. Increase worker concurrency
3. Scale workers horizontally
4. Optimize task processing
5. Monitor queue depth

```yaml
alert: HighQueueDepth
expr: celery_queue_length > 1000
for: 5m
annotations:
  summary: "High Celery queue depth"
  description: "Queue has {{ $value }} pending tasks"
```

### Low Priority Alerts

#### 12. Certificate Expiration

**Condition**: SSL certificate expires soon

**Threshold**: 30 days before expiration

**Severity**: Low

**Notification**: Email

**Runbook**:
1. Renew SSL certificate
2. Update certificate in load balancer
3. Verify certificate installation
4. Test HTTPS connectivity

```yaml
alert: CertificateExpiringSoon
expr: ssl_certificate_expiry_seconds < 2592000
for: 1h
annotations:
  summary: "SSL certificate expiring soon"
  description: "Certificate expires in {{ $value | humanizeDuration }}"
```

#### 13. Backup Failure

**Condition**: Backup job fails

**Threshold**: Immediate

**Severity**: Low

**Notification**: Email

**Runbook**:
1. Check backup logs
2. Verify backup storage
3. Check disk space
4. Retry backup manually
5. Investigate root cause

```yaml
alert: BackupFailure
expr: rate(backup_failures_total[1h]) > 0
for: 1h
annotations:
  summary: "Backup job failed"
  description: "{{ $value }} backup failures in the last hour"
```

## Notification Channels

### Slack Integration

#### Setup Slack Webhook

1. Go to Slack Workspace Settings
2. Navigate to "Manage Apps"
3. Search for "Incoming Webhooks"
4. Click "Add to Slack"
5. Select channel for notifications
6. Copy webhook URL

#### Configure Alerts

```python
# Backend/app/core/alerts.py
import requests
from typing import Dict, List

class SlackNotifier:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_alert(self, alert: Dict):
        """Send alert to Slack"""
        
        severity_colors = {
            "critical": "#FF0000",
            "high": "#FF6600",
            "medium": "#FFCC00",
            "low": "#00CC00"
        }
        
        payload = {
            "attachments": [
                {
                    "color": severity_colors.get(alert["severity"], "#808080"),
                    "title": alert["title"],
                    "text": alert["description"],
                    "fields": [
                        {
                            "title": "Severity",
                            "value": alert["severity"].upper(),
                            "short": True
                        },
                        {
                            "title": "Time",
                            "value": alert["timestamp"],
                            "short": True
                        }
                    ],
                    "footer": "JobSpy Monitoring",
                    "ts": int(time.time())
                }
            ]
        }
        
        requests.post(self.webhook_url, json=payload)
```

#### Slack Message Format

```
🚨 CRITICAL: Database Connection Failed
Database connection failed for 1 minute
Severity: CRITICAL
Time: 2024-01-01 12:00:00 UTC

Runbook: Check database service status
```

### Email Notifications

#### Configure Email Alerts

```python
# Backend/app/core/alerts.py
from app.services.email_service import send_email

class EmailNotifier:
    def __init__(self, smtp_config: Dict):
        self.smtp_config = smtp_config
    
    def send_alert(self, alert: Dict, recipients: List[str]):
        """Send alert via email"""
        
        subject = f"[{alert['severity'].upper()}] {alert['title']}"
        
        body = f"""
        Alert: {alert['title']}
        Severity: {alert['severity'].upper()}
        Time: {alert['timestamp']}
        
        Description:
        {alert['description']}
        
        Runbook:
        {alert['runbook']}
        
        Please investigate and take appropriate action.
        """
        
        send_email(
            subject=subject,
            body=body,
            recipients=recipients,
            template="alert"
        )
```

### PagerDuty Integration

#### Setup PagerDuty

1. Create PagerDuty account
2. Create service for JobSpy
3. Create integration key
4. Configure escalation policy

#### Configure Alerts

```python
# Backend/app/core/alerts.py
import requests

class PagerDutyNotifier:
    def __init__(self, integration_key: str):
        self.integration_key = integration_key
        self.api_url = "https://events.pagerduty.com/v2/enqueue"
    
    def send_alert(self, alert: Dict):
        """Send alert to PagerDuty"""
        
        severity_map = {
            "critical": "critical",
            "high": "error",
            "medium": "warning",
            "low": "info"
        }
        
        payload = {
            "routing_key": self.integration_key,
            "event_action": "trigger",
            "dedup_key": alert["id"],
            "payload": {
                "summary": alert["title"],
                "severity": severity_map.get(alert["severity"], "error"),
                "source": "JobSpy Monitoring",
                "custom_details": {
                    "description": alert["description"],
                    "runbook": alert["runbook"]
                }
            }
        }
        
        requests.post(self.api_url, json=payload)
```

## Escalation Policies

### On-Call Rotation

```yaml
escalation_policy:
  name: "JobSpy On-Call"
  escalation_rules:
    - level: 1
      delay_minutes: 5
      targets:
        - primary_oncall@yourdomain.com
    
    - level: 2
      delay_minutes: 10
      targets:
        - secondary_oncall@yourdomain.com
    
    - level: 3
      delay_minutes: 15
      targets:
        - manager@yourdomain.com
```

### Alert Routing

```yaml
alert_routing:
  critical:
    channels:
      - slack
      - email
      - pagerduty
    escalation_policy: "JobSpy On-Call"
  
  high:
    channels:
      - slack
      - email
    escalation_policy: "JobSpy On-Call"
  
  medium:
    channels:
      - slack
  
  low:
    channels:
      - email
```

## Alert Management

### Silencing Alerts

```python
# Temporarily silence alerts during maintenance
alert_manager.silence(
    alert_name="HighErrorRate",
    duration_minutes=30,
    reason="Deploying new version"
)
```

### Alert Deduplication

```python
# Prevent duplicate alerts
alert_manager.deduplicate(
    alert_id="HighErrorRate",
    window_minutes=5
)
```

### Alert Aggregation

```python
# Aggregate related alerts
alert_manager.aggregate(
    alerts=["HighCPUUsage", "HighMemoryUsage"],
    group_name="ResourceUtilization"
)
```

## Monitoring Alerting System

### Alert Health Metrics

- Alert delivery rate
- Alert response time
- False positive rate
- Alert resolution time

### Alert Dashboard

```
Total Alerts: 150
Critical: 2
High: 8
Medium: 25
Low: 115

Alert Response Time: 5 minutes (avg)
False Positive Rate: 2%
Resolution Time: 30 minutes (avg)
```

## Best Practices

1. **Avoid Alert Fatigue**
   - Set appropriate thresholds
   - Use alert aggregation
   - Implement alert deduplication

2. **Clear Runbooks**
   - Document troubleshooting steps
   - Include escalation procedures
   - Keep runbooks updated

3. **Regular Review**
   - Review alerts weekly
   - Adjust thresholds based on data
   - Remove obsolete alerts

4. **Test Alerts**
   - Test alert notifications
   - Verify escalation paths
   - Document alert procedures

5. **Incident Response**
   - Document incident procedures
   - Establish on-call rotation
   - Conduct post-mortems

## Alerting Checklist

- [ ] Alert rules configured
- [ ] Thresholds set appropriately
- [ ] Slack integration enabled
- [ ] Email notifications configured
- [ ] PagerDuty integration setup
- [ ] Escalation policies defined
- [ ] On-call rotation established
- [ ] Runbooks documented
- [ ] Alert testing completed
- [ ] Team trained on alerting
- [ ] Alert dashboard created
- [ ] Incident procedures documented

## Resources

- [Prometheus Alerting](https://prometheus.io/docs/alerting/latest/overview/)
- [Grafana Alerting](https://grafana.com/docs/grafana/latest/alerting/)
- [PagerDuty Documentation](https://developer.pagerduty.com/)
- [Slack API Documentation](https://api.slack.com/)
