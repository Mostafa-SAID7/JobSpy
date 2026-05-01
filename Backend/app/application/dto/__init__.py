"""
Data Transfer Objects (DTOs)

DTOs are used to transfer data between layers.
They are simple data containers with no business logic.
"""

from .job_dto import JobDTO, JobListDTO
from .search_dto import SearchRequestDTO, SearchResponseDTO

__all__ = [
    "JobDTO",
    "JobListDTO",
    "SearchRequestDTO",
    "SearchResponseDTO",
]
