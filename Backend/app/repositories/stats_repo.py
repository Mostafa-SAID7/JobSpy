"""
Statistics Repository for computing and caching statistics data
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from uuid import UUID
from datetime import datetime, timedelta
import logging

from app.models.job import Job
from app.models.user import User
from app.models.saved_job import SavedJob
from app.models.search_history import SearchHistory

logger = logging.getLogger(__name__)


class StatsRepository:
    """Repository for computing statistics from database"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_total_jobs(self) -> int:
        """Get total number of jobs in database"""
        result = await self.session.execute(select(func.count(Job.id)))
        return result.scalar() or 0
    
    async def get_jobs_by_source(self) -> dict[str, int]:
        """Get count of jobs by source"""
        result = await self.session.execute(
            select(Job.source, func.count(Job.id))
            .group_by(Job.source)
            .order_by(func.count(Job.id).desc())
        )
        return {source: count for source, count in result.all()}
    
    async def get_jobs_by_company(self, limit: int = 10) -> list[dict]:
        """Get top companies by job count"""
        result = await self.session.execute(
            select(Job.company, func.count(Job.id).label("count"))
            .group_by(Job.company)
            .order_by(func.count(Job.id).desc())
            .limit(limit)
        )
        return [
            {"company": company, "count": count}
            for company, count in result.all()
        ]
    
    async def get_jobs_by_type(self) -> dict[str, int]:
        """Get count of jobs by type"""
        result = await self.session.execute(
            select(Job.job_type, func.count(Job.id))
            .group_by(Job.job_type)
            .order_by(func.count(Job.id).desc())
        )
        return {job_type: count for job_type, count in result.all() if job_type}
    
    async def get_remote_jobs_count(self) -> int:
        """Get count of remote jobs"""
        result = await self.session.execute(
            select(func.count(Job.id)).where(Job.is_remote == True)
        )
        return result.scalar() or 0
    
    async def get_salary_statistics(self) -> dict:
        """Get salary statistics"""
        result = await self.session.execute(
            select(
                func.min(Job.salary_min).label("min_salary"),
                func.max(Job.salary_max).label("max_salary"),
                func.avg(Job.salary_min).label("avg_min_salary"),
                func.avg(Job.salary_max).label("avg_max_salary"),
            ).where(Job.salary_min.isnot(None))
        )
        row = result.one()
        return {
            "min_salary": float(row.min_salary) if row.min_salary else None,
            "max_salary": float(row.max_salary) if row.max_salary else None,
            "avg_min_salary": float(row.avg_min_salary) if row.avg_min_salary else None,
            "avg_max_salary": float(row.avg_max_salary) if row.avg_max_salary else None,
        }
    
    async def get_jobs_posted_today(self) -> int:
        """Get count of jobs posted today"""
        today = datetime.utcnow().date()
        result = await self.session.execute(
            select(func.count(Job.id)).where(
                func.date(Job.created_at) == today
            )
        )
        return result.scalar() or 0
    
    async def get_jobs_posted_this_week(self) -> int:
        """Get count of jobs posted this week"""
        week_ago = datetime.utcnow() - timedelta(days=7)
        result = await self.session.execute(
            select(func.count(Job.id)).where(Job.created_at >= week_ago)
        )
        return result.scalar() or 0
    
    async def get_total_users(self) -> int:
        """Get total number of users"""
        result = await self.session.execute(select(func.count(User.id)))
        return result.scalar() or 0
    
    async def get_active_users(self, days: int = 30) -> int:
        """Get count of active users in last N days"""
        days_ago = datetime.utcnow() - timedelta(days=days)
        result = await self.session.execute(
            select(func.count(User.id)).where(User.updated_at >= days_ago)
        )
        return result.scalar() or 0
    
    async def get_total_saved_jobs(self) -> int:
        """Get total number of saved jobs"""
        result = await self.session.execute(select(func.count(SavedJob.id)))
        return result.scalar() or 0
    
    async def get_saved_jobs_by_user(self, user_id: UUID) -> int:
        """Get count of saved jobs for a user"""
        result = await self.session.execute(
            select(func.count(SavedJob.id)).where(SavedJob.user_id == user_id)
        )
        return result.scalar() or 0
    
    async def get_trending_searches(self, limit: int = 10, days: int = 7) -> list[dict]:
        """Get trending search queries"""
        days_ago = datetime.utcnow() - timedelta(days=days)
        result = await self.session.execute(
            select(SearchHistory.query, func.count(SearchHistory.id).label("count"))
            .where(SearchHistory.created_at >= days_ago)
            .group_by(SearchHistory.query)
            .order_by(func.count(SearchHistory.id).desc())
            .limit(limit)
        )
        return [
            {"query": query, "count": count}
            for query, count in result.all()
            if query
        ]
    
    async def get_search_statistics(self) -> dict:
        """Get overall search statistics"""
        total_searches = await self.session.execute(
            select(func.count(SearchHistory.id))
        )
        total_searches = total_searches.scalar() or 0
        
        unique_users = await self.session.execute(
            select(func.count(func.distinct(SearchHistory.user_id)))
        )
        unique_users = unique_users.scalar() or 0
        
        return {
            "total_searches": total_searches,
            "unique_users": unique_users,
            "avg_searches_per_user": (
                total_searches / unique_users if unique_users > 0 else 0
            ),
        }
    
    async def get_jobs_by_location(self, limit: int = 10) -> list[dict]:
        """Get top job locations"""
        result = await self.session.execute(
            select(Job.location, func.count(Job.id).label("count"))
            .where(Job.location.isnot(None))
            .group_by(Job.location)
            .order_by(func.count(Job.id).desc())
            .limit(limit)
        )
        return [
            {"location": location, "count": count}
            for location, count in result.all()
        ]
