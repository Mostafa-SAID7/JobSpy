# Production Setup Guide

## Overview

This guide provides step-by-step instructions for deploying the JobSpy Web Application to a production environment. The deployment uses Docker containers orchestrated with docker-compose, with support for multiple hosting platforms.

## Prerequisites

- Docker and Docker Compose installed
- Domain name configured
- SSL/TLS certificate (Let's Encrypt recommended)
- PostgreSQL database (managed or self-hosted)
- Redis instance (managed or self-hosted)
- SMTP service for email notifications (SendGrid, AWS SES, etc.)
- Monitoring service account (Sentry, DataDog, New Relic)

## Hosting Platform Selection

### Option 1: Render (Recommended for Beginners)

**Pros:**
- Simple deployment from GitHub
- Automatic SSL certificates
- Built-in PostgreSQL and Redis
- Free tier available
- Good documentation

**Cons:**
- Limited customization
- Potential vendor lock-in
- Pricing increases with scale

**Setup:**
1. Create account at render.com
2. Connect GitHub repository
3. Create PostgreSQL database
4. Create Redis instance
5. Deploy backend service
6. Deploy frontend service

### Option 2: Railway

**Pros:**
- Simple deployment
- Good pricing
- GitHub integration
- Environment variables management

**Cons:**
- Smaller community
- Limited advanced features

**Setup:**
1. Create account at railway.app
2. Connect GitHub repository
3. Create PostgreSQL database
4. Create Redis instance
5. Deploy services

### Option 3: AWS (Recommended for Scale)

**Pros:**
- Highly scalable
- Many service options
- Pay-as-you-go pricing
- Global infrastructure

**Cons:**
- Complex setup
- Steeper learning curve
- Requires AWS knowledge

**Setup:**
1. Create AWS account
2. Setup RDS for PostgreSQL
3. Setup ElastiCache for Redis
4. Setup ECS for container orchestration
5. Setup ALB for load balancing
6. Setup CloudFront for CDN
7. Setup Route53 for DNS

## Environment Configuration

### Production Environment Variables

Create `.env.production` file with the following variables:

```bash
# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# Database
DATABASE_URL=postgresql://user:password@host:5432/jobspy_prod
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Redis
REDIS_URL=redis://host:6379/0
REDIS_PASSWORD=your_secure_password

# Security
SECRET_KEY=your_very_secure_secret_key_min_32_chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]
CORS_ALLOW_CREDENTIALS=true

# Email
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your_sendgrid_api_key
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=JobSpy

# Celery
CELERY_BROKER_URL=redis://host:6379/1
CELERY_RESULT_BACKEND=redis://host:6379/2

# Monitoring
SENTRY_DSN=your_sentry_dsn
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1

# AWS (if using S3)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=jobspy-exports
AWS_REGION=us-east-1

# Frontend
VITE_API_URL=https://api.yourdomain.com
VITE_APP_NAME=JobSpy
```

## Database Setup

### PostgreSQL Configuration

```bash
# Connect to PostgreSQL
psql -h your-host -U postgres

# Create database
CREATE DATABASE jobspy_prod;

# Create user
CREATE USER jobspy_user WITH PASSWORD 'secure_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE jobspy_prod TO jobspy_user;

# Connect to database
\c jobspy_prod

# Grant schema privileges
GRANT ALL ON SCHEMA public TO jobspy_user;
```

### Run Migrations

```bash
# From backend directory
alembic upgrade head
```

### Create Indexes

```sql
-- Performance indexes
CREATE INDEX idx_jobs_site_name ON jobs(site_name);
CREATE INDEX idx_jobs_posted_date ON jobs(posted_date DESC);
CREATE INDEX idx_saved_jobs_user_id ON saved_jobs(user_id);
CREATE INDEX idx_alerts_user_id ON alerts(user_id);
CREATE INDEX idx_alerts_is_active ON alerts(is_active);
```

## Redis Configuration

### Redis Setup

```bash
# Connect to Redis
redis-cli -h your-host -p 6379

# Set password (if not already set)
CONFIG SET requirepass your_secure_password

# Verify connection
PING

# Check memory usage
INFO memory

# Set max memory policy
CONFIG SET maxmemory-policy allkeys-lru
```

### Redis Persistence

```bash
# Enable RDB snapshots
CONFIG SET save "900 1 300 10 60 10000"

# Enable AOF
CONFIG SET appendonly yes
CONFIG SET appendfsync everysec
```

## SSL/TLS Certificate Setup

### Using Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Certificate Renewal

```bash
# Manual renewal
sudo certbot renew

# Check renewal status
sudo certbot renew --dry-run
```

## Docker Deployment

### Build Docker Images

```bash
# Build backend image
docker build -f Backend/Dockerfile -t jobspy-backend:latest ./Backend

# Build frontend image
docker build -f Frontend/Dockerfile -t jobspy-frontend:latest ./Frontend

# Tag for registry
docker tag jobspy-backend:latest your-registry/jobspy-backend:latest
docker tag jobspy-frontend:latest your-registry/jobspy-frontend:latest

# Push to registry
docker push your-registry/jobspy-backend:latest
docker push your-registry/jobspy-frontend:latest
```

### Deploy with Docker Compose

```bash
# Pull latest images
docker-compose pull

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Health Checks

### Backend Health Check

```bash
curl https://api.yourdomain.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Frontend Health Check

```bash
curl https://yourdomain.com/
```

Expected: HTML response with status 200

## Monitoring and Logging

### Application Monitoring

1. **Sentry Setup**
   - Create Sentry project
   - Add DSN to environment variables
   - Monitor errors and performance

2. **Performance Monitoring**
   - Setup DataDog or New Relic
   - Monitor response times
   - Track resource usage

3. **Uptime Monitoring**
   - Setup UptimeRobot or similar
   - Monitor health endpoints
   - Alert on downtime

### Log Aggregation

```bash
# View application logs
docker-compose logs backend

# Export logs
docker-compose logs backend > backend.log

# Real-time log streaming
docker-compose logs -f backend
```

## Backup and Recovery

### Database Backups

```bash
# Create backup
pg_dump -h your-host -U jobspy_user jobspy_prod > backup.sql

# Restore from backup
psql -h your-host -U jobspy_user jobspy_prod < backup.sql

# Automated daily backup
0 2 * * * pg_dump -h your-host -U jobspy_user jobspy_prod | gzip > /backups/jobspy_$(date +\%Y\%m\%d).sql.gz
```

### Redis Backups

```bash
# Create backup
redis-cli -h your-host BGSAVE

# Copy dump file
cp /var/lib/redis/dump.rdb /backups/redis_$(date +%Y%m%d).rdb
```

## Scaling Considerations

### Horizontal Scaling

1. **Load Balancing**
   - Use nginx or cloud load balancer
   - Route traffic to multiple backend instances
   - Session affinity for WebSocket connections

2. **Database Scaling**
   - Read replicas for read-heavy operations
   - Connection pooling (PgBouncer)
   - Sharding for very large datasets

3. **Cache Scaling**
   - Redis cluster for high availability
   - Cache replication
   - Sentinel for automatic failover

### Vertical Scaling

1. **Increase Resources**
   - More CPU cores
   - More RAM
   - Faster storage

2. **Optimize Code**
   - Profile and optimize hot paths
   - Reduce database queries
   - Implement caching

## Security Hardening

### Network Security

```bash
# Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Restrict database access
# Only allow from application servers
```

### Application Security

1. **HTTPS Enforcement**
   - Redirect HTTP to HTTPS
   - Set HSTS headers
   - Use secure cookies

2. **Rate Limiting**
   - Implement rate limiting on API endpoints
   - Use Redis for distributed rate limiting
   - Alert on suspicious patterns

3. **Input Validation**
   - Validate all user inputs
   - Sanitize database queries
   - Prevent SQL injection

## Troubleshooting

### Common Issues

**Issue: Database connection timeout**
```bash
# Check database connectivity
psql -h your-host -U jobspy_user -d jobspy_prod -c "SELECT 1"

# Check connection pool
# Increase DATABASE_POOL_SIZE in environment
```

**Issue: Redis connection refused**
```bash
# Check Redis status
redis-cli -h your-host ping

# Check Redis password
redis-cli -h your-host -a your_password ping
```

**Issue: High memory usage**
```bash
# Check memory usage
docker stats

# Reduce cache TTL
# Implement cache eviction policies
# Scale horizontally
```

**Issue: Slow API responses**
```bash
# Check database query performance
# Enable query logging
# Add indexes to frequently queried columns
# Implement caching
```

## Maintenance Tasks

### Daily Tasks

- Monitor error logs
- Check system resources
- Verify backups completed

### Weekly Tasks

- Review performance metrics
- Check for security updates
- Test backup restoration

### Monthly Tasks

- Update dependencies
- Review and optimize queries
- Capacity planning

## Rollback Procedure

### Quick Rollback

```bash
# Stop current deployment
docker-compose down

# Restore previous version
docker-compose up -d

# Verify health
curl https://api.yourdomain.com/health
```

### Database Rollback

```bash
# Restore from backup
psql -h your-host -U jobspy_user jobspy_prod < backup.sql

# Verify data integrity
psql -h your-host -U jobspy_user -d jobspy_prod -c "SELECT COUNT(*) FROM jobs"
```

## Support and Resources

- Documentation: https://docs.yourdomain.com
- API Reference: https://api.yourdomain.com/docs
- Status Page: https://status.yourdomain.com
- Support Email: support@yourdomain.com
