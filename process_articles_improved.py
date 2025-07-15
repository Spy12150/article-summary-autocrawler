import json
import os
import time
import argparse
import logging
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from functools import wraps
from dataclasses import dataclass
import requests
from tqdm import tqdm

"""Phase 2: Process scraped articles with LLM for sentiment analysis and summarization."""

# try to import from config.py w/ error handling
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
DEFAULT_MODEL = "deepseek-r132b"
DEFAULT_ENDPOINT = "http://10.30.15.111:8080/api/chat/completions"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DEFAULT_API_KEY = INS_API_KEY
DEFAULT_MODEL = "deepseek-r132b"
DEFAULT_ENDPOINT = "http://10.30.15.111:8080/api/chat/completions"


def generate_unique_filename(base_filename: str) -> str:
    """Generate a unique filename with timestamp to avoid overwriting."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Split the base filename into name and extension
    name, ext = os.path.splitext(base_filename)
    
    # Create the unique filename
    unique_filename = f"{name}_{timestamp}{ext}"
    
    # If the file still exists (unlikely but possible), add a counter
    counter = 1
    while os.path.exists(unique_filename):
        unique_filename = f"{name}_{timestamp}_{counter}{ext}"
        counter += 1
    
    return unique_filename


@dataclass
class QualityMetrics:
    """Metrics for article quality assessment"""
    content_length: int
    sentence_count: int
    tech_keyword_count: int
    has_date: bool
    has_url: bool
    quality_score: int
    quality_factors: List[str]


class RateLimiter:
    """Rate limiter to prevent API overload"""
    def __init__(self, calls_per_second: float = 2.0):
        self.calls_per_second = calls_per_second
        self.last_called = 0.0
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - self.last_called
            left_to_wait = 1.0 / self.calls_per_second - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            self.last_called = time.time()
            return ret
        return wrapper


# Rate limiter instance
rate_limiter = RateLimiter(calls_per_second=2.0)


def calculate_content_hash(content: str) -> str:
    """Calculate hash for article content to detect duplicates"""
    # Normalize content for better duplicate detection
    normalized = content.lower().strip()
    # Remove extra whitespace and newlines
    normalized = ' '.join(normalized.split())
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()


def assess_content_quality(article: Dict) -> QualityMetrics:
    """
    Assess article content quality and return detailed metrics.
    
    Quality Assessment Criteria:
    1. Content Length (0-3 points):
       - <200 chars: 0 points
       - 200-500 chars: 1 point  
       - 500-1000 chars: 2 points
       - >1000 chars: 3 points
    
    2. Sentence Structure (0-2 points):
       - <3 sentences: 0 points
       - 3-5 sentences: 1 point
       - >5 sentences: 2 points
    
    3. Technical Keywords (0-3 points):
       - No tech keywords: 0 points
       - 1-2 tech keywords: 1 point
       - 3-4 tech keywords: 2 points
       - >4 tech keywords: 3 points
    
    4. Metadata Completeness (0-2 points):
       - Has date: +1 point
       - Has valid URL: +1 point
    
    Total Score: 0-10 points
    Quality Levels:
    - 0-3: Poor quality
    - 4-6: Medium quality  
    - 7-10: High quality
    """
    content = article.get('content', '')
    
    # Initialize metrics
    quality_score = 0
    quality_factors = []
    
    # 1. Content Length Assessment
    content_length = len(content)
    if content_length >= 1000:
        quality_score += 3
        quality_factors.append('excellent_length')
    elif content_length >= 500:
        quality_score += 2
        quality_factors.append('good_length')
    elif content_length >= 200:
        quality_score += 1
        quality_factors.append('adequate_length')
    else:
        quality_factors.append('insufficient_length')
    
    # 2. Sentence Structure Assessment
    sentences = [s.strip() for s in content.split('.') if s.strip()]
    sentence_count = len(sentences)
    if sentence_count > 5:
        quality_score += 2
        quality_factors.append('excellent_structure')
    elif sentence_count >= 3:
        quality_score += 1
        quality_factors.append('good_structure')
    else:
        quality_factors.append('poor_structure')
    
    # 3. Technical Keywords Assessment
    tech_keywords = [
        'semiconductor', 'chip', 'manufacturing', 'technology', 'innovation',
        'processor', 'silicon', 'wafer', 'fabrication', 'electronics',
        'circuit', 'transistor', 'integrated', 'microprocessor', 'AI',
        'artificial intelligence', 'machine learning', 'quantum', 'nanotechnology',
        'gallium', 'arsenide', 'nitride', 'TSMC', 'Intel', 'AMD', 'NVIDIA'
    ]
    
    content_lower = content.lower()
    tech_keyword_count = sum(1 for keyword in tech_keywords if keyword in content_lower)
    
    if tech_keyword_count > 4:
        quality_score += 3
        quality_factors.append('highly_technical')
    elif tech_keyword_count >= 3:
        quality_score += 2
        quality_factors.append('technical_content')
    elif tech_keyword_count >= 1:
        quality_score += 1
        quality_factors.append('some_technical')
    else:
        quality_factors.append('non_technical')
    
    # 4. Metadata Completeness
    has_date = bool(article.get('date'))
    has_url = bool(article.get('article_url'))
    
    if has_date:
        quality_score += 1
        quality_factors.append('has_date')
    
    if has_url:
        quality_score += 1
        quality_factors.append('has_url')
    
    return QualityMetrics(
        content_length=content_length,
        sentence_count=sentence_count,
        tech_keyword_count=tech_keyword_count,
        has_date=has_date,
        has_url=has_url,
        quality_score=quality_score,
        quality_factors=quality_factors
    )


def deduplicate_articles(articles: List[Dict]) -> Tuple[List[Dict], int]:
    """
    Remove duplicate articles based on content hash.
    
    Returns:
        Tuple of (unique_articles, duplicate_count)
    """
    seen_hashes = set()
    unique_articles = []
    duplicate_count = 0
    
    for article in articles:
        content = article.get('content', '')
        if not content:
            continue
            
        content_hash = calculate_content_hash(content)
        
        if content_hash not in seen_hashes:
            seen_hashes.add(content_hash)
            # Add hash to article for tracking
            article['content_hash'] = content_hash
            unique_articles.append(article)
        else:
            duplicate_count += 1
            logger.info(f"Duplicate article found: {article.get('headline', 'Unknown')[:50]}...")
    
    logger.info(f"Deduplication complete: {len(unique_articles)} unique articles, {duplicate_count} duplicates removed")
    return unique_articles, duplicate_count


def load_articles(path: str) -> List[Dict]:
    """Load articles from JSON file."""
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


@rate_limiter
def call_llm(
    text: str, 
    api_key: str, 
    model: str = DEFAULT_MODEL,
    endpoint: str = DEFAULT_ENDPOINT,
    max_retries: int = 1,
    timeout: int = 60,  # Reduced timeout
    session_id: Optional[str] = None
) -> Optional[Dict]:
    """Call LLM endpoint for sentiment analysis and summarization."""
    
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
                    "你是一位专业的半导体行业新闻分析师，为中国半导体公司的营销高管服务。"
                    "请分析文章内容，并仅返回一个JSON对象，包含以下键值对："
                    "'sentiment' (情绪分析，必须是以下之一：利好 / 中立 / 利弊)，"
                    "'summary' (中文简要摘要，不超过80字)，"
                    "'relevant' (相关性，必须是：是 或 否 - 该信息是否对中国半导体公司营销高管有用)。"
                    "请确保返回格式严格为JSON，不要包含任何其他文本、分析或markdown格式。"
                    "摘要必须是有意义的中文内容，不能为空或null。"
                )
            },
            {
                "role": "user",
                "content": text
            }
        ],
        "temperature": 0.2,
        "preset": True
    }

    if session_id:
        payload["session_id"] = session_id

    # Add session for better connection handling
    session = requests.Session()
    session.headers.update(headers)

    for attempt in range(max_retries):
        try:
            response = session.post(endpoint, json=payload, timeout=timeout)
            response.raise_for_status()
            
            raw = response.text.strip()
            if not raw:
                logger.error("Empty response body from LLM endpoint")
                return None
                
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON returned by LLM endpoint: {raw}")
                return None
            finally:
                session.close()

            # Parse nested or flat result
            if 'choices' in response_data and response_data['choices']:
                content = response_data['choices'][0]['message']['content']
                import re
                json_match = re.search(r"\{.*\}", content, re.DOTALL)
                if json_match:
                    json_payload = json_match.group(0)
                    try:
                        result = json.loads(json_payload)
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse extracted JSON payload: {json_payload}")
                        result = None
                else:
                    logger.error(f"No JSON object found in LLM content: {content}")
                    result = None
            elif 'sentiment' in response_data and 'summary' in response_data:
                result = response_data
            else:
                logger.warning(f"Unexpected response format: {response_data}")
                result = None

            # Return if valid
            if result and result.get('sentiment') in ['利好','中立','利弊'] and result.get('summary') and result.get('relevant') in ['是','否']:
                if result.get('summary') and result['summary'].strip() and result['summary'].strip().lower() != 'none':
                    return result
            logger.warning(f"Invalid or missing keys in LLM response: {result}")
            
        except (requests.exceptions.RequestException, ConnectionError, OSError) as e:
            logger.warning(f"Request failed (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep((2 ** attempt) + (attempt * 0.1))
            else:
                logger.error("Max retries exceeded")
        except Exception as e:
            logger.error(f"Unexpected error during API call: {e}")
            break

    return None


# Mock LLM function removed - only real LLM results are accepted


def process_single_article(
    article: Dict, 
    api_key: str, 
    model: str,
    endpoint: str
) -> Dict:
    """Process a single article with LLM analysis and quality assessment."""
    processed_article = article.copy()
    
    # Assess content quality first
    quality_metrics = assess_content_quality(article)
    processed_article['quality_score'] = quality_metrics.quality_score
    processed_article['quality_factors'] = quality_metrics.quality_factors
    processed_article['content_length'] = quality_metrics.content_length
    processed_article['sentence_count'] = quality_metrics.sentence_count
    processed_article['tech_keyword_count'] = quality_metrics.tech_keyword_count
    
    # Get article content for analysis
    content = article.get('content', '')
    if not content:
        logger.warning(f"No content found for article: {article.get('headline', 'Unknown')}")
        processed_article['sentiment'] = '中立'
        processed_article['summary'] = '无内容可供分析'
        processed_article['relevant'] = '否'
        processed_article['processing_status'] = 'no_content'
        return processed_article
    
    # Skip processing if quality is too low (score < 3)
    if quality_metrics.quality_score < 3:
        logger.info(f"Skipping low quality article: {article.get('headline', 'Unknown')[:50]}...")
        processed_article['sentiment'] = '中立'
        processed_article['summary'] = '文章质量过低，跳过分析'
        processed_article['relevant'] = '否'
        processed_article['processing_status'] = 'low_quality'
        processed_article.pop('content', None)
        return processed_article
    
    # Call LLM for high-quality articles
    result = call_llm(content, api_key, model, endpoint)
    
    if result:
        processed_article['sentiment'] = result['sentiment']
        processed_article['summary'] = result['summary']
        processed_article['relevant'] = result['relevant']
        processed_article['processing_status'] = 'success'
    else:
        # No fallback - failed LLM calls are marked as failed
        logger.warning(f"LLM call failed for article: {article.get('headline', 'Unknown')[:50]}...")
        processed_article['sentiment'] = '中立'
        processed_article['summary'] = 'LLM分析失败'
        processed_article['relevant'] = '否'
        processed_article['processing_status'] = 'failed'
    
    processed_article.pop('content', None)
    return processed_article


def process_articles_sequentially(
    articles: List[Dict],
    api_key: str,
    model: str,
    endpoint: str
) -> List[Dict]:
    """Process articles sequentially to avoid endpoint timeouts."""
    processed_articles = []
    
    logger.info(f"Starting sequential processing of {len(articles)} articles")
    
    with tqdm(total=len(articles), desc="Processing articles sequentially") as pbar:
        for i, article in enumerate(articles):
            logger.info(f"Processing article {i+1}/{len(articles)}: {article.get('headline', 'Unknown')[:50]}...")
            
            try:
                processed_article = process_single_article(article, api_key, model, endpoint)
                processed_articles.append(processed_article)
                
                # Log processing status
                status = processed_article.get('processing_status', 'unknown')
                if status == 'success':
                    logger.info(f"✓ Successfully processed article {i+1}")
                elif status == 'failed':
                    logger.warning(f"✗ Failed to process article {i+1}")
                elif status == 'low_quality':
                    logger.info(f"- Skipped low quality article {i+1}")
                else:
                    logger.info(f"? Article {i+1} processed with status: {status}")
                    
            except Exception as e:
                logger.error(f"Error processing article {i+1}: {str(e)}")
                # Still add the article with error status
                error_article = article.copy()
                error_article['sentiment'] = '中立'
                error_article['summary'] = f'处理错误: {str(e)}'
                error_article['relevant'] = '否'
                error_article['processing_status'] = 'error'
                error_article.pop('content', None)
                processed_articles.append(error_article)
            
            pbar.update(1)
    
    return processed_articles


def process_articles(
    input_path: str,
    output_path: str,
    api_key: str,
    model: str = DEFAULT_MODEL,
    endpoint: str = DEFAULT_ENDPOINT
) -> None:
    """Process all articles with LLM analysis, deduplication, and quality assessment."""
    # Load articles
    articles = load_articles(input_path)
    
    if not articles:
        logger.warning("No articles to process")
        return
    
    logger.info(f"Starting processing pipeline for {len(articles)} articles")
    
    # Step 1: Deduplicate articles
    unique_articles, duplicate_count = deduplicate_articles(articles)
    
    # Step 2: Process articles sequentially
    processed_articles = process_articles_sequentially(
        unique_articles, api_key, model, endpoint
    )
    
    # Step 3: Generate statistics
    success_count = sum(1 for article in processed_articles if article.get('processing_status') == 'success')
    failed_count = sum(1 for article in processed_articles if article.get('processing_status') == 'failed')
    low_quality_count = sum(1 for article in processed_articles if article.get('processing_status') == 'low_quality')
    relevant_count = sum(1 for article in processed_articles if article.get('relevant') == '是')
    
    quality_scores = [article.get('quality_score', 0) for article in processed_articles]
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
    
    # Step 4: Save results
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_articles, f, ensure_ascii=False, indent=2)
    
    # Step 5: Log statistics
    logger.info(f"Processing complete!")
    logger.info(f"Original articles: {len(articles)}")
    logger.info(f"Duplicates removed: {duplicate_count}")
    logger.info(f"Unique articles processed: {len(unique_articles)}")
    logger.info(f"Successfully processed: {success_count}")
    logger.info(f"Failed to process: {failed_count}")
    logger.info(f"Low quality (skipped): {low_quality_count}")
    logger.info(f"Relevant articles: {relevant_count}")
    logger.info(f"Average quality score: {avg_quality:.2f}/10")
    logger.info(f"Results saved to: {output_path}")


def main():
    """Main CLI interface for article processing."""
    parser = argparse.ArgumentParser(
        description="Process scraped articles with LLM for sentiment analysis and summarization"
    )
    
    parser.add_argument("--input", default="data/article_data.json", help="Input JSON file path")
    parser.add_argument("--output", default="data/articles_processed.json", help="Output JSON file path")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model name (default: {DEFAULT_MODEL})")
    parser.add_argument("--key", default=os.getenv("INS_API_KEY", DEFAULT_API_KEY), help="API key")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT, help="LLM endpoint URL")
    parser.add_argument("--max-workers", type=int, default=5, help="Max concurrent workers (default: 5)")
    parser.add_argument("--auto-filename", action="store_true", help="Generate unique filenames with timestamps")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        return
    
    # Generate unique filename if requested
    output_path = args.output
    if args.auto_filename:
        output_path = generate_unique_filename(args.output)
        logger.info(f"Auto-generated output filename: {output_path}")
    
    try:
        process_articles(
            input_path=args.input,
            output_path=output_path,
            api_key=args.key,
            model=args.model,
            endpoint=args.endpoint
        )
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise


if __name__ == "__main__":
    main()
