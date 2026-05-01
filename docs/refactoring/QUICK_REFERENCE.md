# 🚀 Quick Reference Guide - Backend Refactoring

## 📊 Current Status (2026-05-01)

**Progress:** 70% Complete (3.8 of 5 phases)

| Phase | Status | Progress |
|-------|--------|----------|
| 1. Domain Layer | ✅ Complete | 100% |
| 2. Application Layer | ✅ Complete | 100% |
| 3. Infrastructure Layer | ✅ Complete | 100% |
| 4. Dependency Injection | 🚧 In Progress | 80% |
| 5. Thin Controllers | ⏳ Pending | 0% |
| 6. Testing & Cleanup | ⏳ Pending | 0% |

---

## 📁 New Architecture Structure

```
Backend/app/
├── domain/                      # ✅ Pure business logic
│   ├── entities/job.py
│   ├── value_objects/
│   │   ├── salary.py
│   │   ├── location.py
│   │   ├── job_type.py
│   │   └── experience_level.py
│   ├── services/
│   │   ├── job_scoring_service.py
│   │   ├── skill_extraction_service.py
│   │   └── job_matching_service.py
│   └── interfaces/
│       ├── repositories.py
│       └── cache_repository.py
│
├── application/                 # ✅ Use cases & orchestration
│   ├── use_cases/
│   │   ├── jobs/               # CRUD operations
│   │   ├── search/             # Search operations
│   │   └── scraping/           # Scraping operations
│   ├── dto/                    # Data transfer objects
│   └── mappers/                # Data conversion
│
├── infrastructure/              # ✅ External concerns
│   └── persistence/
│       ├── sqlalchemy/
│       │   ├── repositories/
│       │   └── mappers/
│       └── redis/
│
├── presentation/                # ✅ API layer (NEW!)
│   └── api/v1/
│       ├── dependencies.py     # DI Container
│       └── deps.py             # FastAPI deps
│
└── shared/                      # ✅ Cross-cutting
    └── exceptions/
```

---

## 🔧 How to Use New Architecture

### 1. Using Use Cases (Application Layer)

**Example: Process Scraped Jobs**

```python
from app.application.use_cases.scraping import ProcessScrapedJobsUseCase
from app.presentation.api.v1.dependencies import container

# Get use case from DI container
use_case = container.process_scraped_jobs_use_case()

# Execute use case
result = await use_case.execute(jobs_data, "LinkedIn")

print(f"Saved: {result.saved_count}")
print(f"Duplicates: {result.duplicate_count}")
print(f"Errors: {result.error_count}")
```

### 2. Using Domain Services

**Example: Calculate Job Score**

```python
from app.domain.services import JobScoringService
from app.domain.entities import Job

scoring_service = JobScoringService()
score = scoring_service.calculate_score(job)
```

### 3. Using Value Objects

**Example: Working with Salary**

```python
from app.domain.value_objects import Salary
from decimal import Decimal

# Create salary
salary = Salary(
    min_amount=Decimal("50000"),
    max_amount=Decimal("80000"),
    currency="USD"
)

# Use salary methods
if salary.meets_minimum(Decimal("60000")):
    print("Salary meets minimum requirement")

# Format for display
print(salary.format())  # "$50,000 - $80,000"
```

---

## 🎯 Quick Commands

### Install Dependencies
```bash
cd Backend
pip install -r requirements.txt
```

### Run Tests
```bash
# All tests
pytest Backend/tests/

# Unit tests only
pytest Backend/tests/unit/

# With coverage
pytest Backend/tests/ --cov=app --cov-report=html
```

### Run Application
```bash
cd Backend
uvicorn app.main:app --reload
```

---

## 📝 Common Tasks

### Task 1: Add a New Use Case

1. **Create use case file:**
   ```
   Backend/app/application/use_cases/[category]/[name]_use_case.py
   ```

2. **Implement use case:**
   ```python
   class MyNewUseCase:
       def __init__(
           self,
           job_repository: IJobRepository,
           # ... other dependencies
       ):
           self.job_repository = job_repository
       
       async def execute(self, params):
           # Implementation
           pass
   ```

3. **Add to DI container:**
   ```python
   # In presentation/api/v1/dependencies.py
   my_new_use_case = providers.Factory(
       MyNewUseCase,
       job_repository=job_repository,
   )
   ```

4. **Use in router:**
   ```python
   @router.post("/endpoint")
   @inject
   async def endpoint(
       use_case: MyNewUseCase = Depends(
           Provide[Container.my_new_use_case]
       ),
   ):
       result = await use_case.execute(params)
       return result
   ```

### Task 2: Add a New Domain Service

