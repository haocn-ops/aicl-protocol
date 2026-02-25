"""
AICL - Agent Intent Communication Language

A structured communication protocol for AI agents and human-agent collaboration.
"""

__version__ = "1.0.0"

from .parser import parse_fields, parse_file
from .validator import validate_message, ValidationError

__all__ = [
    "parse_fields",
    "parse_file", 
    "validate_message",
    "ValidationError",
]
