#!/usr/bin/env python3
"""
Demo script showing what processed articles look like
"""
import json
import os
from process_articles import load_articles, process_single_article

def create_demo_output():
    """Create a demo showing what processed articles look like"""
    print("🎯 Demo: What processed articles look like")
    print("="*50)
    
    # Load sample articles
    data_files = [f for f in os.listdir('data') if f.startswith('article_data') and f.endswith('.json')]
    if not data_files:
        print("❌ No article data files found")
        return
    
    sample_file = os.path.join('data', data_files[0])
    articles = load_articles(sample_file)
    
    if not articles:
        print("❌ No articles found")
        return
    
    # Take first article and show before/after
    original_article = articles[0]
    
    print("📰 ORIGINAL ARTICLE:")
    print("-" * 30)
    print(f"Headline: {original_article.get('headline', 'N/A')}")
    print(f"Date: {original_article.get('date', 'N/A')}")
    print(f"Content length: {len(original_article.get('content', ''))}")
    print(f"URL: {original_article.get('article_url', 'N/A')}")
    
    # Simulate what it would look like after processing
    # (This is just a demo - in reality, this would come from the LLM)
    demo_processed = original_article.copy()
    demo_processed.update({
        'sentiment': 'positive',
        'summary': 'Major semiconductor company announces new research collaboration focused on advanced chip development and talent cultivation.',
        'processing_status': 'success'
    })
    
    print("\n🤖 PROCESSED ARTICLE (Demo):")
    print("-" * 30)
    print(f"Headline: {demo_processed.get('headline', 'N/A')}")
    print(f"Date: {demo_processed.get('date', 'N/A')}")
    print(f"Sentiment: {demo_processed.get('sentiment', 'N/A')}")
    print(f"Summary: {demo_processed.get('summary', 'N/A')}")
    print(f"Processing Status: {demo_processed.get('processing_status', 'N/A')}")
    print(f"Content length: {len(demo_processed.get('content', ''))}")
    print(f"URL: {demo_processed.get('article_url', 'N/A')}")
    
    # Show JSON structure
    print("\n📊 JSON OUTPUT STRUCTURE:")
    print("-" * 30)
    demo_output = {
        "headline": demo_processed.get('headline', 'N/A'),
        "date": demo_processed.get('date', 'N/A'),
        "sentiment": demo_processed.get('sentiment', 'N/A'),
        "summary": demo_processed.get('summary', 'N/A'),
        "processing_status": demo_processed.get('processing_status', 'N/A'),
        "content": demo_processed.get('content', '')[:200] + "..." if len(demo_processed.get('content', '')) > 200 else demo_processed.get('content', ''),
        "article_url": demo_processed.get('article_url', 'N/A'),
        "source_url": demo_processed.get('source_url', 'N/A')
    }
    
    print(json.dumps(demo_output, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    create_demo_output()
