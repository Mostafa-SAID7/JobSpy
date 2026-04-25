# JobSpy Database Schema

## Overview

JobSpy uses PostgreSQL as the primary data store. This document describes the database schema, tables, relationships, and design decisions.

## Database Design Principles

1. **Normalization**: Data is normalized to reduce redundancy
2. **Referential Integrity**: Foreign keys enforce relationships
3. **Performance**: Indexes optimize query performance
4. **Scalability**: Design supports growth and partitioning
5. **Auditability**: Timestamps track data changes

## Tables

### Users Table

Stores user account information.

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  profile_photo_url VARCHAR(500),
  bio TEXT,
  location VARCHAR(255),
  experience_level VARCHAR(50),
  preferred_job_types TEXT[],
  preferred_locations TEXT[],
  salary_min INTEGER,
  salary_max INTEGER,
  is_active BOOLEAN DEFAULT TRUE,
  email_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login_at TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
```

**Columns**:
- `id`: Unique user identifier (UUID)
- `email`: User email address (unique)
- `password_hash`: Hashed password
- `full_name`: User's full name
- `profile_photo_url`: URL to profile photo
- `bio`: User biography
- `location`: User's location
- `experience_level`: Career level (entry, mid, senior, executive)
- `preferred_job_types`: Array of preferred job types
- `preferred_locations`: Array of preferred locations
- `salary_min`: Minimum salary expectation
- `salary_max`: Maximum salary expectation
- `is_active`: Account status
- `email_verified`: Email verification status
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp
- `last_login_at`: Last login timestamp

### Jobs Table

Stores job listings.

```sql
CREATE TABLE jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255) NOT NULL,
  company VARCHAR(255) NOT NULL,
  location VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  requirements TEXT[],
  benefits TEXT[],
  salary_min INTEGER,
  salary_max INTEGER,
  job_type VARCHAR(50),
  experience_level VARCHAR(50),
  industry VARCHAR(100),
  source_id UUID NOT NULL REFERENCES job_sources(id),
  external_url VARCHAR(500) NOT NULL,
  external_id VARCHAR(255) UNIQUE,
  posted_date TIMESTAMP NOT NULL,
  scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_jobs_title ON jobs(title);
CREATE INDEX idx_jobs_company ON jobs(company);
CREATE INDEX idx_jobs_location ON jobs(location);
CREATE INDEX idx_jobs_posted_date ON jobs(posted_date DESC);
CREATE INDEX idx_jobs_source_id ON jobs(source_id);
CREATE INDEX idx_jobs_external_id ON jobs(external_id);
CREATE INDEX idx_jobs_created_at ON jobs(created_at DESC);
```

**Columns**:
- `id`: Unique job identifier (UUID)
- `title`: Job title
- `company`: Company name
- `location`: Job location
- `description`: Full job description
- `requirements`: Array of job requirements
- `benefits`: Array of job benefits
- `salary_min`: Minimum salary
- `salary_max`: Maximum salary
- `job_type`: Job type (full-time, part-time, contract, freelance)
- `experience_level`: Required experience level
- `industry`: Industry sector
- `source_id`: Reference to job source
- `external_url`: URL to original job posting
- `external_id`: ID from external source
- `posted_date`: When job was posted
- `scraped_at`: When job was scraped
- `is_active`: Whether job is still active
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp

### JobSources Table

Stores job source information (LinkedIn, Indeed, etc.).

```sql
CREATE TABLE job_sources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL UNIQUE,
  url VARCHAR(500),
  description TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_job_sources_name ON job_sources(name);
```

**Columns**:
- `id`: Unique source identifier
- `name`: Source name (LinkedIn, Indeed, Wuzzuf, Bayt)
- `url`: Source website URL
- `description`: Source description
- `is_active`: Whether source is active
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp

### SavedJobs Table

Stores user's saved jobs.

```sql
CREATE TABLE saved_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  notes TEXT,
  rating INTEGER CHECK (rating >= 1 AND rating <= 5),
  saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, job_id)
);

CREATE INDEX idx_saved_jobs_user_id ON saved_jobs(user_id);
CREATE INDEX idx_saved_jobs_job_id ON saved_jobs(job_id);
CREATE INDEX idx_saved_jobs_saved_at ON saved_jobs(saved_at DESC);
```

**Columns**:
- `id`: Unique saved job identifier
- `user_id`: Reference to user
- `job_id`: Reference to job
- `notes`: User's notes about the job
- `rating`: User's rating (1-5)
- `saved_at`: When job was saved

### Alerts Table

Stores user job alerts.

```sql
CREATE TABLE alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  keywords TEXT[],
  locations TEXT[],
  salary_min INTEGER,
  salary_max INTEGER,
  job_types TEXT[],
  experience_levels TEXT[],
  industries TEXT[],
  frequency VARCHAR(50),
  notification_method VARCHAR(50),
  is_active BOOLEAN DEFAULT TRUE,
  last_triggered_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_alerts_user_id ON alerts(user_id);
