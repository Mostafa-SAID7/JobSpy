# 🚀 Phase 4 & 5 Implementation Guide

## Phase 4: Dependency Injection ✅ 80% COMPLETE

### ✅ Completed Tasks

1. **Created Presentation Layer Structure** ✅
   ```
   Backend/app/presentation/
   └── api/
       └── v1/
           ├── dependencies.py    # DI Container
           └── deps.py            # FastAPI dependencies
   ```

2. **Created DI Container** ✅
   - File: `presentation/api/v1/dependencies.py`
   - Wired up all dependencies:
     - ✅ Repositories (JobRepositoryImpl, CacheRepositoryImpl)
     - ✅ Domain services (JobScoringService, SkillExtractionService, JobMatchingService)
     - ✅ Mappers (JobMapper, JobORMMapper)
     - ✅ All 8 use cases

3. **Added dependency-injector to requirements.txt** ✅

### ⏳ Remaining Tasks

#### Task 1: Install Dependencies
```bash
cd Backend
pip install -r requirements.txt
```

#### Task 2: Update main.py to Initialize Container

**File:** `Backend/app/main.py`

**Add these imports:**
```python
from app.presentation.api.v1.dependencies import container, wire_container
```

**Add container initialization in startup event:**
```python
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    # Wire the DI container to router modules
    wire_container([
        "app.routers.jobs",
        "app.routers.auth",
        "app.routers.alerts",
        "app.routers.saved_jobs",
        "app.routers.stats",
        "app.routers.users",
    ])
    
    logger.info("Application started successfully")
```

**Add container cleanup in shutdown event:**
```python
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    from app.presentation.api.v1.dependencies import reset_container
    reset_container()
    logger.info("Application shutdown complete")
```

#### Task 3: Test DI Container

Create a test file to verify DI setup:

**File:** `Backend/tests/unit/test_di_container.py`

```python
import pytest
from app.presentation.api.v1.dependencies import container
from app.application.use_cases.jobs.create_job_use_case import CreateJobUseCase
from app.domain.services.job_scoring_service import JobScoringService


def test_container_provides_use_cases():
    """Test that container can provide use cases."""
    # This will fail if dependencies are not wired correctly
    use_case = container.create_job_use_case()
    assert use_case is not None
    assert isinstance(use_case, CreateJobUseCase)


def test_container_provides_domain_services():
    """Test that container can provide domain services."""
    service = container.job_scoring_service()
    assert service is not None
    assert isinstance(service, JobScoringService)


def test_singleton_services_are_reused():
    """Test that singleton services return same instance."""
    service1 = container.job_scoring_service()
    service2 = container.job_scoring_service()
    assert service1 is service2  # Same instance


def test_factory_use_cases_are_new():
    """Test that factory use cases return new instances."""
    use_case1 = container.create_job_use_case()
    use_case2 = container.create_job_use_case()
    assert use_case1 is not use_case2  # Different instances
```

---

## Phase 5: Thin Controllers 🚧 NEXT

### Overview
Refactor routers to use dependency injection and delegate all business logic to use cases.

### Goals
1. Remove business logic from controllers
2. Use DI to inject use cases
3. Keep only HTTP concerns in routers
4. Maintain backward compatibility

### Implementation Strategy

#### Step 1: Refactor Jobs Router (Example)

**File:** `Backend/app/routers/jobs.py`

**Before (Current):**
```python
from app.services.job_processing_service import JobProcessingService

@router.post("/scrape")
async def scrape_jobs(
    source: str,
    db: AsyncSession = Depends(get_db),
):
    # ❌ Business logic in controller
    job_processor = JobProcessingService(db)
    result = await job_processor.process_scraped_jobs(jobs_data, source)
    return result
```

