# وثيقة التصميم - تحويل JobSpy إلى تطبيق ويب

## المقدمة

هذه وثيقة التصميم الشاملة لتحويل أداة JobSpy CLI إلى تطبيق ويب متكامل وجاهز للإنتاج.



## نظرة عامة على المعمارية

### الهدف
تحويل مكتبة JobSpy CLI إلى تطبيق ويب متكامل يوفر:
- واجهة برمجية REST (FastAPI)
- واجهة مستخدم حديثة (Vue.js)
- نظام إدارة المستخدمين والمصادقة
- نظام التنبيهات والإشعارات
- نظام التخزين المؤقت والأداء العالية

### المكونات الرئيسية

```
┌─────────────────────────────────────────────────────────────┐
│                    طبقة العرض (Frontend)                    │
│                      Vue.js + Pinia                         │
│  (صفحات البحث، الحفظ، التنبيهات، الملف الشخصي)              │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/HTTPS
┌────────────────────────▼────────────────────────────────────┐
│                  طبقة الواجهة البرمجية                       │
│                    FastAPI + Uvicorn                        │
│  (المصادقة، البحث، الحفظ، التنبيهات، التصدير)              │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌──────▼──────┐  ┌────▼────────┐
│  PostgreSQL  │  │    Redis    │  │   Celery    │
│   (البيانات) │  │  (التخزين)  │  │  (الوظائف)  │
└──────────────┘  └─────────────┘  └─────────────┘
        │
┌───────▼──────────────────────────────────────┐
│      محرك الكشط (JobSpy Library)             │
│  (LinkedIn, Indeed, Glassdoor, وغيرها)      │
└────────────────────────────────────────────────┘
```

### تدفق البيانات الرئيسي

1. **البحث عن الوظائف**:
   - المستخدم يدخل معايير البحث في الواجهة
   - الطلب يُرسل إلى FastAPI
   - يتم التحقق من الذاكرة المؤقتة (Redis)
   - إذا لم توجد النتائج، يتم تشغيل مهمة Celery
   - محرك الكشط يقوم بكشط المنصات بشكل متزامن
   - النتائج تُحفظ في قاعدة البيانات والذاكرة المؤقتة
   - النتائج تُعاد إلى الواجهة

2. **حفظ الوظائف**:
   - المستخدم ينقر على زر الحفظ
   - الطلب يُرسل إلى FastAPI مع معرف الوظيفة
   - يتم التحقق من أن الوظيفة لم تُحفظ من قبل
   - الوظيفة تُحفظ في قاعدة البيانات
   - رسالة تأكيد تُعاد إلى الواجهة

3. **التنبيهات**:
   - المستخدم ينشئ تنبيهاً لبحث محفوظ
   - مهمة Celery تُشغل كل ساعة
   - يتم البحث عن وظائف جديدة
   - إذا وُجدت وظائف جديدة، يتم إرسال بريد إلكتروني
   - الوظائف الجديدة تُحفظ في قاعدة البيانات



## معمارية الخادم (Backend Architecture)

### هيكل المشروع

```
jobspy-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # نقطة الدخول الرئيسية
│   ├── config.py               # إعدادات التطبيق
│   ├── dependencies.py         # التبعيات المشتركة
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py         # نقاط نهاية المصادقة
│   │   │   ├── search.py       # نقاط نهاية البحث
│   │   │   ├── jobs.py         # نقاط نهاية الوظائف
│   │   │   ├── saved_jobs.py   # نقاط نهاية الحفظ
│   │   │   ├── alerts.py       # نقاط نهاية التنبيهات
│   │   │   └── export.py       # نقاط نهاية التصدير
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # نموذج المستخدم
│   │   ├── job.py              # نموذج الوظيفة
│   │   ├── saved_job.py        # نموذج الوظيفة المحفوظة
│   │   ├── search.py           # نموذج البحث
│   │   └── alert.py            # نموذج التنبيه
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py             # Pydantic schemas للمستخدم
│   │   ├── job.py              # Pydantic schemas للوظيفة
│   │   ├── search.py           # Pydantic schemas للبحث
│   │   └── alert.py            # Pydantic schemas للتنبيه
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py     # خدمة المصادقة
│   │   ├── search_service.py   # خدمة البحث
│   │   ├── job_service.py      # خدمة الوظائف
│   │   ├── alert_service.py    # خدمة التنبيهات
│   │   └── export_service.py   # خدمة التصدير
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── user_repo.py        # مستودع المستخدمين
│   │   ├── job_repo.py         # مستودع الوظائف
│   │   ├── saved_job_repo.py   # مستودع الوظائف المحفوظة
│   │   ├── search_repo.py      # مستودع البحث
│   │   └── alert_repo.py       # مستودع التنبيهات
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── scraping_tasks.py   # مهام الكشط
│   │   ├── alert_tasks.py      # مهام التنبيهات
│   │   └── cleanup_tasks.py    # مهام التنظيف
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── security.py         # أدوات الأمان
│   │   ├── cache.py            # أدوات التخزين المؤقت
│   │   ├── email.py            # أدوات البريد الإلكتروني
│   │   └── validators.py       # أدوات التحقق
│   └── middleware/
│       ├── __init__.py
│       ├── auth.py             # middleware المصادقة
│       ├── error_handler.py    # معالج الأخطاء
│       └── rate_limiter.py     # معدل التحديد
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── migrations/
│   └── alembic/
├── requirements.txt
├── .env.example
└── docker-compose.yml
```

### نقاط النهاية (Endpoints)

#### المصادقة (Authentication)

```
POST /api/v1/auth/register
  Request:
    {
      "email": "user@example.com",
      "password": "secure_password",
      "full_name": "User Name"
    }
  Response:
    {
      "user_id": "uuid",
      "email": "user@example.com",
      "full_name": "User Name",
      "created_at": "2024-01-01T00:00:00Z"
    }

POST /api/v1/auth/login
  Request:
    {
      "email": "user@example.com",
      "password": "secure_password"
    }
  Response:
    {
      "access_token": "jwt_token",
      "refresh_token": "refresh_token",
      "token_type": "bearer",
      "expires_in": 3600
    }

POST /api/v1/auth/refresh
  Request:
    {
      "refresh_token": "refresh_token"
    }
  Response:
    {
      "access_token": "new_jwt_token",
      "expires_in": 3600
    }
```

#### البحث (Search)

