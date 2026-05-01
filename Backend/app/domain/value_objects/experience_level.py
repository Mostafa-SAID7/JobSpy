"""
Experience Level Value Object

Enumeration of experience levels with normalization logic.
"""

from enum import Enum
from typing import Optional


class ExperienceLevel(Enum):
    """
    Experience level enumeration.
    
    Standardized experience levels across all job sources.
    """
    
    ENTRY = "Entry Level"
    MID = "Mid Level"
    SENIOR = "Senior Level"
    LEAD = "Lead"
    EXECUTIVE = "Executive"
    UNKNOWN = "Unknown"
    
    @classmethod
    def from_string(cls, experience_str: Optional[str]) -> "ExperienceLevel":
        """
        Normalize experience level string to enum value.
        
        Handles various formats:
        - "Entry", "Junior", "Graduate", "0-2 years"
        - "Mid", "Intermediate", "2-5 years"
        - "Senior", "5+ years", "5-10 years"
        - "Lead", "Staff", "Principal"
        - "Executive", "Director", "Manager", "VP", "C-level"
        
        Args:
            experience_str: Experience level string from source
        
        Returns:
            ExperienceLevel enum value
        """
        if not experience_str:
            return cls.UNKNOWN
        
        exp_lower = experience_str.lower().strip()
        
        # Entry level variations
        if any(term in exp_lower for term in [
            "entry", "junior", "graduate", "0-2", "0-1", "fresher", "beginner"
        ]):
            return cls.ENTRY
        
        # Mid level variations
        if any(term in exp_lower for term in [
            "mid", "intermediate", "2-5", "3-5", "2-4", "mid-level"
        ]):
            return cls.MID
        
        # Senior level variations
        if any(term in exp_lower for term in [
            "senior", "5+", "5-10", "7+", "experienced", "sr."
        ]):
            return cls.SENIOR
        
        # Lead variations
        if any(term in exp_lower for term in [
            "lead", "staff", "principal", "architect"
        ]):
            return cls.LEAD
        
        # Executive variations
        if any(term in exp_lower for term in [
            "executive", "director", "manager", "vp", "vice president",
            "c-level", "cto", "ceo", "cfo", "head of"
        ]):
            return cls.EXECUTIVE
        
        return cls.UNKNOWN
    
    def years_range(self) -> tuple[int, Optional[int]]:
        """
        Get typical years of experience range for this level.
        
        Returns:
            Tuple of (min_years, max_years). max_years is None for open-ended.
        """
        ranges = {
            ExperienceLevel.ENTRY: (0, 2),
            ExperienceLevel.MID: (2, 5),
            ExperienceLevel.SENIOR: (5, 10),
            ExperienceLevel.LEAD: (8, 15),
            ExperienceLevel.EXECUTIVE: (10, None),
            ExperienceLevel.UNKNOWN: (0, None),
        }
        return ranges[self]
    
    def is_senior_or_above(self) -> bool:
        """Check if experience level is senior or above"""
        return self in (ExperienceLevel.SENIOR, ExperienceLevel.LEAD, ExperienceLevel.EXECUTIVE)
    
    def __str__(self) -> str:
        return self.value