CREATE INDEX idx_alerts_is_active ON alerts(is_active);
CREATE INDEX idx_alerts_created_at ON alerts(created_at DESC);
```

**Columns**:
- `id`: Unique alert identifier
- `user_id`: Reference to user
- `name`: Alert name
- `keywords`: Array of keywords to match
- `locations`: Array of locations to match
- `salary_min`: Minimum salary filter
- `salary_max`: Maximum salary filter
- `job_types`: Array of job types to match
- `experience_levels`: Array of experience levels to match
- `industries`: Array of industries to match
- `frequency`: Alert frequency (real-time, daily, weekly)
- `notification_method`: How to notify (email, in-app, sms)
- `is_active`: Whether alert is active
- `last_triggered_at`: When alert last matched jobs
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp

### SearchHistory Table

Stores user search history for analytics and recommendations.

```sql
CREATE TABLE search_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  query VARCHAR(500),
  filters JSONB,
  results_count INTEGER,
  searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_search_history_user_id ON search_history(user_id);
CREATE INDEX idx_search_history_searched_at ON search_history(searched_at DESC);
```

**Columns**:
- `id`: Unique search record identifier
- `user_id`: Reference to user
- `query`: Search query
- `filters`: JSON object with applied filters
- `results_count`: Number of results returned
- `searched_at`: When search was performed

### UserSkills Table

Stores user skills (many-to-many relationship).

```sql
CREATE TABLE user_skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  skill VARCHAR(100) NOT NULL,
  proficiency_level VARCHAR(50),
  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, skill)
);

CREATE INDEX idx_user_skills_user_id ON user_skills(user_id);
CREATE INDEX idx_user_skills_skill ON user_skills(skill);
```

**Columns**:
- `id`: Unique record identifier
- `user_id`: Reference to user
- `skill`: Skill name
- `proficiency_level`: Proficiency level (beginner, intermediate, advanced, expert)
- `added_at`: When skill was added

### JobSkills Table

Stores required skills for jobs (many-to-many relationship).

```sql
CREATE TABLE job_skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  skill VARCHAR(100) NOT NULL,
  required BOOLEAN DEFAULT TRUE,
  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(job_id, skill)
);

CREATE INDEX idx_job_skills_job_id ON job_skills(job_id);
CREATE INDEX idx_job_skills_skill ON job_skills(skill);
```

**Columns**:
- `id`: Unique record identifier
- `job_id`: Reference to job
- `skill`: Skill name
- `required`: Whether skill is required
- `added_at`: When skill was added

## Relationships

### One-to-Many Relationships

1. **Users → SavedJobs**: One user can have many saved jobs
2. **Users → Alerts**: One user can have many alerts
3. **Users → SearchHistory**: One user can have many search records
4. **Users → UserSkills**: One user can have many skills
5. **JobSources → Jobs**: One source can have many jobs
6. **Jobs → JobSkills**: One job can have many skills

### Many-to-Many Relationships

1. **Users ↔ Jobs** (through SavedJobs): Users can save many jobs, jobs can be saved by many users
2. **Users ↔ Skills** (through UserSkills): Users can have many skills, skills can belong to many users
3. **Jobs ↔ Skills** (through JobSkills): Jobs can require many skills, skills can be required by many jobs

## Indexes

### Performance Indexes

```sql
-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Jobs
CREATE INDEX idx_jobs_title ON jobs(title);
CREATE INDEX idx_jobs_company ON jobs(company);
CREATE INDEX idx_jobs_location ON jobs(location);
CREATE INDEX idx_jobs_posted_date ON jobs(posted_date DESC);
CREATE INDEX idx_jobs_source_id ON jobs(source_id);
CREATE INDEX idx_jobs_external_id ON jobs(external_id);

-- SavedJobs
CREATE INDEX idx_saved_jobs_user_id ON saved_jobs(user_id);
CREATE INDEX idx_saved_jobs_job_id ON saved_jobs(job_id);

