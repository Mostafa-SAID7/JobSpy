"""
خدمة التنبيهات - JobSpy
Alert service for JobSpy
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.alert import Alert
from app.repositories.alert_repo import AlertRepository
from app.repositories.job_repo import JobRepository
from app.repositories.search_history_repo import SearchHistoryRepository
from app.core.redis import redis_client
from app.core.config import settings

logger = logging.getLogger(__name__)


class AlertService:
    """Service for handling alert operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.alert_repo = AlertRepository(db)
        self.job_repo = JobRepository(db)
        self.search_repo = SearchHistoryRepository(db)
    
    async def get_alerts_to_trigger(self) -> List[Alert]:
        """Get alerts that need to be triggered."""
        return await self.alert_repo.get_alerts_to_trigger()
    
    async def trigger_alert(self, alert: Alert) -> Dict[str, Any]:
        """
        Trigger an alert and search for new jobs.
        
        Args:
            alert: Alert to trigger
        
        Returns:
            Dictionary with alert trigger results
        """
        try:
            # Search for jobs matching alert criteria
            jobs = await self.job_repo.search(alert.query)
            
            # Filter by additional criteria if provided
            if alert.filters:
                jobs = self._filter_jobs(jobs, alert.filters)
            
            # Count new jobs (posted after last trigger)
            new_jobs_count = 0
            new_jobs = []
            
            if alert.last_triggered:
                new_jobs = [
                    job for job in jobs
                    if job.posted_date and job.posted_date > alert.last_triggered
                ]
                new_jobs_count = len(new_jobs)
            else:
                new_jobs = jobs
                new_jobs_count = len(jobs)
            
            # Update alert trigger info
            next_trigger = self._calculate_next_trigger(alert.frequency)
            await self.alert_repo.update_trigger_info(alert.id, next_trigger)
            await self.db.commit()
            
            logger.info(f"Alert {alert.id} triggered: {new_jobs_count} new jobs found")
            
            return {
                "alert_id": alert.id,
                "new_jobs_count": new_jobs_count,
                "new_jobs": new_jobs,
                "next_trigger": next_trigger,
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error triggering alert {alert.id}: {str(e)}")
            return {
                "alert_id": alert.id,
                "new_jobs_count": 0,
                "new_jobs": [],
                "success": False,
                "error": str(e),
            }
    
    @staticmethod
    def _filter_jobs(jobs: List[Any], filters: Dict[str, Any]) -> List[Any]:
        """Filter jobs based on criteria."""
        filtered = jobs
        
        if "location" in filters and filters["location"]:
            location = filters["location"].lower()
            filtered = [j for j in filtered if location in (j.location or "").lower()]
        
        if "job_type" in filters and filters["job_type"]:
            job_type = filters["job_type"].lower()
            filtered = [j for j in filtered if j.job_type and job_type in j.job_type.lower()]
        
        if "experience_level" in filters and filters["experience_level"]:
            exp_level = filters["experience_level"].lower()
            filtered = [j for j in filtered if j.experience_level and exp_level in j.experience_level.lower()]
        
        if "salary_min" in filters and filters["salary_min"]:
            min_salary = filters["salary_min"]
            filtered = [j for j in filtered if j.salary_max and j.salary_max >= min_salary]
        
        if "is_remote" in filters and filters["is_remote"] is not None:
            is_remote = filters["is_remote"]
            filtered = [j for j in filtered if j.is_remote == is_remote]
        
        return filtered
    
    @staticmethod
    def _calculate_next_trigger(frequency: str) -> datetime:
        """Calculate next trigger time based on frequency."""
        now = datetime.utcnow()
        
        if frequency == "hourly":
            return now + timedelta(hours=1)
        elif frequency == "daily":
            return now + timedelta(days=1)
        elif frequency == "weekly":
            return now + timedelta(weeks=1)
        else:
            return now + timedelta(days=1)
    
    async def send_alert_notification(self, alert: Alert, new_jobs_count: int, new_jobs: List[Any]) -> bool:
        """
        Send alert notification to user.
        
        Args:
            alert: Alert to send
            new_jobs_count: Number of new jobs found
            new_jobs: List of new jobs
        
        Returns:
            True if notification sent successfully
        """
        try:
            # This would integrate with email service
            # For now, just log the notification
            logger.info(f"Alert {alert.id} notification: {new_jobs_count} new jobs found for user {alert.user_id}")
            
            # Update new_jobs_count
            alert.new_jobs_count = new_jobs_count
            await self.db.commit()
            
            return True
        except Exception as e:
            logger.error(f"Error sending alert notification: {str(e)}")
            return False
    
    async def get_user_alerts(self, user_id: int) -> List[Alert]:
        """
        Get all alerts for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            List of user's alerts
        """
        try:
            # Try to get from cache
            cache_key = f"user_alerts:{user_id}"
            cached_result = await redis_client.get(cache_key)
            if cached_result:
                logger.info(f"Cache hit for user alerts: {user_id}")
                return cached_result
            
            alerts = await self.alert_repo.get_by_user_id(user_id)
            
            # Cache the result
            await redis_client.set(cache_key, alerts, ttl=1800)  # Cache for 30 minutes
            
            return alerts
        except Exception as e:
            logger.error(f"Error getting user alerts: {str(e)}")
            return []
    
    async def create_alert(self, user_id: int, alert_data: Dict[str, Any]) -> Optional[Alert]:
        """
        Create a new alert for a user.
        
        Args:
            user_id: User ID
            alert_data: Alert data
        
        Returns:
            Created alert or None if failed
        """
        try:
            alert = Alert(
                user_id=user_id,
                query=alert_data.get("query"),
                frequency=alert_data.get("frequency", "daily"),
                filters=alert_data.get("filters", {}),
                is_active=alert_data.get("is_active", True),
                created_at=datetime.utcnow(),
                next_trigger=self._calculate_next_trigger(alert_data.get("frequency", "daily")),
            )
            
            await self.alert_repo.create(alert)
            await self.db.commit()
            
            # Invalidate user alerts cache
            cache_key = f"user_alerts:{user_id}"
            await redis_client.delete(cache_key)
            
            logger.info(f"Alert created for user {user_id}: {alert.query}")
            return alert
        except Exception as e:
            logger.error(f"Error creating alert: {str(e)}")
            return None
    
    async def update_alert(self, alert_id: int, alert_data: Dict[str, Any]) -> bool:
        """
        Update an existing alert.
        
        Args:
            alert_id: Alert ID
            alert_data: Updated alert data
        
        Returns:
            True if updated successfully
        """
        try:
            alert = await self.alert_repo.get_by_id(alert_id)
            if alert:
                if "query" in alert_data:
                    alert.query = alert_data["query"]
                if "frequency" in alert_data:
                    alert.frequency = alert_data["frequency"]
                if "filters" in alert_data:
                    alert.filters = alert_data["filters"]
                if "is_active" in alert_data:
                    alert.is_active = alert_data["is_active"]
                
                await self.db.commit()
                
                # Invalidate user alerts cache
                cache_key = f"user_alerts:{alert.user_id}"
                await redis_client.delete(cache_key)
                
                logger.info(f"Alert {alert_id} updated")
                return True
        except Exception as e:
            logger.error(f"Error updating alert: {str(e)}")
        
        return False
    
    async def delete_alert(self, alert_id: int) -> bool:
        """
        Delete an alert.
        
        Args:
            alert_id: Alert ID
        
        Returns:
            True if deleted successfully
        """
        try:
            alert = await self.alert_repo.get_by_id(alert_id)
            if alert:
                user_id = alert.user_id
                await self.alert_repo.delete(alert_id)
                await self.db.commit()
                
                # Invalidate user alerts cache
                cache_key = f"user_alerts:{user_id}"
                await redis_client.delete(cache_key)
                
                logger.info(f"Alert {alert_id} deleted")
                return True
        except Exception as e:
            logger.error(f"Error deleting alert: {str(e)}")
        
        return False
