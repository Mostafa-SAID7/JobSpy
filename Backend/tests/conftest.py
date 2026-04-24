"""
Pytest configuration and fixtures
"""
import sys
import os
from pathlib import Path

# Add the Backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))