```
POST /api/v1/search
  Request:
    {
      "search_term": "Python Developer",
      "location": "San Francisco",
      "job_type": "fulltime",
      "distance": 50,
      "is_remote": false,
      "results_wanted": 100,
      "hours_old": 24,
      "site_name": ["linkedin", "indeed", "glassdoor"]
    }
  Response:
    {
      "search_id": "uuid",
      "status": "processing",
      "created_at": "2024-01-01T00:00:00Z"
    }

GET /api/v1/search/{search_id}
  Response:
    {
      "search_id": "uuid",
      "status": "completed",
      "results": [
        {
          "job_id": "uuid",
          "title": "Python Developer",
          "company": "Tech Company",
          "location": "San Francisco, CA",
          "job_url": "https://...",
          "salary_min": 100000,
          "salary_max": 150000,
          "job_type": "fulltime",
          "description": "...",
          "posted_date": "2024-01-01T00:00:00Z",
          "site_name": "linkedin",
          "is_remote": false
        }
      ],
      "total_results": 150,
      "execution_time_ms": 25000
    }
```

#### الوظائف المحفوظة (Saved Jobs)

```
POST /api/v1/saved-jobs
  Request:
    {
      "job_id": "uuid",
      "notes": "Interesting position"
    }
  Response:
    {
      "saved_job_id": "uuid",
      "job_id": "uuid",
      "saved_at": "2024-01-01T00:00:00Z"
    }

GET /api/v1/saved-jobs
  Query Parameters:
    - page: 1
    - page_size: 20
    - sort_by: saved_at (or title, company, salary_max)
    - sort_order: desc (or asc)
  Response:
    {
      "total": 50,
      "page": 1,
      "page_size": 20,
      "items": [
        {
          "saved_job_id": "uuid",
          "job": { ... },
          "notes": "Interesting position",
          "saved_at": "2024-01-01T00:00:00Z"
        }
      ]
    }

DELETE /api/v1/saved-jobs/{saved_job_id}
  Response:
    {
      "message": "Job removed from saved list"
    }
```

#### التنبيهات (Alerts)

```
POST /api/v1/alerts
  Request:
    {
      "search_id": "uuid",
      "frequency": "hourly",
      "is_active": true
    }
  Response:
    {
      "alert_id": "uuid",
      "search_id": "uuid",
      "frequency": "hourly",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }

GET /api/v1/alerts
  Response:
    {
      "total": 5,
      "items": [
        {
          "alert_id": "uuid",
          "search": { ... },
          "frequency": "hourly",
          "is_active": true,
          "last_checked": "2024-01-01T12:00:00Z",
          "created_at": "2024-01-01T00:00:00Z"
        }
      ]
    }

PUT /api/v1/alerts/{alert_id}
  Request:
    {
      "frequency": "daily",
      "is_active": false
    }
  Response:
    {
      "alert_id": "uuid",
      "frequency": "daily",
      "is_active": false,
      "updated_at": "2024-01-01T00:00:00Z"
    }

DELETE /api/v1/alerts/{alert_id}
  Response:
    {
      "message": "Alert deleted"
    }
```

#### التصدير (Export)

```
POST /api/v1/export
  Request:
    {
      "search_id": "uuid",
      "format": "csv" (or "excel", "json"),
      "include_fields": ["title", "company", "location", "salary_min", "salary_max"]
    }
  Response:
    {
      "export_id": "uuid",
      "status": "processing",
      "format": "csv",
      "created_at": "2024-01-01T00:00:00Z"
    }

GET /api/v1/export/{export_id}
  Response:
    {
      "export_id": "uuid",
      "status": "completed",
      "download_url": "https://s3.amazonaws.com/...",
      "file_size": 1024000,
      "created_at": "2024-01-01T00:00:00Z"
    }
```



## نماذج البيانات (Data Models)

### Pydantic Schemas

#### نموذج المستخدم (User)

