import json
import os
import sys

# Add the current directory to Python path to import the module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from process_articles_sequential import process_articles

def test_sequential_processing():
    """Test the sequential processing with a single article."""
    try:
        # Use the single article test file
        input_file = "data/single_article_test.json"
        
        if not os.path.exists(input_file):
            print(f"Test file not found: {input_file}")
            return False
        
        print("Testing sequential processing...")
        
        # Process the articles
        process_articles(
            input_path=input_file,
            output_path="data/test_sequential_output.json",
            api_key="dummy_key",  # Use dummy key for testing
            model="test-model",
            endpoint="http://10.30.15.111:8080/api/chat/completions"
        )
        
        # Check if output file was created
        if os.path.exists("data/test_sequential_output.json"):
            print("✓ Sequential processing test completed successfully!")
            return True
        else:
            print("✗ Output file was not created")
            return False
            
    except Exception as e:
        print(f"✗ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_sequential_processing()
    sys.exit(0 if success else 1)
