# تطبيق JobSpy الويب
# JobSpy Web Application

منصة بحث عن الوظائف الشاملة - A Comprehensive Job Search Platform

## 📋 نظرة عامة | Overview

تطبيق JobSpy الويب هو منصة متكاملة للبحث عن الوظائف تجمع بيانات الوظائف من عدة مصادر (LinkedIn, Indeed, Wuzzuf, Bayt) وتوفر واجهة موحدة للبحث والتصفية والحفظ والتنبيهات.

JobSpy Web Application is a comprehensive job search platform that aggregates job data from multiple sources (LinkedIn, Indeed, Wuzzuf, Bayt) and provides a unified interface for searching, filtering, saving, and alerts.

## 🏗️ البنية المعمارية | Architecture

```
JobSpy/
├── Backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── routers/        # API Endpoints
│   │   ├── services/       # Business Logic
│   │   ├── repositories/   # Data Access Layer
│   │   ├── models/         # SQLAlchemy Models
│   │   ├── schemas/        # Pydantic Schemas
│   │   ├── core/           # Configuration & Utils
│   │   └── main.py         # FastAPI App
│   ├── requirements.txt    # Python Dependencies
│   ├── Dockerfile          # Backend Container
│   └── .env.example        # Environment Variables
│
├── Frontend/               # Vue.js Frontend
│   ├── src/
│   │   ├── components/     # Vue Components
│   │   ├── pages/          # Page Components
│   │   ├── stores/         # Pinia Stores
│   │   ├── services/       # API Services
│   │   └── App.vue         # Root Component
│   ├── tailwind.config.js  # Tailwind Config
│   ├── Dockerfile          # Frontend Container
│   └── package.json        # Node Dependencies
│
├── docker-compose.yml      # Docker Compose
└── README.md              # This File
```

## 🚀 البدء السريع | Quick Start

### المتطلبات | Requirements

- Docker & Docker Compose
- Python 3.11+ (للتطوير المحلي)
- Node.js 20+ (للتطوير المحلي)

### التثبيت والتشغيل | Installation & Running

#### باستخدام Docker Compose | Using Docker Compose

```bash
# Clone the repository
git clone https://github.com/speedyapply/JobSpy.git
cd JobSpy

# Copy environment file
cp Backend/.env.example Backend/.env

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

#### التطوير المحلي | Local Development

**Backend:**
```bash
cd Backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd Frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 📚 التوثيق | Documentation

### API Documentation
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Project Documentation
- [Requirements](./docs/requirements.md) - المتطلبات الوظيفية
- [Design](./docs/design.md) - التصميم المعماري
- [Tasks](./docs/tasks.md) - قائمة المهام

## 🔧 التكوين | Configuration

### متغيرات البيئة | Environment Variables

انظر إلى `Backend/.env.example` للحصول على قائمة كاملة بمتغيرات البيئة المتاحة.

### قاعدة البيانات | Database

- **Type**: PostgreSQL 16
- **Host**: localhost (Docker: postgres)
- **Port**: 5432
- **User**: jobspy_user
- **Password**: jobspy_password
- **Database**: jobspy_db

### Redis Cache

- **Host**: localhost (Docker: redis)
- **Port**: 6379
- **Database**: 0 (Cache), 1 (Celery Broker), 2 (Celery Results)

## 🧪 الاختبار | Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

## 📦 المكتبات الرئيسية | Main Libraries

### Backend
- **FastAPI**: Modern web framework
- **SQLAlchemy**: ORM
- **Pydantic**: Data validation
- **Celery**: Task queue
- **Redis**: Caching & Message Broker
- **PostgreSQL**: Database

### Frontend
- **Vue 3**: UI Framework
- **Pinia**: State Management
- **Tailwind CSS**: Styling
- **Vite**: Build Tool
- **Axios**: HTTP Client

## 🔐 الأمان | Security

- JWT Authentication
- Password Hashing (bcrypt)
- CORS Protection
- Rate Limiting
- SQL Injection Prevention
- XSS Protection

## 📊 الأداء | Performance

- Redis Caching
- Database Query Optimization
- Pagination
- Lazy Loading
- Code Splitting

## 🤝 المساهمة | Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 الترخيص | License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 الفريق | Team

- **Project Lead**: JobSpy Team
- **Backend**: FastAPI Development Team
- **Frontend**: Vue.js Development Team

## 📞 التواصل | Contact

- Email: support@jobspy.com
- GitHub: https://github.com/speedyapply/JobSpy
- Issues: https://github.com/speedyapply/JobSpy/issues

## 🙏 شكر وتقدير | Acknowledgments

- FastAPI Documentation
- Vue.js Documentation
- SQLAlchemy Documentation
- Tailwind CSS Documentation

---

**آخر تحديث**: 23 أبريل 2026
**Last Updated**: April 23, 2026
