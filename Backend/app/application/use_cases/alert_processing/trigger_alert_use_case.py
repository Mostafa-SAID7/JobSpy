"""
Trigger Alert Use Case

Handles triggering an alert and searching for new jobs matching the alert criteria.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging
from uuid import UUID

from app.domain.entities.alert import Alert
from app.domain.interfaces.repositories import IAlertRepository, IJobRepository
from app.domain.services.job_filtering_service import JobFilteringService

logger = logging.getLogger(__name__)


class TriggerAlertUseCase:
    """Use case for triggering an alert and finding matching jobs."""

    def __init__(
        self,
        alert_repository: IAlertRepository,
        job_repository: IJobRepository,
        filtering_service: JobFilteringService,
    ):
        """
        Initialize the use case.

        Args:
            alert_repository: Repository for alert operations
            job_repository: Repository for job operations
            filtering_service: Domain service for filtering jobs
        """
        self._alert_repository = alert_repository
        self._job_repository = job_repository
        self._filtering_service = filtering_service

    async def execute(self, alert: Alert) -> Dict[str, Any]:
        """
        Trigger an alert and search for new jobs.

        Args:
            alert: Alert to trigger

        Returns:
            Dictionary with alert trigger results including new jobs count
        """
        try:
            # Search for jobs matching alert criteria
            jobs = await self._job_repository.search(alert.query)
            
            # Filter by additional criteria if provided
            if alert.filters:
                jobs = self._filtering_service.filter_jobs(jobs, alert.filters)
            
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
            
            # Update alert trigger info via domain entity
            alert.trigger(new_jobs_count)
            next_trigger = self._calculate_next_trigger(alert.frequency)
            alert.next_trigger = next_trigger
            await self._alert_repository.update(alert)
            
            logger.info(f"Alert {alert.id} triggered: {new_jobs_count} new jobs found")
            
            return {
                "alert_id": str(alert.id),
                "new_jobs_count": new_jobs_count,
                "new_jobs": new_jobs,
                "next_trigger": next_trigger,
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error triggering alert {alert.id}: {str(e)}")
            return {
                "alert_id": str(alert.id),
                "new_jobs_count": 0,
                "new_jobs": [],
                "success": False,
                "error": str(e),
            }

    @staticmethod
    def _calculate_next_trigger(frequency: str) -> datetime:
        """
        Calculate next trigger time based on frequency.

        Args:
            frequency: Alert frequency (hourly, daily, weekly)

        Returns:
            Next trigger datetime
        """
        now = datetime.utcnow()
        
        if frequency == "hourly":
            return now + timedelta(hours=1)
        elif frequency == "daily":
            return now + timedelta(days=1)
        elif frequency == "weekly":
            return now + timedelta(weeks=1)
        else:
            return now + timedelta(days=1)
