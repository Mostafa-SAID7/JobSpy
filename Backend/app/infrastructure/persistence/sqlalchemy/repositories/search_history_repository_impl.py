"""
Search History Repository Implementation (Infrastructure Layer)

Fully replaces the legacy app.repositories.search_history_repo.
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.infrastructure.persistence.sqlalchemy.models.search_history_orm import SearchHistoryORM


class SearchHistoryRepositoryImpl:
    """
    SQLAlchemy implementation for search history persistence.
    Does NOT import legacy app.models — uses only infrastructure ORM models.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: UUID, query: str, filters: dict = None,
                     results_count: int = 0, search_type: str = "basic",
                     job_id: UUID = None) -> SearchHistoryORM:
        """Create a new search history record."""
        db_search = SearchHistoryORM(
            user_id=user_id,
            job_id=job_id,
            query=query,
            filters=filters or {},
            results_count=results_count,
            search_type=search_type,
        )
        self.session.add(db_search)
        await self.session.flush()
        return db_search

    async def get_by_id(self, search_id: UUID) -> Optional[SearchHistoryORM]:
        """Get search history by ID."""
        result = await self.session.execute(
            select(SearchHistoryORM).where(SearchHistoryORM.id == search_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[SearchHistoryORM]:
        """Get search history for a user."""
        result = await self.session.execute(
            select(SearchHistoryORM)
            .where(SearchHistoryORM.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(SearchHistoryORM.created_at.desc())
        )
        return result.scalars().all()

    async def delete(self, search_id: UUID) -> bool:
        """Delete search history by ID."""
        search = await self.get_by_id(search_id)
        if not search:
            return False
        await self.session.delete(search)
        await self.session.flush()
        return True

    async def delete_by_user(self, user_id: UUID) -> int:
        """Delete all search history for a user."""
        result = await self.session.execute(
            select(SearchHistoryORM).where(SearchHistoryORM.user_id == user_id)
        )
        records = result.scalars().all()
        count = len(records)
        for record in records:
            await self.session.delete(record)
        await self.session.flush()
        return count

    async def count_by_user(self, user_id: UUID) -> int:
        """Count search history entries for a user."""
        result = await self.session.execute(
            select(SearchHistoryORM).where(SearchHistoryORM.user_id == user_id)
        )
        return len(result.scalars().all())
