# 🏗️ Architecture Diagram - JobSpy Backend

## Clean Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                          │
│                    (HTTP, API, Controllers)                      │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FastAPI Routers (Thin Controllers)                       │  │
│  │  - jobs.py                                                 │  │
│  │  - auth.py                                                 │  │
│  │  - saved_jobs.py                                           │  │
│  │  - alerts.py                                               │  │
│  │                                                             │  │
│  │  Dependency Injection Container                            │  │
│  │  - dependencies.py                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓ ↑
                        HTTP Requests/Responses
                              ↓ ↑
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                           │
│                  (Use Cases, Orchestration)                      │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Use Cases (Business Workflows)                           │  │
│  │                                                             │  │
│  │  Jobs:                                                      │  │
│  │  - CreateJobUseCase                                        │  │
│  │  - GetJobDetailsUseCase                                    │  │
│  │  - UpdateJobUseCase                                        │  │
│  │  - DeleteJobUseCase                                        │  │
│  │  - ListJobsUseCase                                         │  │
│  │                                                             │  │
│  │  Search:                                                    │  │
│  │  - SearchJobsUseCase                                       │  │
│  │  - AdvancedSearchUseCase                                   │  │
│  │                                                             │  │
│  │  Scraping:                                                  │  │
│  │  - ProcessScrapedJobsUseCase                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  DTOs (Data Transfer Objects)                             │  │
│  │  - JobDTO                                                  │  │
│  │  - SearchRequestDTO                                        │  │
│  │  - SearchResponseDTO                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Mappers (Data Conversion)                                │  │
│  │  - JobMapper (Raw → Domain)                               │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓ ↑
                        Uses Domain Interfaces
                              ↓ ↑
┌─────────────────────────────────────────────────────────────────┐
│                        DOMAIN LAYER                              │
│                  (Business Logic, Entities)                      │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Entities (Business Objects)                              │  │
│  │  - Job                                                     │  │
│  │    • is_remote()                                           │  │
│  │    • matches_skills()                                      │  │
│  │    • is_entry_level()                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Value Objects (Immutable Values)                         │  │
│  │  - Salary                                                  │  │
│  │  - Location                                                │  │
│  │  - JobType                                                 │  │
│  │  - ExperienceLevel                                         │  │
│  │  - DateRange                                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Domain Services (Business Logic)                         │  │
│  │  - JobScoringService                                       │  │
│  │  - SkillExtractionService                                  │  │
│  │  - JobMatchingService                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Interfaces (Contracts)                                    │  │
│  │  - IJobRepository                                          │  │
│  │  - ICacheRepository                                        │  │
│  │  - IJobScraper                                             │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↑
                    Implemented by Infrastructure
                              ↑
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                          │
│              (External Systems, Databases, APIs)                 │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Persistence - SQLAlchemy                                 │  │
│  │                                                             │  │
│  │  Repositories:                                             │  │
│  │  - JobRepositoryImpl (implements IJobRepository)          │  │
│  │                                                             │  │
│  │  ORM Models:                                               │  │
│  │  - JobModel                                                │  │
│  │  - UserModel                                               │  │
│  │  - AlertModel                                              │  │
│  │                                                             │  │
│  │  Mappers:                                                   │  │
│  │  - JobORMMapper (ORM ↔ Domain)                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Persistence - Redis                                       │  │
│  │  - CacheRepositoryImpl (implements ICacheRepository)      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  External Services                                         │  │
│  │  - EmailService                                            │  │
│  │  - ScraperService                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓ ↑
                    External Systems (DB, Redis, APIs)
