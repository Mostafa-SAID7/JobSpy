"""
Script to create a test user for development
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.infrastructure.persistence.sqlalchemy.database import AsyncSessionLocal
from app.infrastructure.persistence.sqlalchemy.models.user_orm import UserORM
from app.shared.security.security import hash_password


async def create_test_user():
    """Create a test user"""
    async with AsyncSessionLocal() as session:
        try:
            # Check if user already exists
            result = await session.execute(
                select(UserORM).where(UserORM.email == "test@example.com")
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print("✅ Test user already exists!")
                print(f"   Email: test@example.com")
                print(f"   Password: password123")
                return
            
            # Create new user
            hashed_password = hash_password("password123")
            user = UserORM(
                email="test@example.com",
                username="testuser",
                full_name="Test User",
                hashed_password=hashed_password,
                is_active=True,
                is_verified=True,
            )
            
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            print("✅ Test user created successfully!")
            print(f"   Email: test@example.com")
            print(f"   Password: password123")
            print(f"   Username: testuser")
            print(f"   User ID: {user.id}")
            
        except Exception as e:
            print(f"❌ Error creating test user: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(create_test_user())
