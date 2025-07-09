"""
Phase 2: Process scraped articles with LLM for sentiment analysis and summarization.
"""
import json
import os
import time
import argparse
import logging
from typing import List, Dict, Optional, Tuple
import requests
from tqdm import tqdm

# Try to import config, fall back to environment variables
try:
    from config import INS_API_KEY
except ImportError:
    INS_API_KEY = os.getenv("INS_API_KEY", "YOUR_API_KEY_HERE")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DEFAULT_API_KEY = INS_API_KEY
DEFAULT_MODEL = "Deepseek-r1:32b"
DEFAULT_ENDPOINT = "http://10.30.15.111:8080/v1/chat/completions"


def load_articles(path: str) -> List[Dict]:
    """Load articles from JSON file.
    
    Args:
        path: Path to JSON file containing articles
        
    Returns:
        List of article dictionaries
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        logger.info(f"Loaded {len(articles)} articles from {path}")
        return articles
    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {path}: {e}")
        raise


def call_llm(
    text: str, 
    api_key: str, 
    model: str = DEFAULT_MODEL,
    endpoint: str = DEFAULT_ENDPOINT,
    max_retries: int = 3,
    timeout: int = 30
) -> Optional[Dict]:
    """Call LLM endpoint for sentiment analysis and summarization.
    
    Args:
        text: Article content to analyze
        api_key: API key for authentication
        model: Model name to use
        endpoint: LLM endpoint URL (use 'mock' for testing)
        max_retries: Maximum number of retry attempts
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with 'sentiment' and 'summary' keys, or None if failed
    """
    # Check for mock mode
    if endpoint == 'mock' or endpoint.lower() == 'mock':
        logger.info("Using mock mode for LLM calls")
        return call_llm_mock(text)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert analyst of GaN semiconductor industry news. "
                    "Return a JSON object with keys 'sentiment' "
                    "(one of positive / neutral / negative) and 'summary' (<=80 words)."
                )
            },
            {
                "role": "user",
                "content": text
            }
        ],
        "temperature": 0.2
    }
    
    for attempt in range(max_retries):
        try:
            # Add session for better connection handling
            session = requests.Session()
            session.headers.update(headers)
            
            response = session.post(
                endpoint,
                json=payload,
                timeout=timeout
            )
            response.raise_for_status()
            
            # Parse response
            response_data = response.json()
            session.close()
            
            # Extract content from response
            if 'choices' in response_data and response_data['choices']:
                content = response_data['choices'][0]['message']['content']
                
                # Try to parse JSON from content
                try:
                    result = json.loads(content)
                    
                    # Validate required keys
                    if 'sentiment' in result and 'summary' in result:
                        # Validate sentiment value
                        if result['sentiment'] in ['positive', 'neutral', 'negative']:
                            return result
                        else:
                            logger.warning(f"Invalid sentiment value: {result['sentiment']}")
                    else:
                        logger.warning(f"Missing required keys in response: {result}")
                        
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse JSON from LLM response: {content}")
                    
            else:
                logger.warning(f"Unexpected response format: {response_data}")
                
        except (requests.exceptions.RequestException, ConnectionError, 
                requests.exceptions.ConnectionError, OSError) as e:
            logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
            
            if attempt < max_retries - 1:
                # Exponential backoff with jitter
                sleep_time = (2 ** attempt) + (attempt * 0.1)
                logger.info(f"Retrying in {sleep_time:.1f} seconds...")
                time.sleep(sleep_time)
            else:
                logger.error(f"Max retries exceeded for article after {max_retries} attempts")
                
        except KeyboardInterrupt:
            logger.error("Processing interrupted by user")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during API call: {e}")
            break
    
    return None


def call_llm_mock(text: str) -> Dict:
    """Mock LLM call for testing when endpoint is not available.
    
    Args:
        text: Article content to analyze
        
    Returns:
        Dictionary with mock sentiment and summary
    """
    import random
    
    # Simple rule-based sentiment analysis for testing
    text_lower = text.lower()
    
    # Positive indicators
    positive_words = ['growth', 'increase', 'success', 'breakthrough', 'innovation', 
                     'partnership', 'investment', 'expansion', 'revenue', 'profit']
    
    # Negative indicators  
    negative_words = ['decline', 'loss', 'failure', 'crisis', 'problem', 'concern',
                     'decrease', 'fall', 'issue', 'challenge']
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        sentiment = "positive"
    elif negative_count > positive_count:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    
    # Generate a simple summary (first sentence + key info)
    sentences = text.split('.')[:3]
    summary = '. '.join(sentences).strip()
    if len(summary) > 80:
        summary = summary[:77] + "..."
    
    return {
        "sentiment": sentiment,
        "summary": summary or "Brief summary of semiconductor industry news."
    }


def process_single_article(
    article: Dict, 
    api_key: str, 
    model: str,
    endpoint: str
) -> Dict:
    """Process a single article with LLM analysis.
    
    Args:
        article: Article dictionary
        api_key: API key for LLM
        model: Model name
        endpoint: LLM endpoint URL
        
    Returns:
        Article dictionary with added sentiment and summary fields
    """
    processed_article = article.copy()
    
    # Get article content for analysis
    content = article.get('content', '')
    if not content:
        logger.warning(f"No content found for article: {article.get('headline', 'Unknown')}")
        processed_article['sentiment'] = 'neutral'
        processed_article['summary'] = 'No content available for analysis'
        processed_article['processing_status'] = 'no_content'
        return processed_article
    
    # Call LLM
    result = call_llm(content, api_key, model, endpoint)
    
    if result:
        processed_article['sentiment'] = result['sentiment']
        processed_article['summary'] = result['summary']
        processed_article['processing_status'] = 'success'
    else:
        # Fallback values if LLM fails
        processed_article['sentiment'] = 'neutral'
        processed_article['summary'] = 'Analysis failed - unable to process content'
        processed_article['processing_status'] = 'failed'
        logger.error(f"Failed to process article: {article.get('headline', 'Unknown')}")
    
    return processed_article


def process_articles(
    input_path: str,
    output_path: str,
    api_key: str,
    model: str = DEFAULT_MODEL,
    endpoint: str = DEFAULT_ENDPOINT
) -> None:
    """Process all articles with LLM analysis and save results.
    
    Args:
        input_path: Path to input JSON file
        output_path: Path to output JSON file
        api_key: API key for LLM
        model: Model name to use
        endpoint: LLM endpoint URL
    """
    # Load articles
    articles = load_articles(input_path)
    
    if not articles:
        logger.warning("No articles to process")
        return
    
    # Process articles with progress bar
    processed_articles = []
    success_count = 0
    failed_count = 0
    
    logger.info(f"Processing {len(articles)} articles with model: {model}")
    
    for article in tqdm(articles, desc="Processing articles"):
        processed_article = process_single_article(article, api_key, model, endpoint)
        processed_articles.append(processed_article)
        
        if processed_article.get('processing_status') == 'success':
            success_count += 1
        else:
            failed_count += 1
    
    # Save results
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_articles, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Processing complete!")
    logger.info(f"Successfully processed: {success_count} articles")
    logger.info(f"Failed to process: {failed_count} articles")
    logger.info(f"Results saved to: {output_path}")


def main():
    """Main CLI interface for article processing."""
    parser = argparse.ArgumentParser(
        description="Process scraped articles with LLM for sentiment analysis and summarization"
    )
    
    parser.add_argument(
        "--input",
        default="data/article_data1.json",
        help="Path to input JSON file with articles (default: data/article_data1.json)"
    )
    
    parser.add_argument(
        "--output",
        default="data/articles_processed.json",
        help="Path to output JSON file (default: data/articles_processed.json)"
    )
    
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Model name to use (default: {DEFAULT_MODEL})"
    )
    
    parser.add_argument(
        "--key",
        default=os.getenv("INS_API_KEY", DEFAULT_API_KEY),
        help="API key for LLM endpoint (default: from config.py, INS_API_KEY env var, or fallback)"
    )
    
    parser.add_argument(
        "--endpoint",
        default=DEFAULT_ENDPOINT,
        help=f"LLM endpoint URL (default: {DEFAULT_ENDPOINT})"
    )
    
    args = parser.parse_args()
    
    # Validate API key
    if args.key == "YOUR_API_KEY_HERE" or args.key == DEFAULT_API_KEY:
        logger.warning("Using default/placeholder API key - please set up config.py or INS_API_KEY environment variable")
    
    # Check if input file exists
    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        return
    
    try:
        process_articles(
            input_path=args.input,
            output_path=args.output,
            api_key=args.key,
            model=args.model,
            endpoint=args.endpoint
        )
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise


if __name__ == "__main__":
    main()
