#!/usr/bin/env python3
"""Simplified test version of the improved processing script"""

import json
import os
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('debug.log')
    ]
)
logger = logging.getLogger(__name__)

def test_mock_llm():
    """Test the mock LLM functionality"""
    logger.info("Testing mock LLM functionality...")
    
    test_text = "This is a test article about semiconductor technology and market growth."
    
    # Simple mock response
    mock_response = {
        "sentiment": "positive",
        "summary": "这是一篇关于半导体技术和市场增长的测试文章。",
        "relevant": "yes"
    }
    
    logger.info(f"Mock response: {mock_response}")
    return mock_response

def test_article_processing():
    """Test processing a single article"""
    logger.info("Testing article processing...")
    
    # Load articles
    input_file = "data/article_data.json"
    if not os.path.exists(input_file):
        logger.error(f"Input file not found: {input_file}")
        return
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        logger.info(f"Loaded {len(articles)} articles")
        
        # Process first article
        if articles:
            article = articles[0]
            logger.info(f"Processing article: {article.get('headline', 'No title')}")
            
            # Test mock LLM
            mock_result = test_mock_llm()
            
            # Create processed article
            processed_article = article.copy()
            processed_article.update({
                "sentiment": mock_result["sentiment"],
                "summary": mock_result["summary"],
                "relevant": mock_result["relevant"],
                "quality_score": 0.8,
                "processing_status": "success"
            })
            
            # Save result
            output_file = "data/test_debug_output.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump([processed_article], f, indent=2, ensure_ascii=False)
            
            logger.info(f"Processed article saved to {output_file}")
            logger.info(f"Summary: {processed_article['summary']}")
            logger.info(f"Sentiment: {processed_article['sentiment']}")
            logger.info(f"Relevant: {processed_article['relevant']}")
            
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        raise

if __name__ == "__main__":
    logger.info("Starting debug test...")
    try:
        test_article_processing()
        logger.info("Debug test completed successfully!")
    except Exception as e:
        logger.error(f"Debug test failed: {e}")
        sys.exit(1)
