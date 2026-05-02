from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.domain.entities.user import User
from app.domain.interfaces.repositories import IUserRepository
from app.infrastructure.persistence.sqlalchemy.models.user_orm import UserORM
from app.infrastructure.persistence.sqlalchemy.mappers.user_mapper import UserMapper


class UserRepositoryImpl(IUserRepository):
    """
    SQLAlchemy implementation of IUserRepository.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        """Create a new user."""
        orm_user = UserMapper.to_orm(user)
        self.session.add(orm_user)
        await self.session.flush()
        await self.session.commit()
        return UserMapper.to_domain(orm_user)

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.session.execute(
            select(UserORM).where(UserORM.id == user_id)
        )
        orm_user = result.scalar_one_or_none()
        return UserMapper.to_domain(orm_user) if orm_user else None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.session.execute(
            select(UserORM).where(UserORM.email == email)
        )
        orm_user = result.scalar_one_or_none()
        return UserMapper.to_domain(orm_user) if orm_user else None

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        result = await self.session.execute(
            select(UserORM).where(UserORM.username == username)
        )
        orm_user = result.scalar_one_or_none()
        return UserMapper.to_domain(orm_user) if orm_user else None

    async def update(self, user: User) -> User:
        """Update a user."""
        result = await self.session.execute(
            select(UserORM).where(UserORM.id == user.id)
        )
        orm_user = result.scalar_one_or_none()
        if not orm_user:
            raise ValueError(f"User with ID {user.id} not found")
        
        # Update fields
        orm_user.email = user.email
        orm_user.username = user.username
        orm_user.full_name = user.full_name
        orm_user.phone = user.phone
        orm_user.bio = user.bio
        orm_user.is_active = user.is_active
        orm_user.is_verified = user.is_verified
        orm_user.last_login = user.last_login
        
        await self.session.flush()
        return UserMapper.to_domain(orm_user)

    async def delete(self, user_id: UUID) -> bool:
        """Delete a user."""
        result = await self.session.execute(
            select(UserORM).where(UserORM.id == user_id)
        )
        orm_user = result.scalar_one_or_none()
        if not orm_user:
            return False
        
        await self.session.delete(orm_user)
        await self.session.flush()
        return True

    async def find_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Find all users."""
        result = await self.session.execute(
            select(UserORM).offset(skip).limit(limit)
        )
        orm_users = result.scalars().all()
        return [UserMapper.to_domain(u) for u in orm_users]

    async def count(self) -> int:
        """Count users."""
        result = await self.session.execute(select(func.count(UserORM.id)))
        return result.scalar() or 0
