# 🧹 Cleanup Execution Plan

**Date:** 2026-05-01  
**Status:** Ready to Execute

---

## Overview

This document outlines the cleanup plan to remove old/deprecated files and ensure the codebase is clean with the new Clean Architecture structure.

---

## ⚠️ IMPORTANT: What NOT to Delete Yet

### Keep These Files (Still in Use)

**Core Infrastructure (Keep):**
- ✅ `Backend/app/core/` - All files (config, database, redis, logging, celery)
- ✅ `Backend/app/main.py` - Application entry point
- ✅ `Backend/app/tasks.py` - Celery tasks

**ORM Models (Keep for now):**
- ✅ `Backend/app/models/` - All ORM models still used by old repositories
  - `job.py`
  - `user.py`
  - `alert.py`
  - `saved_job.py`
  - `search_history.py`

**API Schemas (Keep as API layer):**
- ✅ `Backend/app/schemas/` - All Pydantic schemas for API validation
  - `job.py`
  - `user.py`
  - `alert.py`
  - `saved_job.py`
  - `search_history.py`

**Routers (Keep - will refactor in Phase 5):**
- ✅ `Backend/app/routers/` - All routers
  - `jobs.py`
  - `auth.py`
  - `alerts.py`
  - `saved_jobs.py`
  - `stats.py`
  - `users.py`

**Old Repositories (Keep until Phase 5 complete):**
- ✅ `Backend/app/repositories/` - Still used by routers
  - `job_repo.py`
  - `user_repo.py`
  - `alert_repo.py`
  - `saved_job_repo.py`
  - `search_history_repo.py`
  - `stats_repo.py`

**Services (Keep some):**
- ✅ `Backend/app/services/alert_service.py` - Not deprecated yet
- ✅ `Backend/app/services/email_service.py` - Not deprecated yet
- ✅ `Backend/app/services/stats_service.py` - Not deprecated yet
- ✅ `Backend/app/services/DEPRECATION_NOTICE.md` - Documentation

---

## ❌ Files to Delete Now (Safe to Remove)

### Deprecated Services (Already Replaced)

These services are deprecated and fully replaced by new use cases:

1. **`Backend/app/services/job_processing_service.py`** ❌
   - **Reason:** Replaced by `ProcessScrapedJobsUseCase`
   - **Size:** ~900 lines
   - **Status:** Deprecated, marked in DEPRECATION_NOTICE.md

2. **`Backend/app/services/scraping_service.py`** ❌
   - **Reason:** Unnecessary wrapper, replaced by `ProcessScrapedJobsUseCase`
   - **Status:** Deprecated

3. **`Backend/app/services/search_service.py`** ❌
   - **Reason:** Replaced by `SearchJobsUseCase` and `AdvancedSearchUseCase`
   - **Size:** ~500 lines
   - **Status:** Deprecated, marked in DEPRECATION_NOTICE.md

---

## 🗑️ Other Files to Clean Up

### Duplicate Documentation (Old Versions)

Check for any duplicate or outdated documentation files:

1. **Check for old README files:**
   - Look for `README.old.md`, `README.backup.md`, etc.

2. **Check for old migration docs:**
   - Look for temporary migration notes

---

## 📋 Cleanup Execution Steps

### Step 1: Verify No Active Imports

Before deleting, verify these deprecated services are not imported anywhere:

```bash
# Search for imports of deprecated services
grep -r "from app.services.job_processing_service" Backend/app/
grep -r "from app.services.scraping_service" Backend/app/
grep -r "from app.services.search_service" Backend/app/
grep -r "import job_processing_service" Backend/app/
grep -r "import scraping_service" Backend/app/
grep -r "import search_service" Backend/app/
```

### Step 2: Check Router Usage

Verify routers are not using deprecated services:

```bash
# Check routers
grep -n "JobProcessingService\|ScrapingService\|SearchService" Backend/app/routers/*.py
```

### Step 3: Delete Deprecated Services

If no active imports found, delete:

```bash
rm Backend/app/services/job_processing_service.py
rm Backend/app/services/scraping_service.py
rm Backend/app/services/search_service.py
```

### Step 4: Update Services __init__.py

Remove deprecated services from `Backend/app/services/__init__.py`:

```python
# Remove these lines:
# from .job_processing_service import JobProcessingService
# from .scraping_service import ScrapingService
# from .search_service import SearchService
```

### Step 5: Clean Up Utils

Move security utilities to shared layer:

```bash
# Create shared/security directory if not exists
mkdir -p Backend/app/shared/security

# Move security utils
mv Backend/app/utils/security.py Backend/app/shared/security/

# Update imports in files that use it
```

### Step 6: Remove Empty Directories

After moving files, remove empty directories:

```bash
# Check if utils is empty
ls Backend/app/utils/

# If empty, remove it
rmdir Backend/app/utils/
```

---

## ✅ Verification Checklist

After cleanup, verify:

- [ ] All tests still pass: `pytest Backend/tests/`
- [ ] Application starts: `uvicorn app.main:app`
- [ ] No import errors in logs
- [ ] All endpoints still accessible
- [ ] No broken imports

---

## 🔄 Rollback Plan

If something breaks after cleanup:

```bash
# Restore deleted files from git
git checkout HEAD -- Backend/app/services/job_processing_service.py
git checkout HEAD -- Backend/app/services/scraping_service.py
git checkout HEAD -- Backend/app/services/search_service.py
```

---

## 📊 Expected Results

### Before Cleanup
```
Backend/app/services/
├── __init__.py
├── alert_service.py          ✅ Keep
├── email_service.py          ✅ Keep
├── stats_service.py          ✅ Keep
├── job_processing_service.py ❌ Delete
├── scraping_service.py       ❌ Delete
├── search_service.py         ❌ Delete
└── DEPRECATION_NOTICE.md     ✅ Keep
```

### After Cleanup
```
Backend/app/services/
├── __init__.py
├── alert_service.py          ✅ Kept
├── email_service.py          ✅ Kept
├── stats_service.py          ✅ Kept
└── DEPRECATION_NOTICE.md     ✅ Kept
```

**Files Removed:** 3  
**Lines Removed:** ~1,400 lines of deprecated code

---

## 🎯 Benefits of Cleanup

1. **Reduced Confusion:** No duplicate implementations
2. **Clearer Codebase:** Only active code remains
3. **Easier Maintenance:** Less code to maintain
4. **Better Onboarding:** New developers see only current architecture

---

## ⚠️ Important Notes

1. **Don't delete repositories yet:** They're still used by routers
2. **Don't delete models yet:** They're still used by repositories
3. **Don't delete schemas:** They're used for API validation
4. **Keep routers:** Will refactor in Phase 5

---

## 📅 Timeline

- **Now:** Delete deprecated services (safe)
- **After Phase 5:** Delete old repositories
- **After Phase 6:** Final cleanup and optimization

---

**Status:** Ready to Execute  
**Risk Level:** Low (deprecated services not in use)  
**Estimated Time:** 15-30 minutes