```

---

## Dependency Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     DEPENDENCY DIRECTION                         │
│                                                                   │
│  Presentation Layer                                              │
│         ↓                                                         │
│  Application Layer                                               │
│         ↓                                                         │
│  Domain Layer (Core - No Dependencies)                           │
│         ↑                                                         │
│  Infrastructure Layer (Implements Domain Interfaces)             │
│                                                                   │
│  Rule: Dependencies point INWARD                                 │
│  - Outer layers depend on inner layers                           │
│  - Inner layers NEVER depend on outer layers                     │
│  - Domain layer has NO dependencies                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Use Case Flow Example: Create Job

```
1. HTTP Request
   ↓
2. Router (Presentation)
   @router.post("/jobs")
   @inject
   async def create_job(
       request: CreateJobRequest,
       use_case: CreateJobUseCase = Depends(...)
   )
   ↓
3. Use Case (Application)
   CreateJobUseCase.execute(request)
   ├─→ JobMapper.to_domain(request)
   │   ↓
   │   Domain Entity (Job)
   │
   ├─→ JobScoringService.calculate_score(job)
   │   ↓
   │   Score calculated
   │
   └─→ JobRepository.save(job)
       ↓
4. Repository (Infrastructure)
   JobRepositoryImpl.save(job)
   ├─→ JobORMMapper.to_orm(job)
   │   ↓
   │   ORM Model (JobModel)
   │
   └─→ Database.save(orm_model)
       ↓
5. Database (PostgreSQL)
   ↓
6. Return Response
   Job saved → Domain Entity → DTO → JSON Response
```

---

## Data Flow: Raw Data → Domain → ORM → Database

```
┌─────────────────────────────────────────────────────────────────┐
│                         DATA FLOW                                │
│                                                                   │
│  Raw Data (API Request)                                          │
│  {                                                                │
│    "title": "Software Engineer",                                 │
│    "salary": "$50,000 - $80,000",                                │
│    ...                                                            │
│  }                                                                │
│         ↓                                                         │
│  JobMapper.to_domain()                                           │
│         ↓                                                         │
│  Domain Entity (Job)                                             │
│  Job(                                                             │
│    title="Software Engineer",                                    │
│    salary=Salary(                                                │
│      min_amount=Decimal("50000"),                                │
│      max_amount=Decimal("80000"),                                │
│      currency="USD"                                              │
│    ),                                                             │
│    ...                                                            │
│  )                                                                │
│         ↓                                                         │
│  JobORMMapper.to_orm()                                           │
│         ↓                                                         │
│  ORM Model (JobModel)                                            │
│  JobModel(                                                        │
│    title="Software Engineer",                                    │
│    salary_min=50000.0,                                           │
│    salary_max=80000.0,                                           │
│    salary_currency="USD",                                        │
│    ...                                                            │
│  )                                                                │
│         ↓                                                         │
│  Database (PostgreSQL)                                           │
│  INSERT INTO jobs (title, salary_min, ...) VALUES (...)          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Caching Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                      CACHING FLOW                                │
│                                                                   │
│  1. Request comes in                                             │
│     ↓                                                             │
│  2. Use Case checks cache                                        │
│     cache_repository.get(key)                                    │
│     ↓                                                             │
│  3. Cache Hit?                                                   │
│     ├─ YES → Return cached data                                  │
│     │                                                             │
│     └─ NO → Continue                                             │
│        ↓                                                          │
│  4. Query database                                               │
│     job_repository.get_by_id(id)                                 │
│     ↓                                                             │
│  5. Cache result                                                 │
│     cache_repository.set(key, data, ttl)                         │
│     ↓                                                             │
│  6. Return data                                                  │
│                                                                   │
│  Note: Caching is in USE CASES, not repositories!                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Dependency Injection Container

