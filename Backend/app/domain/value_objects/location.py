"""
Location Value Object

Immutable representation of job location with remote work type.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class RemoteType(Enum):
    """Remote work type enumeration"""
    
    ON_SITE = 0
    REMOTE = 1
    HYBRID = 2
    
    @classmethod
    def from_int(cls, value: int) -> "RemoteType":
        """Convert integer to RemoteType"""
        try:
            return cls(value)
        except ValueError:
            return cls.ON_SITE
    
    @classmethod
    def from_string(cls, remote_str: Optional[str]) -> "RemoteType":
        """
        Parse remote type from string.
        
        Args:
            remote_str: Remote type string
        
        Returns:
            RemoteType enum value
        """
        if not remote_str:
            return cls.ON_SITE
        
        remote_lower = remote_str.lower().strip()
        
        # Remote variations
        if "remote" in remote_lower and "hybrid" not in remote_lower:
            return cls.REMOTE
        
        # Hybrid variations
        if "hybrid" in remote_lower:
            return cls.HYBRID
        
        # On-site variations
        if any(term in remote_lower for term in ["on-site", "onsite", "office", "in-person"]):
            return cls.ON_SITE
        
        return cls.ON_SITE


@dataclass(frozen=True)
class Location:
    """
    Immutable location value object.
    
    Attributes:
        city: City name
        country: Country name
        remote_type: Type of remote work
        full_address: Complete address string
    """
    
    city: Optional[str]
    country: Optional[str]
    remote_type: RemoteType
    full_address: Optional[str] = None
    
    def __post_init__(self):
        """Validate location"""
        # At least one location identifier should be present
        if not any([self.city, self.country, self.full_address]):
            if self.remote_type != RemoteType.REMOTE:
                raise ValueError("Location must have at least city, country, or full address")
    
    @classmethod
    def from_string(
        cls,
        location_str: str,
        remote_type: RemoteType = RemoteType.ON_SITE
    ) -> "Location":
        """
        Parse location from string.
        
        Handles formats like:
        - "San Francisco, CA"
        - "New York, United States"
        - "London, UK"
        - "Remote"
        - "Hybrid - San Francisco"
        
        Args:
            location_str: Location string
            remote_type: Remote work type
        
        Returns:
            Location instance
        """
        if not location_str or not location_str.strip():
            return cls(None, None, RemoteType.REMOTE if remote_type == RemoteType.REMOTE else RemoteType.ON_SITE)
        
        location_str = location_str.strip()
        
        # Check for remote indicators in location string
        location_lower = location_str.lower()
        if "remote" in location_lower and "hybrid" not in location_lower:
            remote_type = RemoteType.REMOTE
        elif "hybrid" in location_lower:
            remote_type = RemoteType.HYBRID
        
        # Parse city and country
        parts = [p.strip() for p in location_str.split(',')]
        
        if len(parts) >= 2:
            city = parts[0]
            country = parts[-1]
            return cls(city, country, remote_type, location_str)
        elif len(parts) == 1:
            # Single part - could be city or country
            return cls(parts[0], None, remote_type, location_str)
        
        return cls(None, None, remote_type, location_str)
    
    @classmethod
    def remote(cls) -> "Location":
        """Create a remote location"""
        return cls(None, None, RemoteType.REMOTE, "Remote")
    
    @classmethod
    def hybrid(cls, city: Optional[str] = None, country: Optional[str] = None) -> "Location":
        """Create a hybrid location"""
        full_address = f"Hybrid - {city}" if city else "Hybrid"
        return cls(city, country, RemoteType.HYBRID, full_address)
    
    def is_remote(self) -> bool:
        """Check if location is fully remote"""
        return self.remote_type == RemoteType.REMOTE
    
    def is_hybrid(self) -> bool:
        """Check if location is hybrid"""
        return self.remote_type == RemoteType.HYBRID
    
    def is_on_site(self) -> bool:
        """Check if location is on-site"""
        return self.remote_type == RemoteType.ON_SITE
    
    def matches_location(self, search_location: str) -> bool:
        """
        Check if this location matches a search location.
        
        Args:
            search_location: Location to search for
        
        Returns:
            True if matches, False otherwise
        """
        search_lower = search_location.lower()
        
        # Country code mappings for better matching
        country_mappings = {
            'united states': ['us', 'usa', 'united states', 'america'],
            'united kingdom': ['uk', 'gb', 'united kingdom', 'britain'],
            'united arab emirates': ['uae', 'united arab emirates', 'dubai', 'abu dhabi'],
            'saudi arabia': ['sa', 'saudi', 'saudi arabia', 'ksa'],
            'egypt': ['egypt', 'eg', 'cairo'],
            'india': ['india', 'in'],
            'canada': ['canada', 'ca'],
            'germany': ['germany', 'de'],
            'singapore': ['singapore', 'sg'],
            'australia': ['australia', 'au', 'aus']
        }
        
        # Check if search location is a known country
        for country_name, aliases in country_mappings.items():
            if search_lower in aliases or search_lower == country_name:
                # Check if any alias matches this location
                location_lower = self.format().lower()
                for alias in aliases:
                    if alias in location_lower:
                        return True
        
        # Fallback to substring matching
        if self.city and search_lower in self.city.lower():
            return True
        
        if self.country and search_lower in self.country.lower():
            return True
        
        if self.full_address and search_lower in self.full_address.lower():
            return True
        
        return False
    
    def format(self) -> str:
        """
        Format location for display.
        
        Returns:
            Formatted location string
        """
        if self.full_address:
            return self.full_address
        
        if self.is_remote():
            return "Remote"
        
        parts = []
        if self.city:
            parts.append(self.city)
        if self.country:
            parts.append(self.country)
        
        location_str = ", ".join(parts) if parts else "Location not specified"
        
        if self.is_hybrid():
            return f"Hybrid - {location_str}"
        
        return location_str
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {
            "city": self.city,
            "country": self.country,
            "remote_type": self.remote_type.value,
            "full_address": self.full_address,
        }
    
    def __str__(self) -> str:
        return self.format()
