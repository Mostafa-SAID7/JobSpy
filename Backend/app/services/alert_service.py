"""
Alert Service - JobSpy (Refactored to Clean Architecture)

Alert service for JobSpy - now a thin wrapper around use cases.
This service is kept for backward compatibility with background jobs/schedulers.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.alert import Alert
from app.repositories.alert_repo import AlertRepository
from app.repositories.job_repo import JobRepository
from app.core.redis import redis_client
from app.domain.services.job_filtering_service import JobFilteringService
from app.application.use_cases.alert_processing.trigger_alert_use_case import TriggerAlertUseCase

logger = logging.getLogger(__name__)


class AlertService:
    """
    Service for handling alert operations.
    
    REFACTORED: Now uses Clean Architecture with use cases and domain services.
    This service is kept as a thin wrapper for backward compatibility with
    background jobs and schedulers.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.alert_repo = AlertRepository(db)
        self.job_repo = JobRepository(db)
        
        # Domain services
        self.filtering_service = JobFilteringService()
        
        # Use cases
        self.trigger_alert_use_case = TriggerAlertUseCase(
            alert_repository=self.alert_repo,
            job_repository=self.job_repo,
            filtering_service=self.filtering_service,
        )
    
    async def get_alerts_to_trigger(self) -> List[Alert]:
        """Get alerts that need to be triggered."""
        return await self.alert_repo.get_alerts_to_trigger()
    
    async def trigger_alert(self, alert: Alert) -> Dict[str, Any]:
        """
        Trigger an alert and search for new jobs.
        
        REFACTORED: Now delegates to TriggerAlertUseCase.
        
        Args:
            alert: Alert to trigger
        
        Returns:
            Dictionary with alert trigger results
        """
        result = await self.trigger_alert_use_case.execute(alert)
        await self.db.commit()
        return result
    
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
    
    async def get_user_alerts(self, user_id: UUID) -> List[Alert]:
        """
        Get all alerts for a user.
        
        DEPRECATED: Use ListAlertsUseCase instead.
        Kept for backward compatibility.
        
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
            
            alerts = await self.alert_repo.get_by_user(user_id)
            
            # Cache the result
            await redis_client.set(cache_key, alerts, ttl=1800)  # Cache for 30 minutes
            
            return alerts
        except Exception as e:
            logger.error(f"Error getting user alerts: {str(e)}")
            return []
    
    async def create_alert(self, user_id: UUID, alert_data: Dict[str, Any]) -> Optional[Alert]:
        """
        Create a new alert for a user.
        
        DEPRECATED: Use CreateAlertUseCase instead.
        Kept for backward compatibility.
        
        Args:
            user_id: User ID
            alert_data: Alert data
        
        Returns:
            Created alert or None if failed
        """
        try:
            from app.schemas.alert import AlertCreate
            
            alert_create = AlertCreate(**alert_data)
            alert = await self.alert_repo.create(user_id, alert_create)
            await self.db.commit()
            
            # Invalidate user alerts cache
            cache_key = f"user_alerts:{user_id}"
            await redis_client.delete(cache_key)
            
            logger.info(f"Alert created for user {user_id}: {alert.query}")
            return alert
        except Exception as e:
            logger.error(f"Error creating alert: {str(e)}")
            return None
    
    async def update_alert(self, alert_id: UUID, alert_data: Dict[str, Any]) -> bool:
        """
        Update an existing alert.
        
        DEPRECATED: Use UpdateAlertUseCase instead.
        Kept for backward compatibility.
        
        Args:
            alert_id: Alert ID
            alert_data: Updated alert data
        
        Returns:
            True if updated successfully
        """
        try:
            from app.schemas.alert import AlertUpdate
            
            alert_update = AlertUpdate(**alert_data)
            alert = await self.alert_repo.update(alert_id, alert_update)
            
            if alert:
                await self.db.commit()
                
                # Invalidate user alerts cache
                cache_key = f"user_alerts:{alert.user_id}"
                await redis_client.delete(cache_key)
                
                logger.info(f"Alert {alert_id} updated")
                return True
        except Exception as e:
            logger.error(f"Error updating alert: {str(e)}")
        
        return False
    
    async def delete_alert(self, alert_id: UUID) -> bool:
        """
        Delete an alert.
        
        DEPRECATED: Use DeleteAlertUseCase instead.
        Kept for backward compatibility.
        
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