-- Alerts
CREATE INDEX idx_alerts_user_id ON alerts(user_id);
CREATE INDEX idx_alerts_is_active ON alerts(is_active);

-- SearchHistory
CREATE INDEX idx_search_history_user_id ON search_history(user_id);
```

## Constraints

### Primary Keys

All tables have UUID primary keys for distributed system compatibility.

### Foreign Keys

- SavedJobs.user_id → Users.id (CASCADE DELETE)
- SavedJobs.job_id → Jobs.id (CASCADE DELETE)
- Alerts.user_id → Users.id (CASCADE DELETE)
- SearchHistory.user_id → Users.id (CASCADE DELETE)
- UserSkills.user_id → Users.id (CASCADE DELETE)
- JobSkills.job_id → Jobs.id (CASCADE DELETE)
- Jobs.source_id → JobSources.id

### Unique Constraints

- Users.email (unique)
- Jobs.external_id (unique)
- SavedJobs (user_id, job_id) - composite unique
- UserSkills (user_id, skill) - composite unique
- JobSkills (job_id, skill) - composite unique

### Check Constraints

- SavedJobs.rating: 1-5 or NULL

## Data Types

### UUID

Used for all primary keys and foreign keys for:
- Distributed system compatibility
- Better security (harder to guess IDs)
- Easier data migration

### VARCHAR

Used for:
- Email addresses (255 characters)
- Names and titles (255 characters)
- URLs (500 characters)
- Enums (50 characters)

### TEXT

Used for:
- Long descriptions
- Job descriptions
- User bios

### TEXT[]

Used for:
- Arrays of strings (job types, locations, skills)
- PostgreSQL native array type

### JSONB

Used for:
- Complex nested data (search filters)
- Flexible schema
- Efficient querying

### INTEGER

Used for:
- Salary values
- Counts
- Ratings

### BOOLEAN

Used for:
- Status flags (is_active, email_verified)
- Boolean conditions

### TIMESTAMP

Used for:
- All date/time values
- Defaults to CURRENT_TIMESTAMP
- Timezone-aware

## Migrations

Migrations are managed with Alembic. Key migrations:

1. **Initial Schema**: Create all tables and relationships
2. **Add Indexes**: Add performance indexes
3. **Add Constraints**: Add data integrity constraints
4. **Add Columns**: Add new features
5. **Modify Columns**: Update data types or constraints

## Performance Considerations

### Query Optimization

1. **Indexing Strategy**
   - Index frequently searched columns
   - Index foreign keys
   - Index date columns for range queries

2. **Query Patterns**
   - Use EXPLAIN ANALYZE to optimize queries
   - Avoid N+1 queries with proper joins
   - Use pagination for large result sets

3. **Partitioning**
   - Consider partitioning Jobs table by date
   - Partition SearchHistory by user_id

### Maintenance

1. **Vacuum and Analyze**
   ```sql
   VACUUM ANALYZE;
   ```

2. **Index Maintenance**
   ```sql
   REINDEX INDEX idx_jobs_posted_date;
   ```

3. **Statistics Update**
   ```sql
   ANALYZE;
   ```

## Backup and Recovery

### Backup Strategy

1. **Full Backups**: Daily full database backups
2. **Incremental Backups**: Hourly incremental backups
3. **Point-in-Time Recovery**: WAL archiving for PITR

### Backup Commands

```bash
# Full backup
pg_dump -U jobspy -d jobspy > backup_full.sql

# Compressed backup
pg_dump -U jobspy -d jobspy | gzip > backup_full.sql.gz

# Restore
psql -U jobspy -d jobspy < backup_full.sql
```

## Security

### Data Protection

1. **Encryption at Rest**: Database encryption
2. **Encryption in Transit**: SSL/TLS for connections
3. **Access Control**: Role-based database access
4. **Audit Logging**: Track data changes

### SQL Injection Prevention

- Use parameterized queries (SQLAlchemy ORM)
- Input validation
- Prepared statements

## Monitoring

### Key Metrics

1. **Query Performance**
   - Slow query log
   - Query execution time
   - Index usage

2. **Database Health**
   - Connection count
   - Cache hit ratio
   - Disk usage

3. **Data Integrity**
   - Constraint violations
   - Foreign key errors
   - Data consistency

## Future Enhancements

1. **Partitioning**: Partition large tables by date
2. **Sharding**: Horizontal scaling for massive datasets
3. **Read Replicas**: Separate read and write operations
4. **Caching Layer**: Redis for frequently accessed data
5. **Full-Text Search**: PostgreSQL full-text search for better search performance

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
