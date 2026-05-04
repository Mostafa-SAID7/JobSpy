import asyncio
import sys
import os
from sqlalchemy import select

# Add Backend to path
backend_path = os.path.abspath(os.path.join(os.getcwd(), 'Backend'))
sys.path.append(backend_path)

# Change directory to Backend to load .env correctly
os.chdir(backend_path)

from app.infrastructure.persistence.sqlalchemy.database import AsyncSessionLocal
from app.infrastructure.persistence.sqlalchemy.models.user_model import UserModel

async def check_user():
    async with AsyncSessionLocal() as session:
        try:
            email = "m.ssaid356@gmail.com"
            query = select(UserModel).where(UserModel.email == email)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            
            if user:
                print(f"User found: {user.email}")
                print(f"Hashed password: {user.hashed_password}")
                print(f"Is active: {user.is_active}")
            else:
                print(f"User NOT found: {email}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await session.close()

if __name__ == "__main__":
    asyncio.run(check_user())
