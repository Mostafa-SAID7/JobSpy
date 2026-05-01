# 🧹 Cleanup and Migration Plan

## Current State Analysis

### ✅ NEW Architecture (Clean Architecture)
```
Backend/app/
├── domain/              ✅ NEW - Pure business logic
│   ├── entities/
│   ├── value_objects/
│   ├── services/
│   └── interfaces/
│
└── application/         ✅ NEW - Use cases & orchestration
    ├── use_cases/
    ├── dto/
    └── mappers/
```

### ⚠️ OLD Architecture (To be migrated/deprecated)
```
Backend/app/
├── models/              ⚠️ OLD - ORM models (needs migration to infrastructure)
├── repositories/        ⚠️ OLD - Mixed with caching (needs refactoring)
├── services/            ⚠️ OLD - God classes (to be deprecated)
├── schemas/             ⚠️ OLD - Pydantic schemas (keep for now, will become API schemas)
├── routers/             ⚠️ OLD - Controllers with business logic (needs refactoring)
├── utils/               ⚠️ OLD - Vague naming (needs reorganization)
└── core/                ✅ KEEP - Infrastructure config (will move to infrastructure/)
```

---

## 📋 Migration Strategy

### Phase 3A: Create Infrastructure Layer (NEW)

**Create these directories:**
```
Backend/app/infrastructure/
├── persistence/
│   ├── sqlalchemy/
│   │   ├── models/          # Move from app/models/
│   │   ├── repositories/    # Implement interfaces from domain
│   │   └── mappers/         # ORM ↔ Domain conversion
│   └── redis/
│       └── cache_repository_impl.py
├── scrapers/
│   ├── base_scraper.py
│   ├── linkedin_scraper.py
│   ├── indeed_scraper.py
│   └── scraper_factory.py
└── external_services/
    └── email_service_impl.py
```

### Phase 3B: Migrate ORM Models

**Action:** Move `app/models/` → `app/infrastructure/persistence/sqlalchemy/models/`

**Files to move:**
- `models/job.py` → `infrastructure/persistence/sqlalchemy/models/job_model.py`
- `models/user.py` → `infrastructure/persistence/sqlalchemy/models/user_model.py`
- `models/alert.py` → `infrastructure/persistence/sqlalchemy/models/alert_model.py`
- `models/saved_job.py` → `infrastructure/persistence/sqlalchemy/models/saved_job_model.py`
- `models/search_history.py` → `infrastructure/persistence/sqlalchemy/models/search_history_model.py`

**Why:** Separate ORM concerns from domain entities

### Phase 3C: Refactor Repositories

**Action:** Create new repository implementations that:
1. Implement domain interfaces
2. Remove caching logic (move to cache repository)
3. Convert between ORM models and domain entities

**Old files (to be deprecated):**
- ❌ `repositories/job_repo.py` (has caching mixed in)
- ❌ `repositories/user_repo.py`
- ❌ `repositories/alert_repo.py`
- ❌ `repositories/saved_job_repo.py`
- ❌ `repositories/search_history_repo.py`
- ❌ `repositories/stats_repo.py`

**New files (to be created):**
- ✅ `infrastructure/persistence/sqlalchemy/repositories/job_repository_impl.py`
- ✅ `infrastructure/persistence/sqlalchemy/repositories/user_repository_impl.py`
- ✅ `infrastructure/persistence/redis/cache_repository_impl.py`

### Phase 3D: Deprecate Old Services

**Action:** Mark old services as deprecated, create migration guide

**Files to deprecate:**
- ❌ `services/job_processing_service.py` → Use `ProcessScrapedJobsUseCase`
- ❌ `services/scraping_service.py` → Use `ProcessScrapedJobsUseCase`
- ❌ `services/search_service.py` → Use `SearchJobsUseCase`, `AdvancedSearchUseCase`
- ⚠️ `services/alert_service.py` → Keep for now (Phase 4)
- ⚠️ `services/email_service.py` → Keep for now (Phase 4)
- ⚠️ `services/stats_service.py` → Keep for now (Phase 4)

### Phase 3E: Reorganize Utilities

**Action:** Move from vague `utils/` to specific locations

**Old:**
- `utils/security.py` → `infrastructure/security/` or `shared/security/`

