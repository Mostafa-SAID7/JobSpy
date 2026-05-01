"""
Domain Entities - Core business objects with identity

Entities are defined by their identity (ID), not their attributes.
They contain business logic and enforce invariants.
"""

from .job import Job

__all__ = ["Job"]
