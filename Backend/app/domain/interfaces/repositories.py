"""
Repository Interfaces

Contracts for data persistence that infrastructure must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID

from ..entities.job import Job
from ..entities.user import User
from ..entities.saved_job import SavedJob
from ..entities.alert import Alert


class IJobRepository(ABC):
    """Interface for job repository."""
    
    @abstractmethod
    async def save(self, job: Job) -> Job: pass
    
    @abstractmethod
    async def get_by_id(self, job_id: UUID) -> Optional[Job]: pass
    
    @abstractmethod
    async def get_by_source_url(self, source_url: str) -> Optional[Job]: pass
    
    @abstractmethod
    async def exists_by_url(self, source_url: str) -> bool: pass
    
    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Job]: pass
    
    @abstractmethod
    async def find_by_source(self, source: str, skip: int = 0, limit: int = 100) -> List[Job]: pass
    
    @abstractmethod
    async def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Job]: pass
    
    @abstractmethod
    async def update(self, job: Job) -> Job: pass
    
    @abstractmethod
    async def delete(self, job_id: UUID) -> bool: pass
    
    @abstractmethod
    async def count(self) -> int: pass


class IUserRepository(ABC):
    """Interface for user repository."""
    
    @abstractmethod
    async def create(self, user: User) -> User: pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]: pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]: pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]: pass
    
    @abstractmethod
    async def update(self, user: User) -> User: pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool: pass
    
    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[User]: pass
    
    @abstractmethod
    async def count(self) -> int: pass


class ISavedJobRepository(ABC):
    """Interface for saved job repository."""
    
    @abstractmethod
    async def create(self, saved_job: SavedJob) -> SavedJob: pass
    
    @abstractmethod
    async def get_by_id(self, saved_job_id: UUID) -> Optional[SavedJob]: pass
    
    @abstractmethod
    async def get_by_user_and_job(self, user_id: UUID, job_id: UUID) -> Optional[SavedJob]: pass
    
    @abstractmethod
    async def get_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[SavedJob]: pass
    
    @abstractmethod
    async def get_by_user_with_jobs(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Tuple[SavedJob, Job]]: pass
    
    @abstractmethod
    async def delete(self, saved_job_id: UUID) -> bool: pass
    
    @abstractmethod
    async def delete_by_user_and_job(self, user_id: UUID, job_id: UUID) -> bool: pass
    
    @abstractmethod
    async def count_by_user(self, user_id: UUID) -> int: pass
    
    @abstractmethod
    async def is_saved(self, user_id: UUID, job_id: UUID) -> bool: pass


class IAlertRepository(ABC):
    """Interface for alert repository."""
    
    @abstractmethod
    async def create(self, alert: Alert) -> Alert: pass
    
    @abstractmethod
    async def get_by_id(self, alert_id: UUID) -> Optional[Alert]: pass
    
    @abstractmethod
    async def get_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Alert]: pass
    
    @abstractmethod
    async def update(self, alert: Alert) -> Alert: pass
    
    @abstractmethod
    async def delete(self, alert_id: UUID) -> bool: pass
    
    @abstractmethod
    async def count_by_user(self, user_id: UUID) -> int: pass
    
    @abstractmethod
    async def get_all_active(self) -> List[Alert]: pass


class IStatsRepository(ABC):
    """Interface for statistics repository."""
    
    @abstractmethod
    async def get_total_jobs(self) -> int: pass
    
    @abstractmethod
    async def get_jobs_by_source(self) -> Dict[str, int]: pass
    
    @abstractmethod
    async def get_jobs_by_company(self, limit: int = 10) -> List[Dict[str, Any]]: pass
    
    @abstractmethod
    async def get_jobs_by_type(self) -> Dict[str, int]: pass
    
    @abstractmethod
    async def get_remote_jobs_count(self) -> int: pass
    
    @abstractmethod
    async def get_salary_statistics(self) -> Dict[str, Any]: pass
    
    @abstractmethod
    async def get_jobs_posted_today(self) -> int: pass
    
    @abstractmethod
    async def get_jobs_posted_this_week(self) -> int: pass
    
    @abstractmethod
    async def get_total_users(self) -> int: pass
    
    @abstractmethod
    async def get_total_saved_jobs(self) -> int: pass
    
    @abstractmethod
    async def get_active_users(self, days: int = 30) -> int: pass
    
    @abstractmethod
    async def get_search_statistics(self) -> Dict[str, Any]: pass
    
    @abstractmethod
    async def get_trending_searches(self, limit: int = 10, days: int = 7) -> List[Dict[str, Any]]: pass
    
    @abstractmethod
    async def get_jobs_by_location(self, limit: int = 10) -> List[Dict[str, Any]]: pass


class ISearchHistoryRepository(ABC):
    @abstractmethod
    async def count_by_user(self, user_id: UUID) -> int: pass
