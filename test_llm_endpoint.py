#!/usr/bin/env python3
"""
Quick LLM endpoint test script for the article processing system.
This script tests the LLM endpoint with a single high-quality article.
"""

import subprocess
import os
import json
import sys

def main():
    """Run a quick test of the LLM endpoint."""
    print("🧪 LLM Endpoint Test")
    print("=" * 50)
    
    # Check if the test file exists
    test_file = "data/single_article_test.json"
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        print("Please make sure the single article test file exists.")
        sys.exit(1)
    
    print(f"✅ Test file found: {test_file}")
    
    # Run the test
    print("\n🚀 Running LLM endpoint test...")
    cmd = [
        "C:/Users/MaximeWang/AppData/Local/Programs/Python/Python313/python.exe",
        "process_articles_improved.py",
        "--input", test_file,
        "--output", "data/llm_test_result.json",
        "--auto-filename",
        "--max-workers", "1"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ LLM endpoint test completed successfully!")
            
            # Find the generated filename
            output_file = None
            for line in result.stdout.split('\n'):
                if 'Results saved to:' in line:
                    output_file = line.split(':', 1)[1].strip()
                    break
            
            if output_file and os.path.exists(output_file):
                print(f"📄 Results saved to: {output_file}")
                
                # Read and display the result
                with open(output_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if data:
                    article = data[0]
                    print("\n📊 Analysis Results:")
                    print(f"   Headline: {article.get('headline', 'N/A')}")
                    print(f"   Quality Score: {article.get('quality_score', 'N/A')}/10")
                    print(f"   Sentiment: {article.get('sentiment', 'N/A')}")
                    print(f"   Relevant: {article.get('relevant', 'N/A')}")
                    print(f"   Status: {article.get('processing_status', 'N/A')}")
                    print(f"   Summary: {article.get('summary', 'N/A')}")
                    
                    # Check if it's using fallback
                    if article.get('processing_status') == 'fallback':
                        print("\n⚠️  Note: LLM endpoint failed, using fallback mock analysis")
                        print("   Please check your LLM server status")
                    elif article.get('processing_status') == 'success':
                        print("\n🎉 LLM endpoint is working correctly!")
                        print("   Summary is in Chinese and properly formatted")
                else:
                    print("❌ No results found in output file")
            else:
                print("❌ Output file not found")
                
        else:
            print("❌ LLM endpoint test failed!")
            print(f"Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ Test timed out after 120 seconds")
        print("   Your LLM endpoint might be too slow or unresponsive")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed. Check the results above.")

if __name__ == "__main__":
    main()
