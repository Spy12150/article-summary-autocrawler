"""
Database Package for Article Summary Pipeline
Provides MySQL integration for storing and retrieving article data.
"""

from .db_manager import DatabaseManager, migrate_json_to_mysql

__version__ = "1.0.0"
__all__ = ["DatabaseManager", "migrate_json_to_mysql"]
