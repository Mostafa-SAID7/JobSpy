"""
Stats Repository Implementation (Infrastructure Layer)

Implements IStatsRepository using SQLAlchemy aggregations.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.domain.interfaces.repositories import IStatsRepository
from app.infrastructure.persistence.sqlalchemy.models.job_orm import JobORM
from app.infrastructure.persistence.sqlalchemy.models.user_orm import UserORM
from app.infrastructure.persistence.sqlalchemy.models.saved_job_orm import SavedJobORM
from app.infrastructure.persistence.sqlalchemy.models.search_history_orm import SearchHistoryORM


class StatsRepositoryImpl(IStatsRepository):
    """
    SQLAlchemy implementation of IStatsRepository.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_total_jobs(self) -> int:
        """Get total number of jobs."""
        result = await self.session.execute(select(func.count(JobORM.id)))
        return result.scalar() or 0

    async def get_jobs_by_source(self) -> Dict[str, int]:
        """Get job count grouped by source."""
        result = await self.session.execute(
            select(JobORM.source, func.count(JobORM.id))
            .group_by(JobORM.source)
            .order_by(func.count(JobORM.id).desc())
        )
        return {source: count for source, count in result.all() if source}

    async def get_jobs_by_company(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top companies by job count."""
        result = await self.session.execute(
            select(JobORM.company, func.count(JobORM.id).label("count"))
            .group_by(JobORM.company)
            .order_by(func.count(JobORM.id).desc())
            .limit(limit)
        )
        return [{"company": company, "count": count} for company, count in result.all()]

    async def get_jobs_by_type(self) -> Dict[str, int]:
        """Get job count grouped by type."""
        result = await self.session.execute(
            select(JobORM.job_type, func.count(JobORM.id))
            .group_by(JobORM.job_type)
            .order_by(func.count(JobORM.id).desc())
        )
        return {job_type: count for job_type, count in result.all() if job_type}

    async def get_remote_jobs_count(self) -> int:
        """Get count of remote jobs (is_remote == 1 or 2)."""
        result = await self.session.execute(
            select(func.count(JobORM.id)).where(JobORM.is_remote > 0)
        )
        return result.scalar() or 0

    async def get_salary_statistics(self) -> Dict[str, Any]:
        """Get salary min/max/avg statistics."""
        result = await self.session.execute(
            select(
                func.min(JobORM.salary_min).label("min_salary"),
                func.max(JobORM.salary_max).label("max_salary"),
                func.avg(JobORM.salary_min).label("avg_min_salary"),
                func.avg(JobORM.salary_max).label("avg_max_salary"),
            ).where(JobORM.salary_min.isnot(None))
        )
        row = result.one()
        return {
            "min_salary": float(row.min_salary) if row.min_salary else None,
            "max_salary": float(row.max_salary) if row.max_salary else None,
            "avg_min_salary": float(row.avg_min_salary) if row.avg_min_salary else None,
            "avg_max_salary": float(row.avg_max_salary) if row.avg_max_salary else None,
        }

    async def get_jobs_posted_today(self) -> int:
        """Get count of jobs created today."""
        today = datetime.utcnow().date()
        result = await self.session.execute(
            select(func.count(JobORM.id)).where(
                func.date(JobORM.created_at) == today
            )
        )
        return result.scalar() or 0

    async def get_total_users(self) -> int:
        """Get total number of users."""
        result = await self.session.execute(select(func.count(UserORM.id)))
        return result.scalar() or 0

    async def get_total_saved_jobs(self) -> int:
        """Get total number of saved jobs."""
        result = await self.session.execute(select(func.count(SavedJobORM.id)))
        return result.scalar() or 0

    async def get_active_users(self, days: int = 30) -> int:
        """Get count of recently active users."""
        threshold = datetime.utcnow() - timedelta(days=days)
        result = await self.session.execute(
            select(func.count(UserORM.id)).where(UserORM.updated_at >= threshold)
        )
        return result.scalar() or 0

    async def get_trending_searches(self, limit: int = 10, days: int = 7) -> List[Dict[str, Any]]:
        """Get trending search queries."""
        days_ago = datetime.utcnow() - timedelta(days=days)
        result = await self.session.execute(
            select(SearchHistoryORM.query, func.count(SearchHistoryORM.id).label("count"))
            .where(SearchHistoryORM.created_at >= days_ago)
            .group_by(SearchHistoryORM.query)
            .order_by(func.count(SearchHistoryORM.id).desc())
            .limit(limit)
        )
        return [{"query": q, "count": c} for q, c in result.all() if q]

    async def get_jobs_by_location(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top job locations."""
        result = await self.session.execute(
            select(JobORM.location, func.count(JobORM.id).label("count"))
            .where(JobORM.location.isnot(None))
            .group_by(JobORM.location)
            .order_by(func.count(JobORM.id).desc())
            .limit(limit)
        )
        return [{"location": loc, "count": c} for loc, c in result.all()]
