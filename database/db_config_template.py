"""
Database Configuration Template
Copy this file to db_config.py and update with your MySQL credentials.
"""

# MySQL Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'database': 'article_summary_db',
    'user': 'article_user',
    'password': 'your_password_here',  # ⚠️ CHANGE THIS!
    'charset': 'utf8mb4',
    'use_unicode': True,
    'autocommit': True
}

# Connection Pool Settings (for production use)
POOL_CONFIG = {
    'pool_name': 'article_pool',
    'pool_size': 5,
    'pool_reset_session': True
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'database.log'
}

# Migration Settings
MIGRATION_CONFIG = {
    'batch_size': 100,
    'backup_json': True,
    'skip_duplicates': True
}
