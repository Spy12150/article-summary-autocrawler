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

"""Phase 2: Process scraped articles with LLM for sentiment analysis and summarization.
This one using sequential processing to avoid endpoint timeouts and no mock LLM fallback.

I'm still working on fixing the concurrent version but there's bugs, so this is the most efficient for now

but it's still roughly 1 minute per article which is pretty slow"""

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

# Quality assessment dataclass
@dataclass
class QualityMetrics:
    quality_score: float
    quality_factors: List[str]
    content_length: int
    sentence_count: int
    tech_keyword_count: int

# Rate limiting decorator
def rate_limiter(func):
    """Rate limiter decorator to prevent overwhelming the API."""
    last_call_time = 0
    min_interval = 1.0  # Minimum 1 second between calls
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal last_call_time
        current_time = time.time()
        time_since_last_call = current_time - last_call_time
        
        if time_since_last_call < min_interval:
            sleep_time = min_interval - time_since_last_call
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        last_call_time = time.time()
        return func(*args, **kwargs)
    
    return wrapper

def load_articles(file_path: str) -> List[Dict]:
    """Load articles from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return []
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file: {file_path}")
        return []

def generate_unique_filename(base_path: str) -> str:
    """Generate unique filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = os.path.dirname(base_path)
    base_name = os.path.splitext(os.path.basename(base_path))[0]
    extension = os.path.splitext(base_path)[1]
    
    return os.path.join(base_dir, f"{base_name}_{timestamp}{extension}")

def generate_content_hash(article: Dict) -> str:
    """Generate hash for article content to detect duplicates."""
    content = article.get('content', '')
    headline = article.get('headline', '')
    combined = f"{headline}|{content}"
    return hashlib.md5(combined.encode('utf-8')).hexdigest()

def deduplicate_articles(articles: List[Dict]) -> Tuple[List[Dict], int]:
    """Remove duplicate articles based on content hash."""
    seen_hashes = set()
    unique_articles = []
    duplicate_count = 0
    
    for article in articles:
        content_hash = generate_content_hash(article)
        
        if content_hash not in seen_hashes:
            seen_hashes.add(content_hash)
            unique_articles.append(article)
        else:
            duplicate_count += 1
            logger.debug(f"Duplicate article found: {article.get('headline', 'Unknown')[:50]}...")
    
    logger.info(f"Deduplication: {len(articles)} -> {len(unique_articles)} articles ({duplicate_count} duplicates removed)")
    return unique_articles, duplicate_count

def assess_content_quality(article: Dict) -> QualityMetrics:
    """Assess the quality of article content."""
    content = article.get('content', '')
    headline = article.get('headline', '')
    
    # Basic metrics
    content_length = len(content)
    sentence_count = len([s for s in content.split('.') if s.strip()])
    
    # Quality factors
    quality_factors = []
    quality_score = 0
    
    # Length factor (0-3 points)
    if content_length > 1000:
        quality_score += 3
        quality_factors.append("sufficient_length")
    elif content_length > 500:
        quality_score += 2
        quality_factors.append("moderate_length")
    elif content_length > 200:
        quality_score += 1
        quality_factors.append("short_length")
    else:
        quality_factors.append("very_short")
    
    # Sentence structure factor (0-2 points)
    if sentence_count > 5:
        quality_score += 2
        quality_factors.append("well_structured")
    elif sentence_count > 2:
        quality_score += 1
        quality_factors.append("basic_structure")
    else:
        quality_factors.append("poor_structure")
    
    # Technology keyword relevance (0-3 points)
    tech_keywords = [
        'semiconductor', 'chip', 'technology', 'AI', 'manufacturing', 'processor',
        'memory', 'GPU', 'CPU', 'silicon', 'fabrication', 'innovation', 'research',
        'development', 'market', 'industry', 'company', 'investment', 'revenue'
    ]
    
    content_lower = content.lower()
    tech_keyword_count = sum(1 for keyword in tech_keywords if keyword in content_lower)
    
    if tech_keyword_count >= 5:
        quality_score += 3
        quality_factors.append("highly_relevant")
    elif tech_keyword_count >= 2:
        quality_score += 2
        quality_factors.append("relevant")
    elif tech_keyword_count >= 1:
        quality_score += 1
        quality_factors.append("somewhat_relevant")
    else:
        quality_factors.append("low_relevance")
    
    # Headline quality (0-2 points)
    if headline and len(headline) > 20:
        quality_score += 2
        quality_factors.append("good_headline")
    elif headline:
        quality_score += 1
        quality_factors.append("basic_headline")
    else:
        quality_factors.append("no_headline")
    
    return QualityMetrics(
        quality_score=quality_score,
        quality_factors=quality_factors,
        content_length=content_length,
        sentence_count=sentence_count,
        tech_keyword_count=tech_keyword_count
    )

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
    
    prompt = f"""
请分析以下半导体行业新闻文章，并提供：

1. 情绪分析（请回答"利好"、"中立"或"利弊"）
2. 中文总结（100-200字）
3. 对中国半导体营销高管的相关性（请回答"是"或"否"）

文章内容：
{text}

请用以下JSON格式回答：
{{
  "sentiment": "利好/中立/利弊",
  "summary": "中文总结内容",
  "relevant": "是/否"
}}
"""
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500,
        "temperature": 0.3
    }
    
    for attempt in range(max_retries + 1):
        try:
            logger.debug(f"Making LLM API call (attempt {attempt + 1}/{max_retries + 1})")
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                
                # Try to parse JSON response
                try:
                    parsed_result = json.loads(content)
                    
                    # Validate required fields
                    if all(key in parsed_result for key in ['sentiment', 'summary', 'relevant']):
                        logger.debug("LLM API call successful")
                        return parsed_result
                    else:
                        logger.warning(f"LLM response missing required fields: {content}")
                        return None
                        
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse LLM response as JSON: {content}")
                    return None
                    
            else:
                logger.warning(f"LLM API call failed with status {response.status_code}: {response.text}")
                if attempt < max_retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
        except requests.exceptions.Timeout:
            logger.warning(f"LLM API call timed out (attempt {attempt + 1})")
            if attempt < max_retries:
                time.sleep(2 ** attempt)
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"LLM API call failed: {e}")
            if attempt < max_retries:
                time.sleep(2 ** attempt)
    
    logger.error("All LLM API call attempts failed")
    return None

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
        json.dump(processed_articles, f, indent=2, ensure_ascii=False)
    
    # Step 5: Print summary
    logger.info("\n=== PROCESSING SUMMARY ===")
    logger.info(f"Total articles loaded: {len(articles)}")
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
    parser.add_argument("--auto-filename", action="store_true", help="Auto-generate unique output filename with timestamp")
    
    args = parser.parse_args()
    
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
