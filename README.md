# Article Summary Autocrawler

A modular Python tool for scraping news articles and analyzing sentiment using LLM processing.

## General Project Structure Map

![Project Structure](images/struct1.png)

## Architecture

The system consists of two main phases (right now! still in progress):

1. **Web Scraping**: Extracts articles using multiple crawling methods
2. **LLM Processing**: Analyzes sentiment and generates summaries

Data flow: Web scraping → article_dataN.json → LLM processing → articles_processed.json

## Quick Start

### Installation

```bash
git clone <repo-url>
cd article-summary-autocrawler
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

```bash
cp config.example.py config.py
# Edit config.py with your actual API keys
```

### Basic Usage

```bash
# Scrape articles
python main.py

# Process with LLM
python process_articles.py
```

## Project Structure

```
├── main.py                     # Article scraping
├── process_articles.py         # LLM processing
├── google_search.py           # Google Custom Search integration
├── config.py                  # API keys (gitignored)
├── config.example.py          # Template for API keys
├── requirements.txt           # Dependencies
├── crawlers/                  # Scraping modules
│   ├── base.py
│   ├── trafilatura_crawler.py
│   ├── playwright_crawler.py
│   └── html_fallback_crawler.py
├── data/                      # Output files (gitignored)
│   ├── article_data1.json     # Raw scraped articles
│   └── articles_processed.json # LLM-analyzed articles
└── downloaded_htmls/          # Raw HTML cache (gitignored)
```

## Features

### Web Scraping (Phase 1)
- Multi-method approach: Trafilatura → HTML fallback → Playwright
- Google search integration for finding news sites
- Content filtering based on length and headline validation
- Error handling with graceful failures
- Per-site statistics tracking

### LLM Processing (Phase 2)
- Sentiment analysis (positive/neutral/negative)
- Article summarization in Chinese (80 words max)
- Relevance assessment for Chinese semiconductor marketing executives
- Retry logic with exponential backoff
- Mock mode for testing without real LLM endpoint
- Batch processing with progress tracking

## Usage Examples

### Article Scraping

```bash
# Manual URL entry
python main.py
# Choose option 1, enter URLs manually

# Google search mode
python main.py
# Choose option 2, search by keywords
```

### LLM Processing

```bash
# Process with real LLM endpoint
python process_articles.py --input data/article_data1.json

# Mock mode for testing
python process_articles.py --endpoint 'mock' --input data/article_data1.json

# Custom configuration
python process_articles.py \
    --input data/article_data9.json \
    --output data/custom_processed.json \
    --model "deepseek-r132b"
```

### Command Line Options

#### process_articles.py

| Option | Default | Description |
|--------|---------|-------------|
| `--input` | `data/article_data.json` | Input JSON file with articles |
| `--output` | `data/articles_processed.json` | Output JSON file for processed articles |
| `--model` | `deepseek-r132b` | LLM model name |
| `--key` | From config.py | API key for authentication |
| `--endpoint` | `http://10.30.15.111:8080/api/chat/completions` | LLM endpoint URL |

## Input/Output Formats

### Input Format (Raw Articles)
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

### Output Format (Processed Articles)
```json
[
  {
    "headline": "Article headline",
    "date": "2025/06/12",
    "article_url": "https://example.com/article",
    "source_url": "https://example.com",
    "sentiment": "positive",
    "summary": "文章内容的简明摘要（中文，最多80字）...",
    "relevant": "yes",
    "processing_status": "success"
  }
]
```

## API Key Management

### Security Best Practices
- API keys stored in `config.py` (gitignored)
- Template provided in `config.example.py` (committed)
- Environment variable fallbacks available
- Clear separation of code and credentials

### Setup for New Environments
```bash
# Copy template
cp config.example.py config.py

# Edit with real keys
nano config.py

# Verify gitignore
git status  # config.py should not appear
```

## Network Requirements

### Full Functionality
- Right now the program is only designed for internal LLM, I will add OpenAI API functionality soon
- Internet access for web scraping
- Access to `10.30.15.111:8080` for internal LLM
- Google Custom Search API access

### Development/Testing
- Use `--endpoint 'mock'` for offline testing
- Mock mode provides realistic sentiment analysis

## Testing

```bash
# Test LLM endpoint connectivity
python test_connection.py

# Test processing pipeline
python test_processing.py

# See sample output format
python demo_processing.py
```

## GitHub Deployment

### Before Pushing
1. Ensure `config.py` is in `.gitignore`
2. Verify no API keys in source code
3. Include `config.example.py` for others
4. Test that `git status` doesn't show `config.py`

### Deployment Process
1. Clone repo on target machine
2. Copy `config.example.py` to `config.py`
3. Add real API keys to `config.py`
4. Test network connectivity to LLM endpoint
5. Run the pipeline

## Documentation

- [SETUP.md](SETUP.md): Deployment guide for new environments
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md): Common issues and solutions


