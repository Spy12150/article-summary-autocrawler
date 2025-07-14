import json
import os
import sys
from process_articles import load_articles, process_single_article

"""Test script for process_articles.py functionality"""

def test_basic_functionality():
    """Test basic loading and processing functionality"""
    print("Testing process_articles.py functionality...")
    
    # Check if we have any data files
    data_dir = "data"
    if not os.path.exists(data_dir):
        print(f"❌ Data directory '{data_dir}' not found")
        return False
    
    # Look for existing article files
    article_files = [f for f in os.listdir(data_dir) if f.startswith('article_data') and f.endswith('.json')]
    
    if not article_files:
        print("❌ No article data files found in data/ directory")
        return False
    
    # Use the first available file
    test_file = os.path.join(data_dir, article_files[0])
    print(f"✅ Using test file: {test_file}")
    
    # Test loading articles
    try:
        articles = load_articles(test_file)
        print(f"✅ Successfully loaded {len(articles)} articles")
        
        if articles:
            # Show first article info
            first_article = articles[0]
            print(f"✅ First article headline: {first_article.get('headline', 'No headline')}")
            print(f"✅ First article content length: {len(first_article.get('content', ''))}")
            
            # Test single article processing (with mock/fallback)
            print("\n🧪 Testing single article processing (will use fallback due to mock API)...")
            processed = process_single_article(
                first_article,
                "mock_api_key",
                "mock_model",
                "mock_endpoint"
            )
            
            print(f"✅ Processing status: {processed.get('processing_status')}")
            print(f"✅ Sentiment: {processed.get('sentiment')}")
            print(f"✅ Summary: {processed.get('summary')}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def show_usage():
    """Show usage examples"""
    print("\n" + "="*60)
    print("USAGE EXAMPLES:")
    print("="*60)
    print("# Process articles with default settings:")
    print("python process_articles.py")
    print()
    print("# Process specific file:")
    print("python process_articles.py --input data/article_data9.json")
    print()
    print("# Use custom model and API key:")
    print("python process_articles.py --model 'Deepseek-r1:32b' --key 'your_api_key_here'")
    print()
    print("# Full custom command:")
    print("python process_articles.py \\")
    print("    --input data/article_data9.json \\")
    print("    --output data/processed_articles.json \\")
    print("    --model 'Deepseek-r1:32b' \\")
    print("    --key 'your_api_key_here' \\")
    print("    --endpoint 'http://10.30.15.111:8080/v1/chat/completions'")

if __name__ == "__main__":
    print("🚀 Testing Phase 2 Article Processing")
    print("="*50)
    
    success = test_basic_functionality()
    
    if success:
        print("\n✅ All tests passed!")
        show_usage()
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