**After (Clean Architecture):**
```python
from dependency_injector.wiring import inject, Provide
from app.presentation.api.v1.dependencies import Container
from app.application.use_cases.scraping import ProcessScrapedJobsUseCase

@router.post("/scrape")
@inject
async def scrape_jobs(
    source: str,
    jobs_data: List[Dict[str, Any]],
    use_case: ProcessScrapedJobsUseCase = Depends(
        Provide[Container.process_scraped_jobs_use_case]
    ),
):
    """
    Thin controller - only HTTP concerns.
    All business logic delegated to use case.
    """
    try:
        result = await use_case.execute(jobs_data, source)
        return {
            "success": True,
            "saved": result.saved_count,
            "duplicates": result.duplicate_count,
            "errors": result.error_count,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error scraping jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

#### Step 2: Refactor Search Endpoints

**Before:**
```python
@router.get("/search")
async def search_jobs(
    query: str,
    db: AsyncSession = Depends(get_db),
):
    search_service = SearchService(db)
    result = await search_service.search_jobs(user_id, query)
    return result
```

**After:**
```python
@router.get("/search")
@inject
async def search_jobs(
    query: str,
    skip: int = 0,
    limit: int = 20,
    use_case: SearchJobsUseCase = Depends(
        Provide[Container.search_jobs_use_case]
    ),
):
    try:
        result = await use_case.execute(query, skip, limit)
        return {
            "query": query,
            "results": result.jobs,
            "total": result.total_count,
            "has_more": result.has_more,
        }
    except Exception as e:
        logger.error(f"Error searching jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

#### Step 3: Refactor CRUD Endpoints

**Create Job:**
```python
@router.post("", response_model=JobResponse)
@inject
async def create_job(
    request: CreateJobRequest,
    use_case: CreateJobUseCase = Depends(
        Provide[Container.create_job_use_case]
    ),
):
    try:
        job = await use_case.execute(request)
        return JobResponse.from_entity(job)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**Get Job:**
```python
@router.get("/{job_id}", response_model=JobResponse)
@inject
async def get_job(
    job_id: UUID,
    use_case: GetJobDetailsUseCase = Depends(
        Provide[Container.get_job_details_use_case]
    ),
):
    try:
        job = await use_case.execute(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return JobResponse.from_entity(job)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**Update Job:**
```python
@router.put("/{job_id}", response_model=JobResponse)
@inject
async def update_job(
    job_id: UUID,
    request: UpdateJobRequest,
    use_case: UpdateJobUseCase = Depends(
        Provide[Container.update_job_use_case]
    ),
):
    try:
        job = await use_case.execute(job_id, request)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return JobResponse.from_entity(job)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**Delete Job:**
```python
@router.delete("/{job_id}", status_code=204)
@inject
async def delete_job(
    job_id: UUID,
    use_case: DeleteJobUseCase = Depends(
        Provide[Container.delete_job_use_case]
    ),
):
    try:
        success = await use_case.execute(job_id)
        if not success:
            raise HTTPException(status_code=404, detail="Job not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**List Jobs:**
```python
@router.get("", response_model=JobListResponse)
@inject
async def list_jobs(
    skip: int = 0,
    limit: int = 20,
    use_case: ListJobsUseCase = Depends(
        Provide[Container.list_jobs_use_case]
    ),
):
    try:
        result = await use_case.execute(skip, limit)
        return JobListResponse(
            jobs=[JobResponse.from_entity(job) for job in result.jobs],
            total=result.total_count,
            skip=skip,
            limit=limit,
            has_more=result.has_more,
        )
    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Checklist for Each Router

When refactoring a router, ensure:

- [ ] Import `@inject` decorator from `dependency_injector.wiring`
- [ ] Import `Provide` from `dependency_injector.wiring`
- [ ] Import `Container` from `app.presentation.api.v1.dependencies`
- [ ] Add `@inject` decorator to each endpoint
- [ ] Inject use case via `Depends(Provide[Container.use_case_name])`
- [ ] Remove manual service instantiation
- [ ] Remove business logic from controller
- [ ] Keep only HTTP concerns (request/response handling, status codes)
- [ ] Add proper error handling
- [ ] Add logging for errors
- [ ] Test endpoint still works

### Routers to Refactor (Priority Order)

1. **jobs.py** - Main router (highest priority)
2. **auth.py** - Authentication
3. **saved_jobs.py** - Saved jobs
4. **alerts.py** - Job alerts
5. **stats.py** - Statistics
6. **users.py** - User management

---

## Testing Strategy

### Unit Tests

**Test Use Cases:**
```python
@pytest.mark.asyncio
async def test_create_job_use_case():
    # Mock dependencies
    mock_repo = Mock(spec=IJobRepository)
    mock_mapper = Mock(spec=JobMapper)
    mock_scoring = Mock(spec=JobScoringService)
    
    # Create use case with mocks
    use_case = CreateJobUseCase(
        job_repository=mock_repo,
        job_mapper=mock_mapper,
        scoring_service=mock_scoring,
    )
    
    # Test execution
    result = await use_case.execute(test_data)
    
    # Verify
    assert result is not None
    mock_repo.save.assert_called_once()
```

### Integration Tests

**Test Endpoints:**
```python
@pytest.mark.asyncio
async def test_create_job_endpoint(client, test_db):
    response = await client.post(
        "/api/v1/jobs",
        json={
            "title": "Software Engineer",
            "company": "Tech Corp",
            # ... other fields
        }
    )
    
    assert response.status_code == 201
    assert response.json()["title"] == "Software Engineer"
```

---

## Migration Checklist

### Phase 4 Completion
- [x] Create presentation layer structure
- [x] Create DI container
- [x] Add dependency-injector to requirements
- [ ] Install dependencies
- [ ] Update main.py to initialize container
- [ ] Test DI container
- [ ] Verify all dependencies resolve

### Phase 5 Completion
- [ ] Refactor jobs.py router
- [ ] Refactor auth.py router
- [ ] Refactor saved_jobs.py router
- [ ] Refactor alerts.py router
- [ ] Refactor stats.py router
- [ ] Refactor users.py router
- [ ] Remove old service instantiations
- [ ] Test all endpoints
- [ ] Update API documentation

---

## Common Pitfalls to Avoid

### ❌ Don't Do This:

**1. Business Logic in Controller:**
```python
@router.post("/jobs")
async def create_job(job_data: dict):
    # ❌ Parsing in controller
    salary = Salary.from_string(job_data["salary"])
    
    # ❌ Validation in controller
    if salary.max_amount < 50000:
        raise HTTPException(400, "Salary too low")
    
    # ❌ Business logic in controller
    score = calculate_score(job_data)
```

**2. Direct Repository Access:**
```python
@router.get("/jobs/{id}")
async def get_job(id: UUID, db: Session = Depends(get_db)):
    # ❌ Direct repository access
    job_repo = JobRepository(db)
    job = await job_repo.get_by_id(id)
```

**3. Manual Service Instantiation:**
```python
@router.post("/search")
async def search(query: str, db: Session = Depends(get_db)):
    # ❌ Manual instantiation
    search_service = SearchService(db)
    result = await search_service.search(query)
```

### ✅ Do This Instead:

**1. Thin Controller:**
```python
@router.post("/jobs")
@inject
async def create_job(
    request: CreateJobRequest,
    use_case: CreateJobUseCase = Depends(Provide[Container.create_job_use_case]),
):
    try:
        job = await use_case.execute(request)
        return JobResponse.from_entity(job)
    except ValueError as e:
        raise HTTPException(400, str(e))
```

**2. Dependency Injection:**
```python
@router.get("/jobs/{id}")
@inject
async def get_job(
    id: UUID,
    use_case: GetJobDetailsUseCase = Depends(Provide[Container.get_job_details_use_case]),
):
    job = await use_case.execute(id)
    if not job:
        raise HTTPException(404, "Job not found")
    return JobResponse.from_entity(job)
```

---

## Success Criteria

### Phase 4 Complete When:
- [x] DI container created
- [x] All dependencies wired
- [ ] Container initialized in main.py
- [ ] All tests passing
- [ ] No circular dependencies

### Phase 5 Complete When:
- [ ] All routers refactored
- [ ] No business logic in controllers
- [ ] All endpoints use DI
- [ ] All tests passing
- [ ] API documentation updated

---

## Next Steps After Phase 5

### Phase 6: Testing & Cleanup
1. Write unit tests for domain layer (target 80%+ coverage)
2. Write unit tests for use cases
3. Write integration tests for endpoints
4. Delete deprecated services
5. Update all documentation
6. Performance testing
7. Security audit

---

**Status:** Phase 4 - 80% Complete | Phase 5 - Ready to Start  
**Next Action:** Install dependencies and update main.py

