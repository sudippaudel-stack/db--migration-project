"""
Legacy Migration Tool - Database migration utility for legacy to new schema migration.

This package provides a comprehensive CLI tool for migrating data from legacy
database schemas to new improved schemas with data validation, transformation,
and seeding capabilities.
"""

__version__ = "1.0.0"
__author__ = "Your Team"
__description__ = "Legacy Database Migration Tool"

from config.settings import settings
from services.database import db_manager, get_db_manager
from utils.logger import get_logger, logger

__all__ = [
    "__version__",
    "db_manager",
    "get_db_manager",
    "get_logger",
    "logger",
    "settings",
]
