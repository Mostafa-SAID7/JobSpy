from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class SavedJob:
    """
    Domain entity representing a Saved Job.
    """
    
    user_id: UUID
    job_id: UUID
    id: UUID = field(default_factory=uuid4)
    notes: Optional[str] = None
    saved_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def update_notes(self, notes: str):
        """Update notes for the saved job."""
        self.notes = notes
        self.updated_at = datetime.utcnow()
