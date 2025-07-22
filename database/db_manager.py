"""
Database Manager for Article Summary Pipeline
Handles MySQL database operations for storing and retrieving article data.
"""

import mysql.connector
from mysql.connector import Error
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages MySQL database connections and operations for article data.
    """
    
    def __init__(self, host='localhost', database='article_summary_db', 
                 user='article_user', password='your_password_here', port=3306):
        """
        Initialize database connection parameters.
        
        Args:
            host (str): MySQL server host (default: localhost)
            database (str): Database name
            user (str): MySQL username
            password (str): MySQL password
            port (int): MySQL port (default: 3306)
        """
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.connection = None
    
    def connect(self):
        """
        Establish connection to MySQL database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port,
                autocommit=True  # Enable autocommit for immediate data persistence
            )
            
            if self.connection.is_connected():
                logger.info(f"Successfully connected to MySQL database: {self.database}")
                return True
                
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            return False
    
    def disconnect(self):
        """Close the database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("MySQL connection closed")
    
    def test_connection(self):
        """
        Test database connection and verify tables exist.
        
        Returns:
            bool: True if connection and tables are valid
        """
        if not self.connect():
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # Check if tables exist
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            
            required_tables = ['articles', 'quality_factors']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                logger.error(f"Missing tables: {missing_tables}")
                logger.error("Please run the setup.sql script first!")
                return False
            
            logger.info("Database connection and tables verified successfully")
            return True
            
        except Error as e:
            logger.error(f"Error testing connection: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def insert_article(self, article_data: Dict) -> bool:
        """
        Insert a single article into the database.
        
        Args:
            article_data (Dict): Article data dictionary
            
        Returns:
            bool: True if insertion successful
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            
            # Insert into articles table
            article_query = """
            INSERT INTO articles (
                date, headline, article_url, source_url, content_hash,
                quality_score, content_length, sentence_count, tech_keyword_count,
                sentiment, summary, relevant, processing_status, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            
            article_values = (
                article_data.get('date'),
                article_data.get('headline'),
                article_data.get('article_url'),
                article_data.get('source_url'),
                article_data.get('content_hash'),
                article_data.get('quality_score'),
                article_data.get('content_length'),
                article_data.get('sentence_count'),
                article_data.get('tech_keyword_count'),
                article_data.get('sentiment'),
                article_data.get('summary'),
                article_data.get('relevant'),
                article_data.get('processing_status'),
                datetime.now()
            )
            
            cursor.execute(article_query, article_values)
            article_id = cursor.lastrowid
            
            # Insert quality factors
            quality_factors = article_data.get('quality_factors', [])
            if quality_factors:
                factor_query = """
                INSERT INTO quality_factors (article_id, factor_name)
                VALUES (%s, %s)
                """
                
                for factor in quality_factors:
                    cursor.execute(factor_query, (article_id, factor))
            
            logger.info(f"Successfully inserted article: {article_data.get('headline', 'Unknown')}")
            return True
            
        except Error as e:
            logger.error(f"Error inserting article: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def batch_insert_articles(self, articles: List[Dict]) -> Tuple[int, int]:
        """
        Insert multiple articles into the database.
        
        Args:
            articles (List[Dict]): List of article data dictionaries
            
        Returns:
            Tuple[int, int]: (successful_insertions, failed_insertions)
        """
        successful = 0
        failed = 0
        
        for article in articles:
            if self.insert_article(article):
                successful += 1
            else:
                failed += 1
        
        logger.info(f"Batch insert completed: {successful} successful, {failed} failed")
        return successful, failed
    
    def get_article_by_hash(self, content_hash: str) -> Optional[Dict]:
        """
        Retrieve an article by its content hash.
        
        Args:
            content_hash (str): The content hash to search for
            
        Returns:
            Dict or None: Article data if found
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return None
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
            SELECT a.*, GROUP_CONCAT(qf.factor_name) as quality_factors
            FROM articles a
            LEFT JOIN quality_factors qf ON a.id = qf.article_id
            WHERE a.content_hash = %s
            GROUP BY a.id
            """
            
            cursor.execute(query, (content_hash,))
            result = cursor.fetchone()
            
            if result and result['quality_factors']:
                result['quality_factors'] = result['quality_factors'].split(',')
            
            return result
            
        except Error as e:
            logger.error(f"Error retrieving article: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
    
    def get_articles_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Retrieve articles within a date range.
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            
        Returns:
            List[Dict]: List of article data
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
            SELECT a.*, GROUP_CONCAT(qf.factor_name) as quality_factors
            FROM articles a
            LEFT JOIN quality_factors qf ON a.id = qf.article_id
            WHERE a.date BETWEEN %s AND %s
            GROUP BY a.id
            ORDER BY a.date DESC
            """
            
            cursor.execute(query, (start_date, end_date))
            results = cursor.fetchall()
            
            # Convert quality_factors from string to list
            for result in results:
                if result['quality_factors']:
                    result['quality_factors'] = result['quality_factors'].split(',')
                else:
                    result['quality_factors'] = []
            
            return results
            
        except Error as e:
            logger.error(f"Error retrieving articles by date range: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def get_recent_articles(self, limit: int = 10) -> List[Dict]:
        """
        Get the most recently processed articles.
        
        Args:
            limit (int): Maximum number of articles to return
            
        Returns:
            List[Dict]: List of recent article data
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
            SELECT a.*, GROUP_CONCAT(qf.factor_name) as quality_factors
            FROM articles a
            LEFT JOIN quality_factors qf ON a.id = qf.article_id
            GROUP BY a.id
            ORDER BY a.created_at DESC
            LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            
            # Convert quality_factors from string to list
            for result in results:
                if result['quality_factors']:
                    result['quality_factors'] = result['quality_factors'].split(',')
                else:
                    result['quality_factors'] = []
            
            return results
            
        except Error as e:
            logger.error(f"Error retrieving recent articles: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def count_articles(self) -> int:
        """
        Get the total number of articles in the database.
        
        Returns:
            int: Total article count
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return 0
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM articles")
            count = cursor.fetchone()[0]
            return count
            
        except Error as e:
            logger.error(f"Error counting articles: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()
    
    def delete_article_by_hash(self, content_hash: str) -> bool:
        """
        Delete an article by its content hash.
        
        Args:
            content_hash (str): The content hash of the article to delete
            
        Returns:
            bool: True if deletion successful
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            
            # First get the article ID
            cursor.execute("SELECT id FROM articles WHERE content_hash = %s", (content_hash,))
            result = cursor.fetchone()
            
            if not result:
                logger.warning(f"Article with hash {content_hash} not found")
                return False
            
            article_id = result[0]
            
            # Delete quality factors first (due to foreign key constraint)
            cursor.execute("DELETE FROM quality_factors WHERE article_id = %s", (article_id,))
            
            # Delete the article
            cursor.execute("DELETE FROM articles WHERE id = %s", (article_id,))
            
            logger.info(f"Successfully deleted article with hash: {content_hash}")
            return True
            
        except Error as e:
            logger.error(f"Error deleting article: {e}")
            return False
        finally:
            if cursor:
                cursor.close()


def migrate_json_to_mysql(json_file_path: str, db_manager: DatabaseManager) -> bool:
    """
    Migrate existing JSON data to MySQL database.
    
    Args:
        json_file_path (str): Path to the JSON file containing article data
        db_manager (DatabaseManager): Initialized database manager instance
        
    Returns:
        bool: True if migration successful
    """
    try:
        # Load JSON data
        with open(json_file_path, 'r', encoding='utf-8') as file:
            articles = json.load(file)
        
        logger.info(f"Loaded {len(articles)} articles from JSON file")
        
        # Test database connection
        if not db_manager.test_connection():
            logger.error("Database connection test failed")
            return False
        
        # Migrate articles
        successful, failed = db_manager.batch_insert_articles(articles)
        
        logger.info(f"Migration completed: {successful} articles inserted, {failed} failed")
        return failed == 0
        
    except FileNotFoundError:
        logger.error(f"JSON file not found: {json_file_path}")
        return False
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON file: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during migration: {e}")
        return False


if __name__ == "__main__":
    """
    Example usage and testing
    """
    # Initialize database manager
    # IMPORTANT: Replace 'your_password_here' with your actual MySQL password
    db = DatabaseManager(password='your_password_here')
    
    # Test connection
    if db.test_connection():
        print("✅ Database connection successful!")
        
        # Get article count
        count = db.count_articles()
        print(f"📊 Total articles in database: {count}")
        
        # Get recent articles
        recent = db.get_recent_articles(5)
        print(f"📰 Recent articles: {len(recent)}")
        
        for article in recent:
            print(f"  - {article['headline'][:50]}...")
    
    else:
        print("❌ Database connection failed!")
        print("Make sure to:")
        print("1. Run the setup.sql script in MySQL Workbench")
        print("2. Update the password in this script")
        print("3. Ensure MySQL server is running")
    
    # Disconnect
    db.disconnect()
