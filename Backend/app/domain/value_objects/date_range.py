"""
Date Range Value Object

Immutable representation of a date range.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass(frozen=True)
class DateRange:
    """
    Immutable date range value object.
    
    Attributes:
        start_date: Start date of range
        end_date: End date of range
    
    Invariants:
        - start_date cannot be after end_date
    """
    
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    
    def __post_init__(self):
        """Validate date range"""
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValueError(
                    f"Start date ({self.start_date}) cannot be after "
                    f"end date ({self.end_date})"
                )
    
    @classmethod
    def from_days(cls, days: int, end_date: Optional[datetime] = None) -> "DateRange":
        """
        Create date range from number of days.
        
        Args:
            days: Number of days in range
            end_date: End date (default: now)
        
        Returns:
            DateRange instance
        """
        if end_date is None:
            end_date = datetime.utcnow()
        
        start_date = end_date - timedelta(days=days)
        return cls(start_date, end_date)
    
    @classmethod
    def last_7_days(cls) -> "DateRange":
        """Create date range for last 7 days"""
        return cls.from_days(7)
    
    @classmethod
    def last_30_days(cls) -> "DateRange":
        """Create date range for last 30 days"""
        return cls.from_days(30)
    
    @classmethod
    def last_90_days(cls) -> "DateRange":
        """Create date range for last 90 days"""
        return cls.from_days(90)
    
    def contains(self, date: datetime) -> bool:
        """
        Check if date falls within this range.
        
        Args:
            date: Date to check
        
        Returns:
            True if date is within range, False otherwise
        """
        if self.start_date and date < self.start_date:
            return False
        
        if self.end_date and date > self.end_date:
            return False
        
        return True
    
    def overlaps(self, other: "DateRange") -> bool:
        """
        Check if this range overlaps with another range.
        
        Args:
            other: Other date range
        
        Returns:
            True if ranges overlap, False otherwise
        """
        if not self.start_date or not self.end_date:
            return True
        
        if not other.start_date or not other.end_date:
            return True
        
        return (
            self.start_date <= other.end_date and
            self.end_date >= other.start_date
        )
    
    def duration_days(self) -> Optional[int]:
        """
        Get duration of range in days.
        
        Returns:
            Number of days or None if range is open-ended
        """
        if not self.start_date or not self.end_date:
            return None
        
        return (self.end_date - self.start_date).days
    
    def format(self) -> str:
        """
        Format date range for display.
        
        Returns:
            Formatted date range string
        """
        if self.start_date and self.end_date:
            return f"{self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}"
        
        if self.start_date:
            return f"From {self.start_date.strftime('%Y-%m-%d')}"
        
        if self.end_date:
            return f"Until {self.end_date.strftime('%Y-%m-%d')}"
        
        return "All time"
    
    def __str__(self) -> str:
        return self.format()