**New structure:**
```
Backend/app/shared/
├── security/
│   ├── password_hasher.py
│   ├── token_manager.py
│   └── auth_utils.py
├── exceptions/
│   ├── domain_exceptions.py
│   ├── application_exceptions.py
│   └── infrastructure_exceptions.py
└── constants/
    ├── scoring_constants.py
    └── cache_keys.py
```

---

## 🗑️ Files to Delete (After Migration)

### Immediate (Phase 3)
None yet - keep old files until new ones are tested

### After Phase 4 (Dependency Injection Complete)
- ❌ `services/job_processing_service.py`
- ❌ `services/scraping_service.py`
- ❌ `services/search_service.py`

### After Phase 5 (Controllers Refactored)
- ❌ Old repository implementations (if not needed)

---

## ✅ Files to Keep (No Changes Needed)

### Core Infrastructure
- ✅ `core/config.py` - Configuration
- ✅ `core/database.py` - Database connection
- ✅ `core/redis.py` - Redis client
- ✅ `core/logging.py` - Logging setup
- ✅ `core/celery.py` - Celery config

### API Layer (Will refactor in Phase 5)
- ⚠️ `routers/*.py` - Keep but will refactor
- ⚠️ `schemas/*.py` - Keep as API schemas

### Application Entry
- ✅ `main.py` - Application entry point
- ✅ `tasks.py` - Celery tasks

---

## 📝 Step-by-Step Execution Plan

### Step 1: Create Infrastructure Structure ✅ NEXT
```bash
mkdir -p Backend/app/infrastructure/persistence/sqlalchemy/{models,repositories,mappers}
mkdir -p Backend/app/infrastructure/persistence/redis
mkdir -p Backend/app/infrastructure/scrapers
mkdir -p Backend/app/infrastructure/external_services
mkdir -p Backend/app/shared/{security,exceptions,constants}
```

### Step 2: Move ORM Models
- Copy `models/*.py` to `infrastructure/persistence/sqlalchemy/models/`
- Rename to `*_model.py` for clarity
- Update imports

### Step 3: Create Repository Implementations
- Implement `IJobRepository` interface
- Implement `ICacheRepository` interface
- Create ORM ↔ Domain mappers

### Step 4: Create Deprecation Notices
- Add deprecation warnings to old services
- Create migration guide

### Step 5: Update Imports (Gradual)
- Update one module at a time
- Test after each change
- Keep old code working during migration

---

## 🎯 Success Criteria

### Phase 3 Complete When:
- [x] Infrastructure layer created
- [x] ORM models separated from domain
- [x] Repository implementations created
- [x] Caching extracted to separate repository
- [x] Old services marked as deprecated
- [x] All tests still passing
- [x] No functionality broken

---

## ⚠️ Migration Risks & Mitigation

### Risk 1: Breaking Existing Code
**Mitigation:** Keep old code working, migrate gradually

### Risk 2: Import Errors
**Mitigation:** Update imports carefully, test thoroughly

### Risk 3: Database Issues
**Mitigation:** ORM models stay the same, just moved

### Risk 4: Test Failures
**Mitigation:** Run tests after each change

---

## 📊 Current vs Target Structure

### Current (Mixed)
```
app/
├── models/          # ORM (infrastructure concern)
├── repositories/    # Mixed (data + caching)
├── services/        # God classes
├── domain/          # ✅ NEW
└── application/     # ✅ NEW
```

### Target (Clean Architecture)
```
app/
├── domain/              # ✅ Pure business logic
├── application/         # ✅ Use cases
├── infrastructure/      # ✅ External concerns
│   ├── persistence/
│   ├── scrapers/
│   └── external_services/
├── presentation/        # API layer (Phase 5)
│   └── api/v1/routers/
└── shared/              # Cross-cutting concerns
```

---

## 🚀 Next Actions

1. ✅ Create infrastructure directory structure
2. ✅ Create `CacheRepositoryImpl`
3. ✅ Create `JobRepositoryImpl`
4. ✅ Create ORM mappers
5. ✅ Create base scraper
6. ⏳ Test new implementations
7. ⏳ Mark old services as deprecated
8. ⏳ Update documentation

---

**Status:** Ready to execute Phase 3
**Estimated Time:** 3-4 hours
**Risk Level:** Low (keeping old code during migration)
