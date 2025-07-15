#!/usr/bin/env python3
"""Simple test to debug the issue"""

import json
import os
import sys

def test_basic():
    print("Testing basic functionality...")
    
    # Test file reading
    input_file = "data/article_data.json"
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        return
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Successfully loaded {len(data)} articles")
        
        # Test first article
        if data:
            first_article = data[0]
            print(f"First article title: {first_article.get('headline', 'No title')}")
            print(f"Content length: {len(first_article.get('content', ''))}")
        
        # Test output
        output_file = "data/test_simple_output.json"
        sample_output = {
            "test": "success",
            "articles_count": len(data),
            "first_article": first_article.get('headline', 'No title') if data else None
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sample_output, f, indent=2, ensure_ascii=False)
        
        print(f"Test output written to {output_file}")
        
    except Exception as e:
        print(f"Error during test: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_basic()
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed!")
        sys.exit(1)
