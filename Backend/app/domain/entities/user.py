from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class User:
    """
    Domain entity representing a User.
    """
    
    email: str
    full_name: str
    hashed_password: str
    id: UUID = field(default_factory=uuid4)
    username: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    def verify(self):
        """Verify the user."""
        self.is_verified = True
        self.updated_at = datetime.utcnow()

    def deactivate(self):
        """Deactivate the user."""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
