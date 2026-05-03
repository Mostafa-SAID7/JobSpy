# 🚀 Next Steps Guide - Continue Refactoring

## Current Status
✅ **Phase 1 Complete**: Domain layer with value objects, entities, services, and interfaces
✅ **Phase 2 Started**: Application layer with first use case and mapper

---

## Immediate Next Steps (Priority Order)

### Step 1: Create Remaining Use Cases (2-3 hours)

#### A. Search Use Cases
Create `application/use_cases/search/search_jobs_use_case.py`:
```python
class SearchJobsUseCase:
    """
    Use Case: Search for jobs with filters.
    
    Replaces SearchService.search_jobs()
    """
    def __init__(
        self,
        job_repository: IJobRepository,
        cache_repository: ICacheRepository,
        scoring_service: JobScoringService,
    ):
        pass
    
    async def execute(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> SearchResult:
        # 1. Generate cache key
        # 2. Check cache
        # 3. If not cached, search repository
        # 4. Apply filters
        # 5. Score and rank results
        # 6. Cache results
        # 7. Return
        pass
```

#### B. Job Management Use Cases
Create these files:
- `application/use_cases/jobs/create_job_use_case.py`
- `application/use_cases/jobs/get_job_details_use_case.py`
- `application/use_cases/jobs/update_job_use_case.py`
- `application/use_cases/jobs/delete_job_use_case.py`

### Step 2: Create DTOs (1 hour)

Create `application/dto/job_dto.py`:
```python
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class JobDTO:
    """Data Transfer Object for Job"""
    id: str
    title: str
    company: str
    location: str
    description: str
    job_type: str
    experience_level: str
    salary_range: Optional[str]
    skills: List[str]
    source: str
    posted_date: datetime
    # ... other fields
```

Create `application/dto/search_dto.py`:
```python
@dataclass
class SearchRequestDTO:
    query: str
    location: Optional[str] = None
    job_type: Optional[str] = None
    salary_min: Optional[float] = None
    skip: int = 0
    limit: int = 20

@dataclass
class SearchResponseDTO:
    results: List[JobDTO]
    total_count: int
    has_more: bool
    page: int
```

### Step 3: Create Infrastructure Implementations (3-4 hours)

#### A. Repository Implementation
Create `infrastructure/persistence/sqlalchemy/repositories/job_repository_impl.py`:
```python
from app.domain.interfaces.repositories import IJobRepository
from app.domain.entities.job import Job

class JobRepositoryImpl(IJobRepository):
    """
    SQLAlchemy implementation of IJobRepository.
    
    Converts between ORM models and domain entities.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, job: Job) -> Job:
        # Convert domain entity to ORM model
        orm_model = self._to_orm(job)
        self.session.add(orm_model)
        await self.session.flush()
        # Convert back to domain entity
        return self._to_domain(orm_model)
    
    async def get_by_id(self, job_id: UUID) -> Optional[Job]:
        # Query ORM model
        # Convert to domain entity
        pass
    
    def _to_orm(self, job: Job) -> JobModel:
        """Convert domain entity to ORM model"""
        pass
    
    def _to_domain(self, orm_model: JobModel) -> Job:
        """Convert ORM model to domain entity"""
        pass
```

#### B. Cache Repository Implementation
Create `infrastructure/persistence/redis/cache_repository_impl.py`:
```python
from app.domain.interfaces.cache_repository import ICacheRepository

class CacheRepositoryImpl(ICacheRepository):
    """Redis implementation of ICacheRepository"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        return await self.redis.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        return await self.redis.set(key, value, ttl)
    
    # ... implement other methods
```

### Step 4: Set Up Dependency Injection (2 hours)

#### A. Install dependency-injector
```bash
pip install dependency-injector
```

#### B. Create DI Container
Create `presentation/api/v1/dependencies.py`:
```python
from dependency_injector import containers, providers
from app.domain.services.job_scoring_service import JobScoringService
from app.domain.services.skill_extraction_service import SkillExtractionService
from app.application.use_cases.scraping.process_scraped_jobs_use_case import ProcessScrapedJobsUseCase
from app.infrastructure.persistence.sqlalchemy.repositories.job_repository_impl import JobRepositoryImpl

class Container(containers.DeclarativeContainer):
    """Dependency Injection Container"""
    
    # Configuration
    config = providers.Configuration()
    
    # Database
    db_session = providers.Dependency()
    
    # Infrastructure - Repositories
    job_repository = providers.Factory(
        JobRepositoryImpl,
        session=db_session,
    )
    
    cache_repository = providers.Singleton(
        CacheRepositoryImpl,
    )
    
    # Domain Services
    scoring_service = providers.Factory(
        JobScoringService,
    )
    
    skill_service = providers.Factory(
        SkillExtractionService,
    )
    
    # Application - Mappers
    job_mapper = providers.Factory(
        JobMapper,
    )
    
    # Application - Use Cases
    process_scraped_jobs_use_case = providers.Factory(
        ProcessScrapedJobsUseCase,
        job_repository=job_repository,
        scoring_service=scoring_service,
        skill_service=skill_service,
        job_mapper=job_mapper,
    )
    
    search_jobs_use_case = providers.Factory(
        SearchJobsUseCase,
        job_repository=job_repository,
        cache_repository=cache_repository,
        scoring_service=scoring_service,
    )
```

### Step 5: Refactor Controllers (2-3 hours)

