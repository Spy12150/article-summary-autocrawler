#!/usr/bin/env python3
"""
Test script to demonstrate single article processing and unique filename generation.
"""

import subprocess
import time
import os

def run_single_article_test():
    """Test the LLM endpoint with a single article."""
    print("=" * 60)
    print("SINGLE ARTICLE LLM ENDPOINT TEST")
    print("=" * 60)
    
    # Test with the real LLM endpoint
    print("\n1. Testing with real LLM endpoint...")
    cmd = [
        "C:/Users/MaximeWang/AppData/Local/Programs/Python/Python313/python.exe",
        "process_articles_improved.py",
        "--input", "data/single_article_test.json",
        "--output", "data/single_test_llm.json",
        "--auto-filename",
        "--max-workers", "1"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Single article test with LLM endpoint completed successfully!")
        print(f"STDOUT: {result.stdout}")
    else:
        print("❌ Single article test with LLM endpoint failed!")
        print(f"STDERR: {result.stderr}")
    
    # Test with mock endpoint for comparison
    print("\n2. Testing with mock endpoint for comparison...")
    cmd_mock = [
        "C:/Users/MaximeWang/AppData/Local/Programs/Python/Python313/python.exe",
        "process_articles_improved.py",
        "--input", "data/single_article_test.json",
        "--output", "data/single_test_mock.json",
        "--endpoint", "mock",
        "--auto-filename",
        "--max-workers", "1"
    ]
    
    print(f"Running: {' '.join(cmd_mock)}")
    result_mock = subprocess.run(cmd_mock, capture_output=True, text=True)
    
    if result_mock.returncode == 0:
        print("✅ Single article test with mock endpoint completed successfully!")
        print(f"STDOUT: {result_mock.stdout}")
    else:
        print("❌ Single article test with mock endpoint failed!")
        print(f"STDERR: {result_mock.stderr}")

def demonstrate_unique_filenames():
    """Demonstrate the unique filename generation."""
    print("\n" + "=" * 60)
    print("UNIQUE FILENAME GENERATION DEMO")
    print("=" * 60)
    
    for i in range(3):
        print(f"\nRun {i+1}:")
        cmd = [
            "C:/Users/MaximeWang/AppData/Local/Programs/Python/Python313/python.exe",
            "process_articles_improved.py",
            "--input", "data/single_article_test.json",
            "--output", "data/analysis.json",
            "--endpoint", "mock",
            "--auto-filename",
            "--max-workers", "1"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Run {i+1} completed successfully!")
            # Extract the generated filename from the stdout
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Auto-generated output filename:' in line:
                    print(f"   Generated file: {line.split(':')[1].strip()}")
                elif 'Results saved to:' in line:
                    print(f"   Saved to: {line.split(':')[1].strip()}")
        else:
            print(f"❌ Run {i+1} failed!")
            print(f"STDERR: {result.stderr}")
        
        # Small delay to ensure different timestamps
        time.sleep(2)

def list_generated_files():
    """List all generated files to show the unique naming."""
    print("\n" + "=" * 60)
    print("GENERATED FILES")
    print("=" * 60)
    
    data_dir = "data"
    if os.path.exists(data_dir):
        files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
        files.sort()
        
        print(f"\nFiles in {data_dir}:")
        for file in files:
            file_path = os.path.join(data_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"  {file} ({file_size} bytes)")
    else:
        print(f"Directory {data_dir} does not exist!")

if __name__ == "__main__":
    print("Starting comprehensive test of improved article processing...")
    
    # Run single article test
    run_single_article_test()
    
    # Demonstrate unique filename generation
    demonstrate_unique_filenames()
    
    # List all generated files
    list_generated_files()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)