```python
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserResponse(UserBase):
    user_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

#### نموذج الوظيفة (Job)

```python
class JobBase(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    job_url: str
    description: Optional[str] = None
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    job_type: JobType  # Enum: fulltime, parttime, internship, contract
    is_remote: bool = False
    posted_date: datetime
    site_name: str

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    job_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

#### نموذج البحث (Search)

```python
class SearchBase(BaseModel):
    search_term: str
    location: Optional[str] = None
    job_type: Optional[JobType] = None
    distance: Optional[int] = None
    is_remote: Optional[bool] = None
    results_wanted: int = 100
    hours_old: int = 24
    site_names: List[str] = []

class SearchCreate(SearchBase):
    pass

class SearchResponse(SearchBase):
    search_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

#### نموذج التنبيه (Alert)

```python
class AlertBase(BaseModel):
    search_id: UUID
    frequency: AlertFrequency  # Enum: hourly, daily, weekly
    is_active: bool = True

class AlertCreate(AlertBase):
    pass

class AlertUpdate(BaseModel):
    frequency: Optional[AlertFrequency] = None
    is_active: Optional[bool] = None

class AlertResponse(AlertBase):
    alert_id: UUID
    user_id: UUID
    last_checked: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

### مخطط قاعدة البيانات (Database Schema)

```sql
-- جدول المستخدمين
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_created_at (created_at)
);

-- جدول الوظائف
CREATE TABLE jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    job_url TEXT UNIQUE NOT NULL,
    description TEXT,
    salary_min DECIMAL(10, 2),
    salary_max DECIMAL(10, 2),
    job_type VARCHAR(50) NOT NULL,
    is_remote BOOLEAN DEFAULT FALSE,
    posted_date TIMESTAMP NOT NULL,
    site_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_title (title),
    INDEX idx_company (company),
    INDEX idx_location (location),
    INDEX idx_site_name (site_name),
    INDEX idx_posted_date (posted_date),
    INDEX idx_job_url (job_url)
);

-- جدول الوظائف المحفوظة
CREATE TABLE saved_jobs (
    saved_job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    notes TEXT,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, job_id),
    INDEX idx_user_id (user_id),
    INDEX idx_job_id (job_id),
    INDEX idx_saved_at (saved_at)
);

-- جدول البحث المحفوظ
CREATE TABLE saved_searches (
    search_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    search_term VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    job_type VARCHAR(50),
    distance INTEGER,
    is_remote BOOLEAN,
    site_names TEXT[] DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- جدول التنبيهات
CREATE TABLE alerts (
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    search_id UUID NOT NULL REFERENCES saved_searches(search_id) ON DELETE CASCADE,
    frequency VARCHAR(50) NOT NULL DEFAULT 'daily',
    is_active BOOLEAN DEFAULT TRUE,
    last_checked TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_search_id (search_id),
    INDEX idx_is_active (is_active)
);

-- جدول سجل البحث
CREATE TABLE search_history (
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    search_term VARCHAR(255),
    location VARCHAR(255),
    results_count INTEGER,
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- جدول نتائج البحث (للتخزين المؤقت)
CREATE TABLE search_results (
    result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    search_id UUID NOT NULL REFERENCES saved_searches(search_id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_search_id (search_id),
    INDEX idx_job_id (job_id)
);

-- جدول التصديرات
CREATE TABLE exports (
    export_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    search_id UUID REFERENCES saved_searches(search_id) ON DELETE SET NULL,
    format VARCHAR(50) NOT NULL,
    file_url TEXT,
    file_size INTEGER,
    status VARCHAR(50) DEFAULT 'processing',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);
```

### استراتيجية الفهرسة (Indexing Strategy)

1. **الفهارس الأساسية**: جميع المفاتيح الأجنبية والأساسية
2. **فهارس البحث**: على الحقول المستخدمة في WHERE clauses
3. **فهارس الترتيب**: على الحقول المستخدمة في ORDER BY
4. **فهارس التصفية**: على الحقول المستخدمة في التصفية المتكررة
5. **فهارس التاريخ**: على created_at و updated_at للاستعلامات الزمنية

### استراتيجية التخزين المؤقت (Caching Strategy)

#### مفاتيح Redis

```
# نتائج البحث
search_results:{search_id} -> JSON (TTL: 1 hour)

# الوظائف المحفوظة
user_saved_jobs:{user_id} -> List[job_id] (TTL: 24 hours)

# معلومات المستخدم
user_profile:{user_id} -> JSON (TTL: 24 hours)

# التنبيهات النشطة
active_alerts -> List[alert_id] (TTL: 1 hour)

# معلومات الوظيفة
job_details:{job_id} -> JSON (TTL: 7 days)

# قائمة المنصات المدعومة
supported_sites -> List[str] (TTL: 30 days)
```

#### سياسات TTL

- نتائج البحث: 1 ساعة
- معلومات المستخدم: 24 ساعة
- الوظائف المحفوظة: 24 ساعة
- معلومات الوظيفة: 7 أيام
- البيانات الثابتة: 30 يوم

#### استراتيجية إلغاء التخزين المؤقت

- عند حفظ وظيفة: إلغاء `user_saved_jobs:{user_id}`
- عند حذف وظيفة: إلغاء `user_saved_jobs:{user_id}`
- عند تحديث التنبيه: إلغاء `active_alerts`
- عند انتهاء صلاحية البحث: إلغاء `search_results:{search_id}`



## معمارية الواجهة الأمامية (Frontend Architecture)

### هيكل المشروع Vue.js

```
jobspy-frontend/
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── components/
│   │   ├── SearchForm.vue
│   │   ├── JobCard.vue
│   │   ├── JobDetails.vue
│   │   ├── SavedJobsList.vue
│   │   ├── AlertsList.vue
│   │   ├── ExportModal.vue
│   │   └── Pagination.vue
│   ├── pages/
│   │   ├── LoginPage.vue
│   │   ├── RegisterPage.vue
│   │   ├── SearchPage.vue
│   │   ├── SavedJobsPage.vue
│   │   ├── AlertsPage.vue
│   │   ├── ProfilePage.vue
│   │   └── NotFoundPage.vue
│   ├── stores/
│   │   ├── auth.ts          # Pinia store للمصادقة
│   │   ├── search.ts        # Pinia store للبحث
│   │   ├── jobs.ts          # Pinia store للوظائف
│   │   ├── alerts.ts        # Pinia store للتنبيهات
│   │   └── ui.ts            # Pinia store لحالة الواجهة
│   ├── services/
│   │   ├── api.ts           # عميل HTTP
│   │   ├── auth.ts          # خدمة المصادقة
│   │   ├── search.ts        # خدمة البحث
│   │   ├── jobs.ts          # خدمة الوظائف
│   │   └── alerts.ts        # خدمة التنبيهات
│   ├── router/
│   │   └── index.ts         # تكوين الموجه
│   ├── utils/
│   │   ├── validators.ts
│   │   ├── formatters.ts
│   │   └── constants.ts
│   └── styles/
│       ├── main.css
│       ├── variables.css
│       └── components.css
├── public/
├── package.json
└── vite.config.ts
```

### مخطط المكونات (Component Tree)

```
App
├── Router
│   ├── LoginPage
│   │   ├── LoginForm
│   │   └── RegisterLink
│   ├── RegisterPage
│   │   ├── RegisterForm
│   │   └── LoginLink
│   ├── SearchPage
│   │   ├── SearchForm
│   │   ├── FilterPanel
│   │   ├── ResultsList
│   │   │   └── JobCard (repeated)
│   │   ├── Pagination
│   │   └── ExportModal
│   ├── SavedJobsPage
│   │   ├── SavedJobsList
│   │   │   └── SavedJobCard (repeated)
│   │   └── Pagination
│   ├── AlertsPage
│   │   ├── AlertsList
│   │   │   └── AlertCard (repeated)
│   │   └── CreateAlertModal
│   └── ProfilePage
│       ├── UserInfo
│       ├── ChangePassword
│       └── Preferences
└── Navigation
    ├── Header
    │   ├── Logo
    │   ├── SearchBar
    │   └── UserMenu
    └── Sidebar
        ├── NavLinks
        └── UserProfile
```

### إدارة الحالة (State Management with Pinia)

```typescript
// stores/auth.ts
export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    accessToken: null,
    refreshToken: null,
    isAuthenticated: false,
    isLoading: false,
    error: null
  }),
  
  getters: {
    isLoggedIn: (state) => state.isAuthenticated,
    currentUser: (state) => state.user
  },
  
  actions: {
    async login(email, password) { ... },
    async register(email, password, fullName) { ... },
    async logout() { ... },
    async refreshAccessToken() { ... }
  }
})

// stores/search.ts
export const useSearchStore = defineStore('search', {
  state: () => ({
    searchResults: [],
    currentSearch: null,
    isLoading: false,
    error: null,
    filters: {
      jobType: null,
      salaryMin: null,
      salaryMax: null,
      location: null,
      isRemote: false
    },
    pagination: {
      page: 1,
      pageSize: 20,
      total: 0
    }
  }),
  
  actions: {
    async performSearch(criteria) { ... },
    setFilters(filters) { ... },
    clearFilters() { ... },
    goToPage(page) { ... }
  }
})
```

### تدفق البيانات (Data Flow)

```
User Input (SearchForm)
    ↓
Dispatch Action (useSearchStore.performSearch)
    ↓
API Call (services/search.ts)
    ↓
Backend Response
    ↓
Update Store State
    ↓
Component Re-render (ResultsList)
    ↓
Display Results (JobCard components)
```



## خصائص الصحة (Correctness Properties)

*الخاصية هي سمة أو سلوك يجب أن يكون صحيحاً عبر جميع عمليات التنفيذ الصحيحة للنظام - بشكل أساسي، بيان رسمي حول ما يجب أن يفعله النظام. تخدم الخصائص كجسر بين المواصفات القابلة للقراءة من قبل الإنسان وضمانات الصحة القابلة للتحقق من قبل الآلة.*

### Property 1: البحث يعيد نتائج من جميع المنصات المحددة

*لأي معايير بحث صحيحة وقائمة منصات محددة، يجب أن تحتوي النتائج على وظائف من جميع المنصات المحددة (أو رسالة خطأ واضحة إذا فشلت منصة معينة)*

**Validates: Requirements 1.1, 2.2, 2.4**

### Property 2: جميع نتائج البحث تحتوي على الحقول المطلوبة

*لأي نتيجة بحث، يجب أن تحتوي على جميع الحقول المطلوبة: title, company, location, job_url, salary_min, salary_max, job_type, description, posted_date, site_name*

**Validates: Requirements 1.4**

### Property 3: معرف المنصة يُحفظ بشكل صحيح

*لأي وظيفة مكشوطة من منصة معينة، يجب أن يكون site_name مساوياً لمعرف المنصة الصحيح*

**Validates: Requirements 2.3**

### Property 4: تصفية الراتب تعيد النتائج الصحيحة

*لأي مجموعة من الوظائف وأي نطاق راتب محدد، يجب أن تحتوي النتائج المصفاة على وظائف فقط حيث salary_min >= min_requested و salary_max <= max_requested*

**Validates: Requirements 3.2**

### Property 5: تصفية الموقع تعيد النتائج الصحيحة

*لأي مجموعة من الوظائف وأي موقع محدد، يجب أن تحتوي النتائج المصفاة على وظائف فقط من الموقع المحدد*

**Validates: Requirements 3.3**

### Property 6: تصفية المسافة تعيد النتائج الصحيحة

*لأي مجموعة من الوظائف وأي موقع مركزي ومسافة محددة، يجب أن تحتوي النتائج المصفاة على وظائف فقط ضمن المسافة المحددة*

**Validates: Requirements 3.4**

### Property 7: البريد الإلكتروني يجب أن يكون فريداً

*لأي بريد إلكتروني محدد، يجب ألا يكون هناك حسابان بنفس البريد الإلكتروني في قاعدة البيانات*

**Validates: Requirements 4.2**

### Property 8: كلمة المرور مشفرة بشكل صحيح

*لأي كلمة مرور مدخلة، يجب ألا تُخزن بصيغة نصية في قاعدة البيانات، بل يجب أن تكون مشفرة باستخدام bcrypt*

**Validates: Requirements 4.3**

### Property 9: JWT token يُصدر عند تسجيل الدخول الناجح

*لأي بيانات دخول صحيحة، يجب أن يُصدر JWT token صحيح يحتوي على معرف المستخدم والبريد الإلكتروني*

**Validates: Requirements 4.4**

### Property 10: JWT token ينتهي بعد الوقت المحدد

*لأي JWT token بصلاحية محددة، يجب أن ينتهي بعد انقضاء الوقت المحدد ولا يُقبل في الطلبات اللاحقة*

**Validates: Requirements 4.5**

### Property 11: حفظ الوظيفة يضيفها إلى قائمة الحفظ

*لأي وظيفة محفوظة من قبل مستخدم، يجب أن تظهر في قائمة الوظائف المحفوظة لهذا المستخدم*

**Validates: Requirements 5.1, 5.3**

### Property 12: معرفات الوظيفة والمستخدم تُحفظ بشكل صحيح

*لأي وظيفة محفوظة، يجب أن تحتوي على job_id و user_id صحيحة*

**Validates: Requirements 5.2**

### Property 13: حذف الوظيفة المحفوظة يزيلها من القائمة

*لأي وظيفة محفوظة يتم حذفها، يجب ألا تظهر في قائمة الوظائف المحفوظة للمستخدم*

**Validates: Requirements 5.4**

### Property 14: منع تكرار حفظ نفس الوظيفة

*لأي وظيفة محفوظة من قبل مستخدم، إذا حاول المستخدم حفظها مرة أخرى، يجب أن يُتجاهل الطلب الثاني ولا تُضاف نسخة مكررة*

**Validates: Requirements 5.5**

### Property 15: إنشاء تنبيه يُفعل المراقبة

*لأي تنبيه ينشئه مستخدم، يجب أن يكون التنبيه نشطاً ويبدأ المراقبة*

**Validates: Requirements 6.1**

### Property 16: الوظائف الجديدة تُحفظ مع تاريخ الاكتشاف

*لأي وظيفة جديدة يتم اكتشافها من خلال تنبيه، يجب أن تُحفظ في قاعدة البيانات مع تاريخ الاكتشاف الصحيح*

**Validates: Requirements 6.4**

### Property 17: تعطيل التنبيه يوقف المراقبة

*لأي تنبيه يتم تعطيله، يجب أن توقف المهام الخلفية المراقبة*

**Validates: Requirements 6.5**

### Property 18: الاستجابة بصيغة JSON مع رمز حالة صحيح

*لأي طلب إلى الواجهة البرمجية، يجب أن تكون الاستجابة بصيغة JSON صحيحة مع رمز حالة HTTP مناسب*

**Validates: Requirements 7.2**

### Property 19: معالجة الأخطاء تعيد رسالة واضحة

*لأي طلب خاطئ إلى الواجهة البرمجية، يجب أن تعيد رسالة خطأ واضحة مع رمز الخطأ المناسب*

**Validates: Requirements 7.3**

### Property 20: المصادقة تحمي نقاط النهاية المحمية

*لأي طلب إلى نقطة نهاية محمية بدون JWT token صحيح، يجب أن يُرفض الطلب*

**Validates: Requirements 7.4**

### Property 21: حفظ الوظيفة من الواجهة ينجح

*لأي نقر على زر الحفظ في الواجهة، يجب أن تُحفظ الوظيفة وتُعرض رسالة تأكيد*

**Validates: Requirements 8.5**

### Property 22: استخدام الوكلاء بشكل دوري

*لأي قائمة وكلاء محددة، يجب أن يستخدم النظام الوكلاء بشكل دوري (Round-robin)*

**Validates: Requirements 9.1**

### Property 23: الانتقال إلى الوكيل التالي عند الفشل

*لأي وكيل يفشل، يجب أن ينتقل النظام إلى الوكيل التالي في القائمة*

**Validates: Requirements 9.2**

### Property 24: تتبع معدل النجاح والفشل للوكلاء

*لأي وكيل مستخدم، يجب أن يُتتبع معدل النجاح والفشل بشكل صحيح*

**Validates: Requirements 9.3**

### Property 25: التصدير يتضمن جميع الحقول المطلوبة

*لأي تصدير للبيانات، يجب أن يتضمن جميع الحقول المحددة: title, company, location, salary_min, salary_max, job_type, description, posted_date, site_name, job_url*

**Validates: Requirements 10.2**

### Property 26: البحث المتقدم يطبق المعايير بشكل صحيح

*لأي معايير بحث متقدمة (عبارات محددة، استبعاد كلمات، عاملات منطقية)، يجب أن تُطبق على الوصف والعنوان والشركة بشكل صحيح*

**Validates: Requirements 11.1, 11.2**

### Property 27: التخزين المؤقت يعيد النتائج المحفوظة

*لأي بحث يتم إجراؤه مرتين بنفس المعايير خلال ساعة واحدة، يجب أن تُعاد النتائج المخزنة مؤقتاً من المرة الأولى*

**Validates: Requirements 12.1**

### Property 28: النتائج المخزنة لها وقت انتهاء صلاحية

*لأي نتائج بحث مخزنة مؤقتاً، يجب أن يكون لها وقت انتهاء صلاحية (TTL) قدره ساعة واحدة*

**Validates: Requirements 12.2**

### Property 29: حذف النتائج المخزنة بعد انتهاء الصلاحية

*لأي نتائج بحث مخزنة مؤقتاً، بعد انتهاء وقت الصلاحية، يجب أن تُحذف من الذاكرة المؤقتة*

**Validates: Requirements 12.3**

### Property 30: معالجة الأخطاء في الكشط تعيد نتائج جزئية

*لأي بحث يفشل من منصة معينة، يجب أن تُعاد النتائج من المنصات الأخرى الناجحة مع رسالة خطأ توضيحية*

**Validates: Requirements 1.5**



## معالجة الأخطاء (Error Handling)

### استراتيجية معالجة الأخطاء

#### مستويات الأخطاء

1. **أخطاء التحقق (Validation Errors)** - 400 Bad Request
   - بيانات مدخلة غير صحيحة
   - معاملات مفقودة
   - صيغة غير صحيحة

2. **أخطاء المصادقة (Authentication Errors)** - 401 Unauthorized
   - JWT token مفقود أو غير صحيح
   - انتهاء صلاحية الجلسة
   - بيانات دخول غير صحيحة

3. **أخطاء التفويض (Authorization Errors)** - 403 Forbidden
   - المستخدم لا يملك صلاحيات كافية
   - محاولة الوصول إلى موارد المستخدم الآخر

4. **أخطاء عدم الوجود (Not Found Errors)** - 404 Not Found
   - الموارد المطلوبة غير موجودة
   - نقطة النهاية غير موجودة

5. **أخطاء الخادم (Server Errors)** - 500 Internal Server Error
   - أخطاء غير متوقعة
   - أخطاء قاعدة البيانات
   - أخطاء الخدمات الخارجية

#### نموذج الخطأ

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "البريد الإلكتروني غير صحيح",
    "details": {
      "field": "email",
      "value": "invalid-email",
      "constraint": "email_format"
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "uuid"
  }
}
```

#### معالجة الأخطاء في الخدمات الخلفية

```python
# مثال على معالجة الأخطاء في Celery
@app.task(bind=True, max_retries=3)
def scrape_jobs_task(self, search_id):
    try:
        # محاولة الكشط
        results = scrape_jobs(search_id)
        return results
    except ScrapeError as e:
        # إعادة المحاولة بعد 5 دقائق
        raise self.retry(exc=e, countdown=300)
    except Exception as e:
        # تسجيل الخطأ وإرسال إشعار
        logger.error(f"Scraping failed: {e}")
        send_error_notification(search_id, str(e))
        raise
