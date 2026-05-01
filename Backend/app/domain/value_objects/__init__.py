"""
Value Objects - Immutable domain concepts

Value objects are defined by their attributes, not identity.
They are immutable and contain validation logic.
"""

from .salary import Salary
from .location import Location
from .job_type import JobType
from .experience_level import ExperienceLevel
from .date_range import DateRange

__all__ = [
    "Salary",
    "Location",
    "JobType",
    "ExperienceLevel",
    "DateRange",
]