```
┌─────────────────────────────────────────────────────────────────┐
│                    DI CONTAINER STRUCTURE                        │
│                                                                   │
│  Container                                                        │
│  ├── Infrastructure                                              │
│  │   ├── job_repository (Factory)                               │
│  │   │   └── Creates new instance per request                   │
│  │   ├── cache_repository (Singleton)                           │
│  │   │   └── Reuses same instance                               │
│  │   └── job_orm_mapper (Singleton)                             │
│  │       └── Reuses same instance                               │
│  │                                                                │
│  ├── Domain                                                       │
│  │   ├── job_scoring_service (Singleton)                        │
│  │   │   └── Stateless, can be reused                           │
│  │   ├── skill_extraction_service (Singleton)                   │
│  │   │   └── Stateless, can be reused                           │
│  │   └── job_matching_service (Singleton)                       │
│  │       └── Stateless, can be reused                           │
│  │                                                                │
│  └── Application                                                  │
│      ├── job_mapper (Singleton)                                  │
│      │   └── Stateless, can be reused                           │
│      └── Use Cases (all Factory)                                 │
│          ├── create_job_use_case                                 │
│          ├── get_job_details_use_case                            │
│          ├── update_job_use_case                                 │
│          ├── delete_job_use_case                                 │
│          ├── list_jobs_use_case                                  │
│          ├── search_jobs_use_case                                │
│          ├── advanced_search_use_case                            │
│          └── process_scraped_jobs_use_case                       │
│              └── Each creates new instance per request           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layer Responsibilities

### Presentation Layer
- **Responsibility:** HTTP concerns, request/response handling
- **Contains:** Routers, controllers, DI container
- **Dependencies:** Application layer
- **Rules:**
  - No business logic
  - Only HTTP status codes and error handling
  - Delegates everything to use cases

### Application Layer
- **Responsibility:** Orchestration, use cases, workflows
- **Contains:** Use cases, DTOs, mappers
- **Dependencies:** Domain layer
- **Rules:**
  - Orchestrates domain services
  - Handles caching
  - Converts between DTOs and domain entities
  - No infrastructure dependencies

### Domain Layer
- **Responsibility:** Business logic, business rules
- **Contains:** Entities, value objects, domain services, interfaces
- **Dependencies:** NONE (pure business logic)
- **Rules:**
  - No infrastructure dependencies
  - No framework dependencies
  - Pure business logic only
  - Defines interfaces for infrastructure

### Infrastructure Layer
- **Responsibility:** External systems, databases, APIs
- **Contains:** Repository implementations, ORM models, external services
- **Dependencies:** Domain layer (implements interfaces)
- **Rules:**
  - Implements domain interfaces
  - Handles database operations
  - Handles external API calls
  - Converts between ORM and domain

---

## Key Principles

### 1. Dependency Inversion
```
❌ BAD: High-level depends on low-level
UseCase → Repository (concrete class)

✅ GOOD: Both depend on abstraction
UseCase → IRepository ← RepositoryImpl
```

### 2. Single Responsibility
```
❌ BAD: God class with 12 responsibilities
JobProcessingService (900 lines)

✅ GOOD: Focused classes
- CreateJobUseCase (80 lines)
- GetJobDetailsUseCase (90 lines)
- JobScoringService (250 lines)
```

### 3. Separation of Concerns
```
❌ BAD: Mixed concerns
Repository with caching logic

✅ GOOD: Separated concerns
- Repository: Data access only
- CacheRepository: Caching only
- UseCase: Orchestration (uses both)
```

---

## File Organization

```
Backend/app/
├── domain/                      # 13 files, ~2,000 lines
│   ├── entities/
│   ├── value_objects/
│   ├── services/
│   └── interfaces/
│
├── application/                 # 16 files, ~2,500 lines
│   ├── use_cases/
│   ├── dto/
│   └── mappers/
│
├── infrastructure/              # 12 files, ~800 lines
│   └── persistence/
│       ├── sqlalchemy/
│       └── redis/
│
├── presentation/                # 5 files, ~250 lines
│   └── api/v1/
│
└── shared/                      # 5 files, ~150 lines
    └── exceptions/

Total: 51 files, ~5,700 lines
```

---

**Last Updated:** 2026-05-01  
**Status:** Architecture Implemented (70% Complete)