```

### استراتيجية إعادة المحاولة (Retry Strategy)

1. **الأخطاء المؤقتة** (Temporary Errors):
   - Timeout: إعادة محاولة بعد 5 ثوان
   - Connection Error: إعادة محاولة بعد 10 ثوان
   - Rate Limit: إعادة محاولة بعد 60 ثانية

2. **الأخطاء الدائمة** (Permanent Errors):
   - Invalid Input: لا تُعاد المحاولة
   - Authentication Error: لا تُعاد المحاولة
   - Not Found: لا تُعاد المحاولة

3. **عدد محاولات إعادة المحاولة**:
   - الحد الأقصى: 3 محاولات
   - الفاصل الزمني: exponential backoff (5s, 10s, 20s)



## استراتيجية الاختبار (Testing Strategy)

### أنواع الاختبارات

#### 1. اختبارات الوحدة (Unit Tests)

**نطاق**: اختبار الدوال والفئات الفردية بمعزل عن بعضها

**أمثلة**:
- اختبار دالة التحقق من البريد الإلكتروني
- اختبار دالة تصفية الراتب
- اختبار دالة تشفير كلمة المرور

**الأدوات**: pytest (Python), Jest (JavaScript)

**التغطية المستهدفة**: 80% على الأقل

```python
# مثال على اختبار الوحدة
def test_email_validation():
    assert validate_email("user@example.com") == True
    assert validate_email("invalid-email") == False
    assert validate_email("") == False