1. **Create service file:**
   ```
   Backend/app/domain/services/[name]_service.py
   ```

2. **Implement service:**
   ```python
   class MyDomainService:
       def __init__(self, config: Optional[Config] = None):
           self.config = config or Config()
       
       def do_something(self, entity):
           # Business logic
           pass
   ```

3. **Add to DI container:**
   ```python
   my_domain_service = providers.Singleton(
       MyDomainService,
   )
   ```

### Task 3: Add a New Value Object

1. **Create value object file:**
   ```
   Backend/app/domain/value_objects/[name].py
   ```

2. **Implement value object:**
   ```python
   from dataclasses import dataclass
   
   @dataclass(frozen=True)
   class MyValueObject:
       field1: str
       field2: int
       
       def __post_init__(self):
           # Validation
           if not self.field1:
               raise ValueError("field1 is required")
       
       def some_method(self):
           # Business logic
           pass
   ```

---

## 🚫 What NOT to Do

### ❌ Don't Put Business Logic in Controllers
```python
# BAD
@router.post("/jobs")
async def create_job(job_data: dict):
    # ❌ Business logic in controller
    if job_data["salary"] < 50000:
        raise HTTPException(400, "Salary too low")
    
    score = calculate_score(job_data)  # ❌
    job = Job(**job_data)  # ❌
```

### ❌ Don't Access Infrastructure from Domain
```python
# BAD
class Job:
    def save(self):
        # ❌ Domain entity accessing database
        db.session.add(self)
        db.session.commit()
```

### ❌ Don't Mix Concerns
```python
# BAD
class JobRepository:
    async def get_by_id(self, job_id):
        # ❌ Caching in repository
        cached = await redis.get(f"job:{job_id}")
        if cached:
            return cached
        
        job = await self.db.query(Job).filter_by(id=job_id).first()
        await redis.set(f"job:{job_id}", job)
        return job
```

---

## ✅ What TO Do

### ✅ Use Dependency Injection
```python
# GOOD
@router.post("/jobs")
@inject
async def create_job(
    request: CreateJobRequest,
    use_case: CreateJobUseCase = Depends(
        Provide[Container.create_job_use_case]
    ),
):
    job = await use_case.execute(request)
    return JobResponse.from_entity(job)
```

### ✅ Keep Domain Pure
```python
# GOOD
class Job:
    def is_remote(self) -> bool:
        """Business logic in domain entity."""
        return self.location.is_remote()
    
    def matches_skills(self, required_skills: List[str]) -> bool:
        """Business logic in domain entity."""
        return any(skill in self.skills for skill in required_skills)
```

### ✅ Separate Concerns
```python
# GOOD - Caching in use case
class GetJobDetailsUseCase:
    async def execute(self, job_id: UUID):
        # Check cache
        cached = await self.cache_repository.get(f"job:{job_id}")
        if cached:
            return cached
        
        # Get from repository
        job = await self.job_repository.get_by_id(job_id)
        
        # Cache result
        await self.cache_repository.set(f"job:{job_id}", job)
        
        return job
```

---

## 📚 Documentation

### Main Documents
- `CURRENT_STATUS_REPORT.md` - Detailed status
- `PHASE_4_AND_5_GUIDE.md` - Implementation guide
- `REFACTORING_PROGRESS.md` - Progress tracking
- `SESSION_SUMMARY.md` - Latest session summary

### Code Documentation
- All files have comprehensive docstrings
- Type hints throughout
- Examples in docstrings

---

## 🆘 Need Help?

### Common Issues

**Issue: Circular dependency error**
- Check import order
- Use `TYPE_CHECKING` for type hints
- Ensure interfaces are in domain layer

**Issue: DI container not resolving**
- Check container is wired in main.py
- Verify all dependencies are registered
- Check for typos in provider names

**Issue: Tests failing**
- Mock all dependencies
- Use `pytest-asyncio` for async tests
- Check test database is set up

### Where to Look

- **Architecture questions:** `REFACTORING_PROGRESS.md`
- **Implementation help:** `PHASE_4_AND_5_GUIDE.md`
- **Current status:** `CURRENT_STATUS_REPORT.md`
- **Migration guide:** `services/DEPRECATION_NOTICE.md`

---

## 🎯 Next Steps

1. **Complete Phase 4:**
   - Install dependencies
   - Update main.py
   - Test DI container

2. **Start Phase 5:**
   - Refactor jobs.py router
   - Refactor other routers
   - Remove old service instantiations

3. **Phase 6:**
   - Write tests
   - Delete deprecated code
   - Update documentation

---

**Last Updated:** 2026-05-01  
**Status:** Phase 4 - 80% Complete  
**Next:** Complete Phase 4, Start Phase 5

