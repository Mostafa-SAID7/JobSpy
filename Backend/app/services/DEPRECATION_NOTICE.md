# ⚠️ DEPRECATION NOTICE

## These Services Are Deprecated

The following services in this directory are **deprecated** and will be removed in a future version.

### Deprecated Services

#### 1. `job_processing_service.py` ❌ DEPRECATED
**Reason:** God class with 12+ responsibilities

**Replacement:** Use the following use cases instead:
- `app.application.use_cases.scraping.ProcessScrapedJobsUseCase` - For processing scraped jobs
- `app.domain.services.JobScoringService` - For scoring jobs
- `app.domain.services.SkillExtractionService` - For extracting skills
- `app.application.mappers.JobMapper` - For parsing/normalizing job data

**Migration Example:**
```python
# OLD (Deprecated)
from app.services.job_processing_service import JobProcessingService

job_processor = JobProcessingService(db)
result = await job_processor.process_scraped_jobs(jobs_data, "LinkedIn")

# NEW (Recommended)
from app.application.use_cases.scraping import ProcessScrapedJobsUseCase
from app.domain.services import JobScoringService, SkillExtractionService
from app.application.mappers import JobMapper
from app.infrastructure.persistence.sqlalchemy.repositories import JobRepositoryImpl

# With dependency injection (Phase 4)
use_case = ProcessScrapedJobsUseCase(
    job_repository=JobRepositoryImpl(db),
    scoring_service=JobScoringService(),
    skill_service=SkillExtractionService(),
    job_mapper=JobMapper(),
)
result = await use_case.execute(jobs_data, "LinkedIn")
```

---

#### 2. `scraping_service.py` ❌ DEPRECATED
**Reason:** Unnecessary abstraction that just delegates to JobProcessingService

**Replacement:** Use `ProcessScrapedJobsUseCase` directly

---

#### 3. `search_service.py` ❌ DEPRECATED
**Reason:** God class with 9+ responsibilities (search, cache, recommendations, trending, etc.)

**Replacement:** Use the following use cases instead:
- `app.application.use_cases.search.SearchJobsUseCase` - For basic search
- `app.application.use_cases.search.AdvancedSearchUseCase` - For advanced search with filters

**Migration Example:**
```python
# OLD (Deprecated)
from app.services.search_service import SearchService

search_service = SearchService(db)
result = await search_service.search_jobs(user_id, "python developer")

# NEW (Recommended)
from app.application.use_cases.search import SearchJobsUseCase
from app.infrastructure.persistence.sqlalchemy.repositories import JobRepositoryImpl
from app.infrastructure.persistence.redis import CacheRepositoryImpl
from app.domain.services import JobScoringService

use_case = SearchJobsUseCase(
    job_repository=JobRepositoryImpl(db),
    cache_repository=CacheRepositoryImpl(),
    scoring_service=JobScoringService(),
)
result = await use_case.execute("python developer")
```

---

### Services to Keep (For Now)

These services are **NOT deprecated** yet:

- ✅ `alert_service.py` - Will be refactored in Phase 4
- ✅ `email_service.py` - Will be moved to infrastructure in Phase 4
- ✅ `stats_service.py` - Will be refactored in Phase 4

---

## Migration Timeline

- **Phase 3 (Current)**: Deprecation notices added, new implementations available
- **Phase 4**: Dependency injection setup, gradual migration
- **Phase 5**: Controllers refactored to use new architecture
- **Phase 6**: Old services removed completely

---

## Benefits of New Architecture

### Before (Old Services)
- ❌ God classes with 10+ responsibilities
- ❌ Tight coupling
- ❌ Hard to test
- ❌ Mixed concerns (business logic + caching + data access)

### After (New Architecture)
- ✅ Single responsibility per class
- ✅ Loose coupling via interfaces
- ✅ Easy to test (mockable dependencies)
- ✅ Clear separation of concerns

---

## Need Help?

See documentation:
- `IMPLEMENTATION_SUMMARY.md` - Overview of new architecture
- `NEXT_STEPS_GUIDE.md` - Migration guide
- `PHASE_2_COMPLETION_REPORT.md` - Detailed changes

---

**Last Updated:** 2026-05-01
**Status:** Deprecated but still functional
**Removal Date:** TBD (after Phase 6)
