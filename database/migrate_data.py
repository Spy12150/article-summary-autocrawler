"""
Migration Script: JSON to MySQL
Migrates existing article data from JSON files to MySQL database.
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from database.db_manager import DatabaseManager, migrate_json_to_mysql


def main():
    """
    Main migration function.
    """
    print("🚀 Article Summary Database Migration Tool")
    print("=" * 50)
    
    # Get database credentials
    print("\n📋 Database Configuration:")
    print("Enter your MySQL connection details:")
    
    host = input("MySQL Host (default: localhost): ").strip() or "localhost"
    port = input("MySQL Port (default: 3306): ").strip() or "3306"
    database = input("Database Name (default: article_summary_db): ").strip() or "article_summary_db"
    username = input("MySQL Username (default: article_user): ").strip() or "article_user"
    password = input("MySQL Password: ").strip()
    
    if not password:
        print("❌ Password is required!")
        return
    
    # Initialize database manager
    db_manager = DatabaseManager(
        host=host,
        database=database,
        user=username,
        password=password,
        port=int(port)
    )
    
    # Test connection
    print("\n🔌 Testing database connection...")
    if not db_manager.test_connection():
        print("❌ Database connection failed!")
        print("\n🔧 Troubleshooting steps:")
        print("1. Ensure MySQL server is running")
        print("2. Check your credentials")
        print("3. Run the setup.sql script in MySQL Workbench first")
        print("4. Verify the database and user exist")
        return
    
    print("✅ Database connection successful!")
    
    # Find JSON files to migrate
    data_dir = project_root / "data"
    json_files = []
    
    if (data_dir / "articles_processed.json").exists():
        json_files.append(data_dir / "articles_processed.json")
    
    if (data_dir / "article_data.json").exists():
        json_files.append(data_dir / "article_data.json")
    
    if not json_files:
        print("❌ No JSON files found in the data directory!")
        return
    
    print(f"\n📁 Found {len(json_files)} JSON file(s) to migrate:")
    for i, file_path in enumerate(json_files, 1):
        print(f"  {i}. {file_path.name}")
    
    # Check current database state
    current_count = db_manager.count_articles()
    print(f"\n📊 Current articles in database: {current_count}")
    
    if current_count > 0:
        overwrite = input("\n⚠️  Database already contains articles. Continue anyway? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Migration cancelled.")
            return
    
    # Migrate each file
    total_migrated = 0
    for json_file in json_files:
        print(f"\n📄 Migrating {json_file.name}...")
        
        try:
            # Load and preview JSON data
            with open(json_file, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            
            print(f"  📊 Found {len(articles)} articles in {json_file.name}")
            
            # Show sample article
            if articles:
                sample = articles[0]
                print(f"  📰 Sample: {sample.get('headline', 'No headline')[:60]}...")
            
            # Migrate
            if migrate_json_to_mysql(str(json_file), db_manager):
                print(f"  ✅ Successfully migrated {json_file.name}")
                total_migrated += len(articles)
            else:
                print(f"  ❌ Failed to migrate {json_file.name}")
        
        except Exception as e:
            print(f"  ❌ Error processing {json_file.name}: {e}")
    
    # Final summary
    print(f"\n🎉 Migration Summary:")
    print(f"  📊 Total articles migrated: {total_migrated}")
    print(f"  📋 Final database count: {db_manager.count_articles()}")
    
    # Show recent articles
    print(f"\n📰 Recent articles in database:")
    recent_articles = db_manager.get_recent_articles(5)
    for i, article in enumerate(recent_articles, 1):
        date = article.get('date', 'No date')
        headline = article.get('headline', 'No headline')[:60]
        quality_score = article.get('quality_score', 'N/A')
        print(f"  {i}. [{date}] {headline}... (Quality: {quality_score})")
    
    # Cleanup
    db_manager.disconnect()
    print("\n✅ Migration completed successfully!")


if __name__ == "__main__":
    main()
