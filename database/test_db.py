"""
Database Testing Script
Tests all database operations and validates the setup.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from database.db_manager import DatabaseManager


def test_database_operations():
    """
    Comprehensive test of all database operations.
    """
    print("🧪 Database Testing Suite")
    print("=" * 40)
    
    # Get database credentials
    print("\n📋 Enter your MySQL credentials:")
    password = input("MySQL Password: ").strip()
    
    if not password:
        print("❌ Password required for testing!")
        return False
    
    # Initialize database manager
    db = DatabaseManager(password=password)
    
    # Test 1: Connection
    print("\n1️⃣  Testing database connection...")
    if not db.test_connection():
        print("❌ Connection test failed!")
        return False
    print("✅ Connection successful!")
    
    # Test 2: Count articles
    print("\n2️⃣  Testing article count...")
    count = db.count_articles()
    print(f"📊 Current article count: {count}")
    
    # Test 3: Insert test article
    print("\n3️⃣  Testing article insertion...")
    test_article = {
        'date': '2025-01-01',
        'headline': 'Test Article for Database Validation',
        'article_url': 'https://example.com/test-article',
        'source_url': 'https://example.com/source',
        'content_hash': 'test_hash_12345',
        'quality_score': 8,
        'quality_factors': ['excellent_length', 'technical_content', 'has_date'],
        'content_length': 1500,
        'sentence_count': 15,
        'tech_keyword_count': 5,
        'sentiment': '中性',
        'summary': '这是一篇用于测试数据库功能的测试文章。',
        'relevant': '是',
        'processing_status': 'success'
    }
    
    if db.insert_article(test_article):
        print("✅ Article insertion successful!")
    else:
        print("❌ Article insertion failed!")
        return False
    
    # Test 4: Retrieve by hash
    print("\n4️⃣  Testing article retrieval by hash...")
    retrieved = db.get_article_by_hash('test_hash_12345')
    if retrieved:
        print(f"✅ Retrieved article: {retrieved['headline']}")
        print(f"   Quality factors: {retrieved['quality_factors']}")
    else:
        print("❌ Failed to retrieve article!")
        return False
    
    # Test 5: Get recent articles
    print("\n5️⃣  Testing recent articles retrieval...")
    recent = db.get_recent_articles(3)
    print(f"📰 Found {len(recent)} recent articles:")
    for i, article in enumerate(recent, 1):
        print(f"   {i}. {article['headline'][:50]}...")
    
    # Test 6: Date range query
    print("\n6️⃣  Testing date range query...")
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    articles_in_range = db.get_articles_by_date_range(yesterday, today)
    print(f"📅 Articles from {yesterday} to {today}: {len(articles_in_range)}")
    
    # Test 7: Clean up test data
    print("\n7️⃣  Cleaning up test data...")
    if db.delete_article_by_hash('test_hash_12345'):
        print("✅ Test article deleted successfully!")
    else:
        print("❌ Failed to delete test article!")
    
    # Final count
    final_count = db.count_articles()
    print(f"\n📊 Final article count: {final_count}")
    
    # Disconnect
    db.disconnect()
    
    print("\n🎉 All tests completed successfully!")
    return True


def quick_status_check():
    """
    Quick database status check without modifying data.
    """
    print("🔍 Quick Database Status Check")
    print("=" * 35)
    
    password = input("MySQL Password: ").strip()
    if not password:
        print("❌ Password required!")
        return
    
    db = DatabaseManager(password=password)
    
    if not db.test_connection():
        print("❌ Database connection failed!")
        return
    
    # Get basic stats
    total_count = db.count_articles()
    recent_articles = db.get_recent_articles(5)
    
    print(f"\n📊 Database Statistics:")
    print(f"   Total articles: {total_count}")
    print(f"   Recent articles (last 5):")
    
    for i, article in enumerate(recent_articles, 1):
        date = article.get('date', 'Unknown')
        headline = article.get('headline', 'No headline')[:40]
        quality = article.get('quality_score', 'N/A')
        print(f"   {i}. [{date}] {headline}... (Q:{quality})")
    
    db.disconnect()
    print("\n✅ Status check completed!")


def main():
    """
    Main testing interface.
    """
    print("🧪 Database Testing Tool")
    print("Choose an option:")
    print("1. Full test suite (recommended for first setup)")
    print("2. Quick status check")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        test_database_operations()
    elif choice == '2':
        quick_status_check()
    elif choice == '3':
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice!")


if __name__ == "__main__":
    main()
