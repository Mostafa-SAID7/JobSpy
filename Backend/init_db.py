"""
Initialize the database with all tables
"""
import asyncio
from app.infrastructure.persistence.sqlalchemy.database import init_db
# Import all models so SQLAlchemy knows about them
from app.infrastructure.persistence.sqlalchemy.models import (
    UserORM,
    JobORM,
    SavedJobORM,
    AlertORM,
    SearchHistoryORM,
)

async def main():
    print("Initializing database...")
    await init_db()
    print("Database initialized successfully!")

if __name__ == "__main__":
    asyncio.run(main())