#### A. Update Router to Use DI
Update `presentation/api/v1/routers/jobs.py`:
```python
from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from app.presentation.api.v1.dependencies import Container
from app.application.use_cases.jobs.create_job_use_case import CreateJobUseCase

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])

@router.post("", response_model=JobResponse)
@inject
async def create_job(
    request: CreateJobRequest,
    use_case: CreateJobUseCase = Depends(Provide[Container.create_job_use_case]),
) -> JobResponse:
    """
    Thin controller - only HTTP concerns.
    All business logic in use case.
    """
    try:
        job = await use_case.execute(request)
        return JobResponse.from_entity(job)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

---

## Testing Strategy

### Unit Tests (Write These First!)

```python
# tests/unit/domain/test_value_objects.py
def test_salary_from_string():
    salary = Salary.from_string("$50,000 - $80,000")
    assert salary.min_amount == Decimal("50000")
    assert salary.max_amount == Decimal("80000")
    assert salary.currency == "USD"

def test_salary_validation():
    with pytest.raises(ValueError):
        Salary(Decimal("100000"), Decimal("50000"), "USD")  # min > max

# tests/unit/domain/test_entities.py
def test_job_creation():
    job = Job.create(
        title="Software Engineer",
        company="Tech Corp",
        location=Location.remote(),
        description="Great job",
        job_type=JobType.FULL_TIME,
        experience_level=ExperienceLevel.MID,
        source="LinkedIn",
        source_url="https://linkedin.com/jobs/123",
        posted_date=datetime.utcnow(),
    )
    assert job.is_remote() == True
    assert job.is_entry_level() == False

# tests/unit/domain/services/test_job_scoring_service.py
def test_job_scoring():
    job = create_test_job()
    scoring_service = JobScoringService()
    score = scoring_service.calculate_score(job)
    assert 0 <= score <= 100

# tests/unit/application/test_use_cases.py
@pytest.mark.asyncio
async def test_process_scraped_jobs():
    # Mock dependencies
    mock_repo = Mock(spec=IJobRepository)
    mock_repo.exists_by_url.return_value = False
    mock_repo.save.return_value = create_test_job()
    
    scoring_service = JobScoringService()
    skill_service = SkillExtractionService()
    job_mapper = JobMapper()
    
    use_case = ProcessScrapedJobsUseCase(
        job_repository=mock_repo,
        scoring_service=scoring_service,
        skill_service=skill_service,
        job_mapper=job_mapper,
    )
    
    result = await use_case.execute([test_job_data], "LinkedIn")
    
    assert result.saved_count == 1
    assert result.duplicate_count == 0
    assert result.error_count == 0
```

---

## Migration Strategy (Gradual Rollout)

### Phase 1: Parallel Implementation
1. Keep old code running
2. Add new architecture alongside
3. Route some traffic to new code
4. Compare results

### Phase 2: Gradual Migration
1. Migrate one endpoint at a time
2. Start with least critical endpoints
3. Monitor for issues
4. Roll back if needed

### Phase 3: Complete Migration
1. All endpoints using new architecture
2. Remove old code
3. Celebrate! 🎉

---

## Checklist for Each Use Case

When creating a new use case, ensure:

- [ ] Single responsibility (one clear purpose)
- [ ] Depends on interfaces, not implementations
- [ ] No infrastructure dependencies
- [ ] Clear input/output types
- [ ] Comprehensive error handling
- [ ] Logging for debugging
- [ ] Unit tests written
- [ ] Integration tests written
- [ ] Documentation complete

---

## Common Pitfalls to Avoid

### ❌ Don't Do This:
```python
# Business logic in controller
@router.post("/jobs")
async def create_job(job_data: dict, db: Session = Depends(get_db)):
    # ❌ Parsing in controller
    salary = Salary.from_string(job_data["salary"])
    
    # ❌ Business logic in controller
    if salary.max_amount < 50000:
        raise HTTPException(400, "Salary too low")
    
    # ❌ Direct repository access
    job_repo = JobRepository(db)
    job = job_repo.create(job_data)
```

### ✅ Do This Instead:
```python
# Thin controller, use case handles everything
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

---

## Resources

### Documentation to Write
1. API documentation (OpenAPI/Swagger)
2. Architecture decision records (ADRs)
3. Developer onboarding guide
4. Deployment guide

### Tools to Use
- **pytest**: Unit and integration testing
- **pytest-asyncio**: Async test support
- **pytest-cov**: Code coverage
- **black**: Code formatting
- **mypy**: Type checking
- **dependency-injector**: DI framework

---

## Success Metrics

Track these metrics to measure progress:

- [ ] All services < 200 lines
- [ ] No business logic in controllers
- [ ] 80%+ test coverage
- [ ] All magic numbers eliminated
- [ ] Zero god classes
- [ ] Full dependency injection
- [ ] All existing tests passing
- [ ] Performance maintained or improved

---

## Questions to Ask Yourself

Before committing code, ask:

1. **Single Responsibility**: Does this class/function do ONE thing?
2. **Dependency Inversion**: Am I depending on abstractions, not concretions?
3. **Testability**: Can I easily unit test this?
4. **Readability**: Will another developer understand this in 6 months?
5. **No Magic**: Are all constants and configurations explicit?

---

## Timeline Estimate

- **Week 1**: Complete Phase 2 (use cases, DTOs)
- **Week 2**: Complete Phase 3 (infrastructure implementations)
- **Week 3**: Complete Phase 4 (dependency injection)
- **Week 4**: Complete Phase 5 (thin controllers)
- **Week 5**: Testing and bug fixes
- **Week 6**: Documentation and deployment

**Total**: 6 weeks for complete refactoring

---

## Need Help?

Refer to these files:
- `IMPLEMENTATION_SUMMARY.md` - What we've built
- `REFACTORING_PROGRESS.md` - Current progress
- `Backend/app/domain/` - Domain layer examples
- `Backend/app/application/` - Application layer examples

---

**Remember**: 
- Take it one step at a time
- Write tests first
- Keep existing functionality working
- Refactor incrementally
- Celebrate small wins!

🚀 **You've got this!**
