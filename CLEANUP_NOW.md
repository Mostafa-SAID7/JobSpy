# 🧹 Cleanup Status - Cannot Execute Yet

**Date:** 2026-05-01  
**Status:** ⚠️ BLOCKED - Services Still In Use  
**Reason:** Routers and other services still depend on deprecated code

---

## ⚠️ IMPORTANT: Why We Can't Clean Up Yet

### Current Dependencies Found:

**`job_processing_service.py` is used by:**
- ✅ `services/search_service.py` (also deprecated)
- ✅ `services/scraping_service.py` (also deprecated)
- ⚠️ `services/alert_service.py` (STILL IN USE!)
- ⚠️ `scripts/seed_sample_jobs.py` (script)

**`search_service.py` is used by:**
- ⚠️ `routers/jobs.py` (STILL IN USE!)

**`scraping_service.py` is used by:**
- Potentially by routers or tasks

**Conclusion:** ❌ Cannot delete yet - would break the application!

---

## 📋 What CAN Be Done Now

### ✅ Safe Actions (No Breaking Changes)

1. **Keep Deprecation Notices** ✅ Already done
2. **Document Dependencies** ✅ Done below
3. **Plan Phase 5 Migration** ✅ See below

### ❌ Unsafe Actions (Would Break App)

1. ❌ Delete deprecated services
2. ❌ Delete old repositories  
3. ❌ Remove old imports

---

## 📊 Dependency Analysis

### Dependency Graph

```
routers/jobs.py
    └── services/search_service.py (deprecated)
            └── services/job_processing_service.py (deprecated)

services/alert_service.py (in use)
    └── services/job_processing_service.py (deprecated)

services/scraping_service.py (deprecated)
    └── services/job_processing_service.py (deprecated)

scripts/seed_sample_jobs.py
    └── services/job_processing_service.py (deprecated)
```

**Conclusion:** Must refactor routers and alert_service FIRST before cleanup.

---

## 🎯 Cleanup Roadmap

### Phase 5A: Refactor jobs.py Router (REQUIRED FIRST)

**File:** `Backend/app/routers/jobs.py`

**Current:**
```python
from app.services.search_service import SearchService

@router.get("/search")
async def search_jobs(query: str, db: AsyncSession = Depends(get_db)):
    search_service = SearchService(db)
    result = await search_service.search_jobs(user_id, query)
    return result
```

**Target:**
```python
from dependency_injector.wiring import inject, Provide
from app.presentation.api.v1.dependencies import Container
from app.application.use_cases.search import SearchJobsUseCase

@router.get("/search")
@inject
async def search_jobs(
    query: str,
    use_case: SearchJobsUseCase = Depends(Provide[Container.search_jobs_use_case]),
):
    result = await use_case.execute(query)
    return result
```

**Estimated Time:** 2-3 hours  
**Status:** ⏳ Pending

---

### Phase 5B: Refactor alert_service.py

**File:** `Backend/app/services/alert_service.py`

**Current:** Uses `JobProcessingService` for filtering

**Target:** Create `AlertUseCase` that uses domain services directly

**Estimated Time:** 1-2 hours  
**Status:** ⏳ Pending

---

### Phase 5C: Update seed_sample_jobs.py Script

**File:** `Backend/scripts/seed_sample_jobs.py`

**Current:** Uses `JobProcessingService`

**Target:** Use `ProcessScrapedJobsUseCase` directly

**Estimated Time:** 30 minutes  
**Status:** ⏳ Pending

---

### Phase 5D: Execute Cleanup (FINAL STEP)

**After all above complete:**

```bash
# NOW safe to remove
rm Backend/app/services/job_processing_service.py
rm Backend/app/services/scraping_service.py
rm Backend/app/services/search_service.py
```

**Estimated Time:** 10 minutes  
**Status:** ⏳ Blocked by Phase 5A, 5B, 5C

---

## ✅ What We CAN Do Now

### 1. Update Documentation ✅

Mark clearly which files are deprecated and why they can't be removed yet.

### 2. Create Migration Tickets

- [ ] Ticket 1: Refactor jobs.py router to use DI
- [ ] Ticket 2: Refactor alert_service.py to use cases
- [ ] Ticket 3: Update seed_sample_jobs.py script
- [ ] Ticket 4: Remove deprecated services

### 3. Add TODO Comments

Add comments to deprecated files explaining the migration path.

---

## 📝 Updated Services __init__.py

**File:** `Backend/app/services/__init__.py`

**Add deprecation warnings:**

```python
"""
Services Layer - JobSpy Backend

DEPRECATION NOTICE:
- JobProcessingService: Use ProcessScrapedJobsUseCase instead
- ScrapingService: Use ProcessScrapedJobsUseCase instead  
- SearchService: Use SearchJobsUseCase or AdvancedSearchUseCase instead

These services are kept temporarily for backward compatibility.
They will be removed after Phase 5 (router refactoring) is complete.

See: Backend/app/services/DEPRECATION_NOTICE.md
"""
import warnings

# Deprecated services (will be removed in Phase 5)
from .job_processing_service import JobProcessingService
from .scraping_service import ScrapingService
from .search_service import SearchService

# Active services
from .alert_service import AlertService
from .email_service import EmailService
from .stats_service import StatsService

# Issue deprecation warnings
warnings.warn(
    "JobProcessingService is deprecated. Use ProcessScrapedJobsUseCase instead.",
    DeprecationWarning,
    stacklevel=2
)

warnings.warn(
    "SearchService is deprecated. Use SearchJobsUseCase or AdvancedSearchUseCase instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    # Deprecated (will be removed)
    "JobProcessingService",
    "ScrapingService", 
    "SearchService",
    # Active
    "AlertService",
    "EmailService",
    "StatsService",
]
```

---

## 🎯 Immediate Action Items

### 1. Add Deprecation Warnings to Code ✅

Let's add Python deprecation warnings so developers know these are deprecated.

### 2. Update DEPRECATION_NOTICE.md ✅

Add dependency information and migration timeline.

### 3. Create Phase 5 Detailed Plan ✅

Document exactly how to refactor each router.

---

## 📊 Timeline

### Current Week (Week 6)
- [x] Phase 4: DI Container (80% done)
- [ ] Complete Phase 4: Update main.py
- [ ] Add deprecation warnings to code

### Next Week (Week 7)
- [ ] Phase 5A: Refactor jobs.py router
- [ ] Phase 5B: Refactor alert_service.py
- [ ] Phase 5C: Update scripts

### Week 8
- [ ] Phase 5D: Remove deprecated services
- [ ] Phase 6: Testing & final cleanup

---

## ✅ Safe Actions We Can Take NOW

### Action 1: Add Deprecation Warnings

I'll update the deprecated service files to add warnings.

### Action 2: Update Documentation

Update DEPRECATION_NOTICE.md with dependency info.

### Action 3: Create Detailed Migration Guide

Document exact steps for Phase 5.

---

**Status:** ⚠️ Cleanup Blocked  
**Blocker:** Routers still use deprecated services  
**Next:** Complete Phase 5 router refactoring  
**ETA for Cleanup:** After Phase 5 complete (~1-2 weeks)