def test_salary_filter():
    jobs = [
        {"salary_min": 50000, "salary_max": 100000},
        {"salary_min": 100000, "salary_max": 150000},
        {"salary_min": 150000, "salary_max": 200000}
    ]
    filtered = filter_by_salary(jobs, 80000, 120000)
    assert len(filtered) == 2
```

#### 2. اختبارات التكامل (Integration Tests)

**نطاق**: اختبار تفاعل المكونات مع بعضها

**أمثلة**:
- اختبار تدفق البحث الكامل
- اختبار تدفق حفظ الوظيفة
- اختبار تدفق المصادقة

**الأدوات**: pytest, TestClient (FastAPI)

```python
# مثال على اختبار التكامل
def test_search_flow(client, db):
    # 1. تسجيل مستخدم جديد
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User"
    })
    assert response.status_code == 201
    
    # 2. تسجيل الدخول
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # 3. إجراء بحث
    response = client.post("/api/v1/search", 
        json={"search_term": "Python Developer"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    search_id = response.json()["search_id"]
    
    # 4. الحصول على النتائج
    response = client.get(f"/api/v1/search/{search_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()["results"]) > 0
```

#### 3. اختبارات الخصائص (Property-Based Tests)

**نطاق**: اختبار الخصائص العامة التي يجب أن تكون صحيحة لأي مدخلات صحيحة

**الأدوات**: Hypothesis (Python), fast-check (JavaScript)

**التكوين**: الحد الأدنى 100 تكرار لكل اختبار

```python
# مثال على اختبار الخصائص
from hypothesis import given, strategies as st

@given(st.text(min_size=1), st.text(min_size=1))
def test_search_returns_results_from_all_sites(search_term, location):
    """Property: البحث يعيد نتائج من جميع المنصات المحددة"""
    sites = ["linkedin", "indeed", "glassdoor"]
    results = perform_search(search_term, location, sites)
    
    # التحقق من أن جميع المنصات موجودة في النتائج
    result_sites = set(job["site_name"] for job in results)
    assert result_sites == set(sites)

@given(st.lists(st.integers(min_value=0, max_value=1000000)))
def test_salary_filter_property(salaries):
    """Property: تصفية الراتب تعيد النتائج الصحيحة"""
    jobs = [{"salary_min": s, "salary_max": s + 50000} for s in salaries]
    min_salary, max_salary = 100000, 150000
    
    filtered = filter_by_salary(jobs, min_salary, max_salary)
    
    # التحقق من أن جميع النتائج ضمن النطاق
    for job in filtered:
        assert job["salary_min"] >= min_salary
        assert job["salary_max"] <= max_salary
```

#### 4. اختبارات النهاية إلى النهاية (E2E Tests)

**نطاق**: اختبار التطبيق الكامل من واجهة المستخدم

**الأدوات**: Playwright, Cypress

**السيناريوهات**:
- تسجيل مستخدم جديد والبحث عن وظائف
- حفظ وظيفة وعرضها لاحقاً
- إنشاء تنبيه وتلقي إشعار

```javascript
// مثال على اختبار E2E
test('User can search for jobs and save them', async ({ page }) => {
  // 1. الذهاب إلى الصفحة الرئيسية
  await page.goto('http://localhost:3000');
  
  // 2. تسجيل الدخول
  await page.click('text=Login');
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button:has-text("Login")');
  
  // 3. البحث عن وظائف
  await page.fill('input[name="search_term"]', 'Python Developer');
  await page.click('button:has-text("Search")');
  
  // 4. انتظار النتائج
  await page.waitForSelector('.job-card');
  
  // 5. حفظ أول وظيفة
  await page.click('.job-card:first-child button:has-text("Save")');
  
  // 6. التحقق من الرسالة
  await expect(page.locator('text=Job saved successfully')).toBeVisible();
});
```

### استراتيجية التغطية

- **الوحدات**: 80% على الأقل
- **التكامل**: 60% على الأقل
- **النهاية إلى النهاية**: السيناريوهات الحرجة

### خط أنابيب الاختبار (Test Pipeline)

```
1. Unit Tests (pytest)
   ↓
2. Integration Tests (pytest + TestClient)
   ↓
3. Property-Based Tests (Hypothesis)
   ↓
4. E2E Tests (Playwright)
   ↓
5. Performance Tests (k6)
   ↓
6. Security Tests (OWASP ZAP)
```



## معمارية الأمان (Security Architecture)

### المصادقة (Authentication)

#### JWT Token Strategy

```
1. المستخدم يسجل الدخول بالبريد الإلكتروني وكلمة المرور
2. الخادم يتحقق من البيانات
3. الخادم ينشئ JWT token يحتوي على:
   - user_id
   - email
   - iat (issued at)
   - exp (expiration time)
4. الخادم يعيد access_token و refresh_token
5. العميل يحفظ tokens في localStorage (مع تحذيرات أمان)
6. العميل يرسل access_token في كل طلب
7. الخادم يتحقق من token قبل معالجة الطلب
```

#### Token Configuration

```python
# Access Token
- Algorithm: HS256
- Expiration: 1 hour
- Secret: environment variable

# Refresh Token
- Algorithm: HS256
- Expiration: 7 days
- Secret: environment variable (different from access token)
```

### التفويض (Authorization)

#### Role-Based Access Control (RBAC)

```python
# الأدوار المدعومة
- USER: مستخدم عادي
- ADMIN: مسؤول النظام
- MODERATOR: معتدل المحتوى

# الصلاحيات
- USER: يمكنه البحث، حفظ الوظائف، إنشاء التنبيهات
- ADMIN: يمكنه إدارة المستخدمين، عرض الإحصائيات
- MODERATOR: يمكنه إدارة المحتوى المخالف
```

#### Middleware للتفويض

```python
@app.get("/api/v1/admin/users")
@require_role("ADMIN")
async def get_all_users(current_user: User = Depends(get_current_user)):
    # فقط المسؤولون يمكنهم الوصول
    return await user_service.get_all_users()
```

### تشفير البيانات (Data Encryption)

#### في الراحة (At Rest)

```python
# كلمات المرور
- Algorithm: bcrypt
- Salt rounds: 12

# البيانات الحساسة
- Algorithm: AES-256-GCM
- Key: environment variable
- IV: random per encryption
```

#### في الحركة (In Transit)

```
- Protocol: HTTPS/TLS 1.3
- Certificate: Let's Encrypt
- HSTS: enabled
- CORS: configured for allowed origins
```

### حماية من الهجمات

#### SQL Injection

```python
# استخدام Parameterized Queries
# ✓ صحيح
query = "SELECT * FROM users WHERE email = %s"
cursor.execute(query, (email,))

# ✗ خطأ
query = f"SELECT * FROM users WHERE email = '{email}'"
cursor.execute(query)
```

#### XSS (Cross-Site Scripting)

```python
# استخدام Pydantic للتحقق من المدخلات
class SearchRequest(BaseModel):
    search_term: str = Field(..., max_length=255)
    
# استخدام HTML escaping في الواجهة
# Vue.js يقوم بـ escaping تلقائياً

# Content Security Policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### CSRF (Cross-Site Request Forgery)

```python
# استخدام CSRF tokens
@app.post("/api/v1/search")
async def search(request: SearchRequest, csrf_token: str = Header(...)):
    # التحقق من CSRF token
    if not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")
    # معالجة الطلب
```

#### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/search")
@limiter.limit("10/minute")
async def search(request: SearchRequest):
    # معالجة الطلب
```

### معالجة الأسرار (Secrets Management)

```python
# استخدام environment variables
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET")
REDIS_URL = os.getenv("REDIS_URL")

# في الإنتاج: استخدام AWS Secrets Manager أو HashiCorp Vault
```



## تحسين الأداء (Performance Optimization)

### استراتيجية الترقيم (Pagination)

```python
# Cursor-based pagination (الأفضل للبيانات الكبيرة)
@app.get("/api/v1/saved-jobs")
async def get_saved_jobs(
    cursor: Optional[str] = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    # استخدام cursor للحصول على الصفحة التالية
    jobs = await job_service.get_saved_jobs(
        user_id=current_user.user_id,
        cursor=cursor,
        limit=limit
    )
    return {
        "items": jobs,
        "next_cursor": jobs[-1].id if len(jobs) == limit else None
    }
```

### تحسين الاستعلامات (Query Optimization)

#### استخدام Indexes

```sql
-- فهارس على الحقول المستخدمة في WHERE
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_jobs_site_name ON jobs(site_name);
CREATE INDEX idx_saved_jobs_user_id ON saved_jobs(user_id);

-- فهارس مركبة للاستعلامات المعقدة
CREATE INDEX idx_jobs_location_type ON jobs(location, job_type);
CREATE INDEX idx_saved_jobs_user_created ON saved_jobs(user_id, saved_at DESC);
```

#### استخدام Eager Loading

```python
# ✗ N+1 Query Problem
saved_jobs = await SavedJob.find_all()
for saved_job in saved_jobs:
    job = await Job.find_by_id(saved_job.job_id)  # استعلام لكل وظيفة

# ✓ Eager Loading
saved_jobs = await SavedJob.find_all().populate("job_id")
```

### استراتيجية التخزين المؤقت (Caching)

#### Multi-Level Caching

```
1. Application Cache (في الذاكرة)
   - استخدام functools.lru_cache للدوال
   - TTL: 5 دقائق

2. Redis Cache
   - نتائج البحث: 1 ساعة
   - معلومات المستخدم: 24 ساعة
   - البيانات الثابتة: 30 يوم

3. CDN Cache
   - الملفات الثابتة: 1 سنة
   - الصور: 7 أيام
```

#### Cache Invalidation

```python
# عند حفظ وظيفة
async def save_job(user_id: UUID, job_id: UUID):
    # حفظ الوظيفة
    await saved_job_repo.create(user_id, job_id)
    
    # إلغاء التخزين المؤقت
    await cache.delete(f"user_saved_jobs:{user_id}")
    await cache.delete(f"user_profile:{user_id}")
```

### معالجة التزامن (Concurrency Handling)

#### استخدام Async/Await

```python
# البحث المتزامن من منصات متعددة
async def search_jobs(search_criteria):
    tasks = [
        scrape_linkedin(search_criteria),
        scrape_indeed(search_criteria),
        scrape_glassdoor(search_criteria),
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # معالجة الأخطاء
    successful_results = [r for r in results if not isinstance(r, Exception)]
    errors = [r for r in results if isinstance(r, Exception)]
    
    return successful_results, errors
```

#### استخدام Connection Pooling

```python
# PostgreSQL Connection Pool
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### مراقبة الأداء (Performance Monitoring)

#### Metrics

```python
# استخدام Prometheus
from prometheus_client import Counter, Histogram

request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response
```

#### Logging

```python
import logging

logger = logging.getLogger(__name__)

# استخدام structured logging
logger.info("Search started", extra={
    "user_id": user_id,
    "search_term": search_term,
    "sites": sites,
    "timestamp": datetime.now().isoformat()
})
```



## معمارية النشر (Deployment Architecture)

### Docker Containerization

#### Dockerfile للخادم

```dockerfile
# Multi-stage build
FROM python:3.11-slim as builder

WORKDIR /app

# تثبيت المتطلبات
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# المرحلة النهائية
FROM python:3.11-slim

WORKDIR /app

# نسخ المتطلبات المثبتة
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# نسخ الكود
COPY app/ ./app/

# تشغيل التطبيق
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Dockerfile للواجهة الأمامية

```dockerfile
# Build stage
FROM node:18-alpine as builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

RUN npm install -g serve

COPY --from=builder /app/dist ./dist

EXPOSE 3000

CMD ["serve", "-s", "dist", "-l", "3000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  # قاعدة البيانات
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: jobspy
      POSTGRES_USER: jobspy
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U jobspy"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # الخادم
  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://jobspy:${DB_PASSWORD}@postgres:5432/jobspy
      REDIS_URL: redis://redis:6379
      JWT_SECRET: ${JWT_SECRET}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app

  # Celery Worker
  celery:
    build: ./backend
    command: celery -A app.tasks worker --loglevel=info
    environment:
      DATABASE_URL: postgresql://jobspy:${DB_PASSWORD}@postgres:5432/jobspy
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app

  # الواجهة الأمامية
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://localhost:8000
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Kubernetes Deployment

#### Deployment للخادم

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jobspy-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: jobspy-backend
  template:
    metadata:
      labels:
        app: jobspy-backend
    spec:
      containers:
      - name: backend
        image: jobspy-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: jobspy-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: jobspy-config
              key: redis-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

#### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: jobspy-backend-service
spec:
  selector:
    app: jobspy-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### CI/CD Pipeline

#### GitHub Actions

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: pytest --cov=app tests/
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: docker build -t jobspy-backend:${{ github.sha }} .
    
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker tag jobspy-backend:${{ github.sha }} jobspy-backend:latest
        docker push jobspy-backend:${{ github.sha }}
        docker push jobspy-backend:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/jobspy-backend \
          backend=jobspy-backend:${{ github.sha }} \
          --record
```

### متطلبات البيئة

#### Development

```bash
# متطلبات النظام
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose

# متطلبات Python
pip install -r requirements.txt

# متطلبات Node.js
npm install
```

#### Production

```bash
# متطلبات النظام
- Kubernetes 1.24+
- Docker Registry
- PostgreSQL 15+ (Managed Service)
- Redis 7+ (Managed Service)
- Load Balancer
- SSL Certificate

# متطلبات الأمان
- HTTPS/TLS 1.3
- Network Policies
- Pod Security Policies
- RBAC
```

### مراقبة وتسجيل (Monitoring & Logging)

#### Prometheus + Grafana

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'jobspy-backend'
    static_configs:
      - targets: ['localhost:8000']
```

#### ELK Stack (Elasticsearch, Logstash, Kibana)

```yaml
# logstash.conf
input {
  file {
    path => "/var/log/jobspy/*.log"
    start_position => "beginning"
  }
}

filter {
  json {
    source => "message"
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "jobspy-%{+YYYY.MM.dd}"
  }
}
```



## تدفقات البيانات (Data Flow Diagrams)

### تدفق البحث (Search Flow)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. المستخدم يدخل معايير البحث في الواجهة                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. الواجهة ترسل طلب POST إلى /api/v1/search                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. FastAPI يتحقق من JWT token والمدخلات                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. يتحقق من Redis للنتائج المخزنة مؤقتاً                    │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼ (موجود)                ▼ (غير موجود)
    ┌────────┐              ┌──────────────┐
    │ عودة   │              │ إنشاء مهمة   │
    │النتائج │              │ Celery       │
    └────────┘              └──────┬───────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │ Celery Worker يكشط المنصات  │
                    │ بشكل متزامن                 │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
            ┌──────────────┐            ┌──────────────┐
            │ LinkedIn     │            │ Indeed       │
            │ Scraper      │            │ Scraper      │
            └──────┬───────┘            └──────┬───────┘
                   │                           │
                   └──────────────┬────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────────┐
                    │ حفظ النتائج في PostgreSQL    │
                    │ وتخزينها في Redis           │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │ إرسال النتائج إلى الواجهة    │
                    │ عبر WebSocket أو Polling    │
                    └──────────────────────────────┘
```

### تدفق المصادقة (Authentication Flow)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. المستخدم يدخل البريد الإلكتروني وكلمة المرور             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. الواجهة ترسل طلب POST إلى /api/v1/auth/login            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. FastAPI يتحقق من البريد الإلكتروني في قاعدة البيانات    │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼ (موجود)                ▼ (غير موجود)
    ┌────────────┐            ┌──────────────┐
    │ التحقق من  │            │ إرجاع خطأ    │
    │كلمة المرور │            │ 401          │
    └────┬───────┘            └──────────────┘
         │
    ┌────┴────────────────────┐
    │                         │
    ▼ (صحيح)                 ▼ (خطأ)
┌──────────────┐         ┌──────────────┐
│ إنشاء JWT    │         │ إرجاع خطأ    │
│ tokens       │         │ 401          │
└────┬─────────┘         └──────────────┘
     │
     ▼
┌──────────────────────────────────────┐
│ إرجاع access_token و refresh_token   │
└────┬─────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────┐
│ الواجهة تحفظ tokens في localStorage  │
└────┬─────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────┐
│ المستخدم يُعاد توجيهه إلى الصفحة    │
│ الرئيسية                             │
└──────────────────────────────────────┘
```

### تدفق التنبيهات (Alert Flow)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. المستخدم ينشئ تنبيهاً لبحث محفوظ                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. FastAPI يحفظ التنبيه في قاعدة البيانات                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Celery Beat يشغل مهمة كل ساعة                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Celery Worker يبحث عن وظائف جديدة                       │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼ (وظائف جديدة)          ▼ (لا توجد وظائف جديدة)
    ┌────────────┐            ┌──────────────┐
    │ حفظ الوظائف│            │ انتظر الساعة │
    │الجديدة     │            │ القادمة      │
    └────┬───────┘            └──────────────┘
         │
         ▼
    ┌────────────────────────────────┐
    │ إرسال بريد إلكتروني للمستخدم  │
    └────┬───────────────────────────┘
         │
         ▼
    ┌────────────────────────────────┐
    │ تحديث last_checked في قاعدة   │
    │ البيانات                       │
    └────────────────────────────────┘
```

## الخلاصة والملاحظات المهمة

### المبادئ الأساسية للتصميم

1. **الفصل بين الطبقات**: فصل واضح بين الواجهة والخادم والقاعدة
2. **قابلية التوسع**: معمارية تدعم النمو الأفقي والعمودي
3. **الأمان أولاً**: تشفير، مصادقة، وتفويض في كل مستوى
4. **الأداء العالية**: تخزين مؤقت، ترقيم، وتحسين الاستعلامات
5. **الموثوقية**: معالجة أخطاء، إعادة محاولة، وتسجيل شامل

### التقنيات المستخدمة

**Backend**:
- FastAPI: إطار عمل ويب حديث وسريع
- SQLAlchemy: ORM قوي وآمن
- Pydantic: التحقق من البيانات والتسلسل
- Celery: معالجة المهام غير المتزامنة
- Redis: التخزين المؤقت والجلسات

**Frontend**:
- Vue.js 3: إطار عمل تفاعلي حديث
- Pinia: إدارة الحالة
- Vite: أداة بناء سريعة
- Tailwind CSS: تصميم استجابي

**Database**:
- PostgreSQL: قاعدة بيانات علائقية قوية
- Alembic: إدارة الهجرات

**DevOps**:
- Docker: حاويات
- Kubernetes: تنسيق الحاويات
- GitHub Actions: CI/CD

### الخطوات التالية

1. **إنشاء المشاريع**: إنشاء مشاريع FastAPI و Vue.js
2. **إعداد قاعدة البيانات**: إنشاء جداول وفهارس
3. **تطوير الواجهة البرمجية**: تطوير نقاط النهاية
4. **تطوير الواجهة الأمامية**: بناء المكونات والصفحات
5. **الاختبار**: كتابة اختبارات شاملة
6. **النشر**: نشر على الإنتاج

