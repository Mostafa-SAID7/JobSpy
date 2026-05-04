#!/usr/bin/env python3
"""
Database Setup Script
Initializes PostgreSQL database and runs migrations
"""

import asyncio
import sys
from app.infrastructure.persistence.sqlalchemy.database import init_db, engine
from app.config.settings import settings


async def setup_database():
    """Initialize database tables"""
    print("Setting up database...")
    print(f"Database URL: {settings.DATABASE_URL}")
    
    try:
        # Create all tables
        await init_db()
        print("Database tables created successfully!")
        
        # Test connection
        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1")
            print("Database connection verified!")
        
        return True
    except Exception as e:
        print(f"Error setting up database: {e}")
        return False
    finally:
        await engine.dispose()


if __name__ == "__main__":
    success = asyncio.run(setup_database())
    sys.exit(0 if success else 1)
