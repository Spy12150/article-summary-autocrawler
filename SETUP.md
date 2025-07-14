# Setup Guide

This guide explains how to set up and run the article scraper on a new machine.

## Prerequisites

- Python 3.8 or higher
- Network access to `10.30.15.111:8080` (for LLM processing)
- Git for cloning the repository

## Installation Steps

### 1. Clone Repository
```bash
git clone <your-github-repo-url>
cd article-summary-autocrawler
```

### 2. Create Virtual Environment
```bash
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

If `requirements.txt` is missing, install manually:
```bash
pip install requests trafilatura playwright beautifulsoup4 tqdm lxml
```

### 4. Configure API Keys
```bash
# Copy the example config file
cp config.example.py config.py

# Edit config.py with your actual API keys
nano config.py  # or use your preferred editor
```

Update `config.py` with your API keys:
```python
# LLM API Configuration
INS_API_KEY = "your_actual_ins_api_key_here"

# Google Custom Search API Configuration  
GOOGLE_API_KEY = "your_google_api_key_here"
GOOGLE_CSE_ID = "your_google_cse_id_here"

# Alternative LLM endpoints (optional)
OPENAI_API_KEY = "your_openai_api_key_here"
```

### 5. Test Network Connectivity
```bash
# Test the LLM endpoint
python test_connection.py
```

Expected output:
```
Main endpoint is accessible
```

### 6. Install Playwright Browser (if needed)
```bash
# Install Playwright browsers
playwright install chromium
```

## Running the Pipeline

### Phase 1: Scrape Articles
```bash
# Interactive mode with manual URLs
python main.py

# Choose option 1 for manual URLs or option 2 for Google search
```

### Phase 2: Process with LLM
```bash
# Process the latest scraped articles
python process_articles.py --input data/article_data1.json

# Or specify exact files
python process_articles.py \
    --input data/article_data1.json \
    --output data/processed_articles.json
```

## Verification

### Test Scraping
```bash
# Run a quick test
python main.py
# Enter a single URL like: https://www.example-news.com
# Request 1-2 articles to test functionality
```

### Test Processing
```bash
# Test with mock mode (doesn't require LLM endpoint)
python process_articles.py --endpoint 'mock' --input data/article_data1.json
```

## Directory Structure After Setup

```
article-summary-autocrawler/
├── .venv/                     # Virtual environment
├── config.py                  # Your API keys (gitignored)
├── data/                      # Created automatically
│   ├── article_data1.json     # Scraped articles
│   └── articles_processed.json # LLM-processed articles
├── downloaded_htmls/          # HTML cache (created automatically)
└── [other project files]
```

## Common Setup Issues

### Python Environment
- Ensure Python 3.8+ is installed: `python --version`
- Use virtual environment to avoid conflicts
- On Windows, use `python` instead of `python3`

### Network Issues
- Test basic connectivity: `ping 10.30.15.111`
- Verify VPN connection if using internal network
- Check firewall settings for port 8080

### Missing Dependencies
- Install missing packages: `pip install [package-name]`
- Update pip if needed: `pip install --upgrade pip`
- For Playwright issues, run: `playwright install`

### API Key Issues
- Verify keys are correctly formatted in `config.py`
- Check that `config.py` is not tracked by git: `git status`
- Test Google Search API with a simple query

## Alternative Configurations

### Using Different LLM Endpoints
```bash
# OpenAI API
python process_articles.py \
    --endpoint 'https://api.openai.com/v1/chat/completions' \
    --model 'gpt-4o' \
    --key 'your-openai-api-key'

# Local LLM server
python process_articles.py \
    --endpoint 'http://localhost:8080/v1/chat/completions' \
    --model 'local-model'
```

### Mock Mode for Development
```bash
# Use mock mode for testing without real LLM
python process_articles.py --endpoint 'mock' --input data/article_data1.json
```

## Security Checklist

Before deployment:
- [ ] `config.py` is in `.gitignore`
- [ ] No API keys in source code
- [ ] `config.example.py` is included for others
- [ ] Test that `git status` doesn't show `config.py`

## Next Steps

After successful setup:
1. Run the full pipeline on sample data
2. Monitor logs for any errors
3. Test with different news sources
4. Schedule regular runs if needed

For troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

# Check network connectivity
ping 10.30.15.111
telnet 10.30.15.111 8080
```

### **If Import Errors Occur:**
```bash
# Install missing packages
pip install <missing-package>

# Or reinstall all
pip install -r requirements.txt --force-reinstall
```

### **Environment Variables Alternative:**
If you prefer not to use `config.py`, set environment variables:
```bash
export INS_API_KEY="your_api_key_here"
export GOOGLE_API_KEY="your_google_key_here" 
export GOOGLE_CSE_ID="your_cse_id_here"

python process_articles.py
```

## Expected output

### **Phase 1 Output:**
- `data/article_dataN.json` (where N increments)
- `downloaded_htmls/` folder with raw HTML files

### **Phase 2 Output:**
- `data/articles_processed.json` with sentiment and summaries
- Console output showing processing progress


