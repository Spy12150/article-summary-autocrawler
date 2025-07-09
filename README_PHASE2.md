# Phase 2: Article Processing with LLM

This module processes scraped semiconductor news articles to add sentiment analysis and summarization using an internal LLM endpoint.

## Features

- 🤖 **LLM Integration**: Calls internal DeepSeek-R1 model for analysis
- 📊 **Sentiment Analysis**: Classifies articles as positive/neutral/negative
- 📝 **Summarization**: Generates concise 1-3 sentence summaries
- 🔄 **Retry Logic**: Automatic retry with exponential backoff
- 📈 **Progress Tracking**: Progress bar for batch processing
- 🛡️ **Error Handling**: Graceful handling of failures with fallback values
- 📋 **Status Tracking**: Tracks processing status for each article

## Installation

```bash
# Install required packages
pip install tqdm requests

# Or using the virtual environment
"/Users/ivorylove/Documents/Code/Innosci Internship Projects/.venv/bin/python" -m pip install tqdm requests
```

## Usage

### Basic Usage

```bash
# Process latest scraped articles
python process_articles.py

# Process specific file
python process_articles.py --input data/article_data9.json
```

### Advanced Usage

```bash
# Custom model and API key
python process_articles.py \
    --input data/article_data9.json \
    --output data/processed_articles.json \
    --model 'Deepseek-r1:32b' \
    --key 'your_api_key_here' \
    --endpoint 'http://10.30.15.111:8080/v1/chat/completions'
```

### Environment Variables

Set your API key as an environment variable:

```bash
export INS_API_KEY="your_api_key_here"
python process_articles.py
```

## Command Line Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--input` | `data/article_data1.json` | Input JSON file with scraped articles |
| `--output` | `data/articles_processed.json` | Output JSON file for processed articles |
| `--model` | `Deepseek-r1:32b` | LLM model name |
| `--key` | `INS_API_KEY` env var | API key for authentication |
| `--endpoint` | `http://10.30.15.111:8080/v1/chat/completions` | LLM endpoint URL |

## Input Format

The input should be a JSON file with articles in this format:

```json
[
  {
    "headline": "Article headline",
    "date": "2025/06/12",
    "content": "Full article content...",
    "article_url": "https://example.com/article",
    "source_url": "https://example.com"
  }
]
```

## Output Format

The output includes original fields plus LLM analysis:

```json
[
  {
    "headline": "Article headline",
    "date": "2025/06/12",
    "content": "Full article content...",
    "article_url": "https://example.com/article",
    "source_url": "https://example.com",
    "sentiment": "positive",
    "summary": "Concise summary of the article content...",
    "processing_status": "success"
  }
]
```

## Processing Status Values

- `success`: Article successfully processed by LLM
- `failed`: LLM processing failed, fallback values used
- `no_content`: Article has no content to analyze

## LLM Endpoint Details

### Request Format

```json
{
  "model": "Deepseek-r1:32b",
  "messages": [
    {
      "role": "system",
      "content": "You are an expert analyst of GaN semiconductor industry news. Return a JSON object with keys 'sentiment' (one of positive / neutral / negative) and 'summary' (<=80 words)."
    },
    {
      "role": "user",
      "content": "Article content here..."
    }
  ],
  "temperature": 0.2
}
```

### Expected Response

```json
{
  "sentiment": "positive",
  "summary": "Brief summary of the article..."
}
```

## Error Handling

- **Network errors**: Automatic retry with exponential backoff (max 3 attempts)
- **Invalid responses**: Logged and fallback values used
- **Missing content**: Skipped with appropriate status
- **API failures**: Graceful degradation with neutral sentiment

## Testing

Run the test script to verify functionality:

```bash
python test_processing.py
```

Run the demo to see sample output:

```bash
python demo_processing.py
```

## Integration with Phase 1

This module is designed to work with the output from `main.py` (Phase 1 scraping):

```bash
# Phase 1: Scrape articles
python main.py

# Phase 2: Process articles  
python process_articles.py --input data/article_data9.json
```

## Cost Estimation

Based on typical article lengths:
- **Per article**: ~1.25 cents (using GPT-4o equivalent)
- **1000 articles**: ~$12.50
- **Processing time**: ~2-3 seconds per article

## Logging

The module provides detailed logging:
- INFO: General processing progress
- WARNING: Retry attempts and recoverable errors
- ERROR: Failed processing attempts

## Future Enhancements

- [ ] Batch processing for better API efficiency
- [ ] Custom sentiment categories (regulatory, market, technical)
- [ ] Multi-language support
- [ ] Caching for repeated content
- [ ] Async processing for speed improvements
