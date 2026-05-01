"""
Salary Value Object

Immutable representation of salary with validation and parsing logic.
"""

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Optional


@dataclass(frozen=True)
class Salary:
    """
    Immutable salary value object.
    
    Attributes:
        min_amount: Minimum salary amount
        max_amount: Maximum salary amount
        currency: Currency code (ISO 4217)
    
    Invariants:
        - min_amount cannot exceed max_amount
        - Amounts cannot be negative
        - Currency must be valid ISO code
    """
    
    min_amount: Optional[Decimal]
    max_amount: Optional[Decimal]
    currency: str = "USD"
    
    def __post_init__(self):
        """Validate salary invariants"""
        # Validate amounts
        if self.min_amount is not None and self.min_amount < 0:
            raise ValueError("Minimum salary cannot be negative")
        
        if self.max_amount is not None and self.max_amount < 0:
            raise ValueError("Maximum salary cannot be negative")
        
        if self.min_amount and self.max_amount:
            if self.min_amount > self.max_amount:
                raise ValueError(
                    f"Minimum salary ({self.min_amount}) cannot exceed "
                    f"maximum salary ({self.max_amount})"
                )
        
        # Validate currency
        if not self.currency or len(self.currency) != 3:
            raise ValueError(f"Invalid currency code: {self.currency}")
    
    @classmethod
    def from_string(cls, salary_str: str, currency: str = "USD") -> "Salary":
        """
        Parse salary from various string formats.
        
        Supported formats:
            - "$50,000 - $80,000"
            - "50k-80k"
            - "50000-80000"
            - "Up to $100,000"
            - "From $50,000"
            - "$75,000"
        
        Args:
            salary_str: Salary string to parse
            currency: Currency code (default: USD)
        
        Returns:
            Salary instance
        
        Raises:
            ValueError: If string cannot be parsed
        """
        if not salary_str or not salary_str.strip():
            return cls(None, None, currency)
        
        # Remove currency symbols and normalize
        cleaned = re.sub(r'[$£€¥₹,\s]', '', salary_str.lower())
        
        # Handle range format (e.g., "50000-80000" or "50k-80k")
        if '-' in cleaned and 'up' not in salary_str.lower():
            parts = cleaned.split('-')
            if len(parts) == 2:
                min_amt = cls._parse_amount(parts[0])
                max_amt = cls._parse_amount(parts[1])
                return cls(min_amt, max_amt, currency)
        
        # Handle "up to" format
        if 'up to' in salary_str.lower() or 'upto' in salary_str.lower():
            max_amt = cls._parse_amount(cleaned)
            return cls(None, max_amt, currency)
        
        # Handle "from" format
        if 'from' in salary_str.lower():
            min_amt = cls._parse_amount(cleaned)
            return cls(min_amt, None, currency)
        
        # Single value - treat as exact or max
        amount = cls._parse_amount(cleaned)
        return cls(amount, amount, currency)
    
    @staticmethod
    def _parse_amount(amount_str: str) -> Optional[Decimal]:
        """
        Parse amount string handling k/K suffix for thousands.
        
        Args:
            amount_str: Amount string (e.g., "50k", "50000")
        
        Returns:
            Decimal amount or None
        """
        if not amount_str or amount_str.strip() == '':
            return None
        
        amount_str = amount_str.strip().lower()
        
        try:
            # Handle 'k' suffix for thousands
            if 'k' in amount_str:
                base = amount_str.replace('k', '')
                return Decimal(base) * 1000
            
            # Handle 'm' suffix for millions
            if 'm' in amount_str:
                base = amount_str.replace('m', '')
                return Decimal(base) * 1_000_000
            
            # Direct number
            return Decimal(amount_str)
        
        except (InvalidOperation, ValueError):
            return None
    
    @classmethod
    def from_range(
        cls,
        min_amount: Optional[float],
        max_amount: Optional[float],
        currency: str = "USD"
    ) -> "Salary":
        """
        Create salary from numeric range.
        
        Args:
            min_amount: Minimum salary
            max_amount: Maximum salary
            currency: Currency code
        
        Returns:
            Salary instance
        """
        min_dec = Decimal(str(min_amount)) if min_amount is not None else None
        max_dec = Decimal(str(max_amount)) if max_amount is not None else None
        return cls(min_dec, max_dec, currency)
    
    def is_in_range(self, expected_salary: Decimal) -> bool:
        """
        Check if expected salary falls within this salary range.
        
        Args:
            expected_salary: Expected salary amount
        
        Returns:
            True if within range, False otherwise
        """
        if self.min_amount and expected_salary < self.min_amount:
            return False
        
        if self.max_amount and expected_salary > self.max_amount:
            return False
        
        return True
    
    def meets_minimum(self, minimum_required: Decimal) -> bool:
        """
        Check if salary meets minimum requirement.
        
        Args:
            minimum_required: Minimum required salary
        
        Returns:
            True if meets minimum, False otherwise
        """
        if not self.max_amount:
            return False
        
        return self.max_amount >= minimum_required
    
    def format(self) -> str:
        """
        Format salary for display.
        
        Returns:
            Formatted salary string
        """
        if self.min_amount and self.max_amount:
            if self.min_amount == self.max_amount:
                return f"{self.currency} {self.min_amount:,.0f}"
            return f"{self.currency} {self.min_amount:,.0f} - {self.max_amount:,.0f}"
        
        if self.max_amount:
            return f"Up to {self.currency} {self.max_amount:,.0f}"
        
        if self.min_amount:
            return f"From {self.currency} {self.min_amount:,.0f}"
        
        return "Salary not specified"
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {
            "min_amount": float(self.min_amount) if self.min_amount else None,
            "max_amount": float(self.max_amount) if self.max_amount else None,
            "currency": self.currency,
        }
