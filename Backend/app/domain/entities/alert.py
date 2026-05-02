from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4


@dataclass
class Alert:
    """
    Domain entity representing a Job Alert.
    """
    
    user_id: UUID
    name: str
    query: str
    frequency: str  # "hourly", "daily", "weekly"
    notification_method: str  # "email", "in_app", "both"
    id: UUID = field(default_factory=uuid4)
    filters: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    last_triggered: Optional[datetime] = None
    next_trigger: Optional[datetime] = None
    new_jobs_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def trigger(self, new_jobs_count: int):
        """Mark alert as triggered."""
        self.last_triggered = datetime.utcnow()
        self.new_jobs_count = new_jobs_count
        self.updated_at = datetime.utcnow()

    def deactivate(self):
        """Deactivate the alert."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
