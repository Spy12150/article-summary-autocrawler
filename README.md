# Semiconductor News Scraper & Analyzer

A robust, modular Python tool for scraping semiconductor industry news and analyzing sentiment using LLM processing.

## 🏗️ **Architecture**

```
Phase 1: News Scraping          Phase 2: LLM Processing
┌─────────────────────────┐     ┌─────────────────────────┐
│   Web Scraping         │     │   Sentiment Analysis    │
│                         │     │                         │
│ • Trafilatura           │────▶│ • DeepSeek-R1 LLM      │
│ • HTML Fallback        │     │ • JSON Summaries       │
│ • Playwright            │     │ • Progress Tracking     │
│ • Google Search         │     │ • Error Handling        │
└─────────────────────────┘     └─────────────────────────┘
           │                               │
           ▼                               ▼
    data/article_dataN.json         data/articles_processed.json
```

## 🚀 **Quick Start**

### **1. Setup**
```bash
git clone <repo-url>
cd "Innosci Internship Projects"
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### **2. Configure API Keys**
```bash
cp config.example.py config.py
# Edit config.py with your actual API keys
```

### **3. Run Pipeline**
```bash
# Scrape articles
python main.py

# Process with LLM
python process_articles.py
```

## 🔒 **Security & API Key Management**

### **✅ What We Do (Secure)**
- API keys stored in `config.py` (gitignored)
- Example template in `config.example.py` (committed)
- Environment variable fallbacks
- Clear separation of code and credentials

### **❌ What We Avoid**
- Hardcoded API keys in source code
- Committing sensitive credentials
- Sharing keys in plain text

### **File Structure**
```
config.py          ← Your actual API keys (NEVER commit)
config.example.py  ← Template for others (safe to commit)
.gitignore         ← Excludes config.py from git
```

### **Setup for New Environments**
```bash
# 1. Copy template
cp config.example.py config.py

# 2. Edit with real keys
nano config.py

# 3. Verify it's gitignored
git status  # config.py should not appear
```

## 📁 **Project Structure**

```
├── main.py                     # Phase 1: News scraping
├── process_articles.py         # Phase 2: LLM processing
├── google_search.py           # Google Custom Search integration
├── config.py                  # API keys (gitignored)
├── config.example.py          # Template for API keys
├── requirements.txt           # Dependencies
├── .gitignore                # Git exclusions
├── SETUP.md                  # Deployment guide
├── TROUBLESHOOTING.md        # Common issues
├── README_PHASE2.md          # Detailed Phase 2 docs
│
├── crawlers/                 # Scraping modules
│   ├── trafilatura_crawler.py
│   ├── playwright_crawler.py
│   └── html_fallback_crawler.py
│
├── data/                     # Output files (gitignored)
│   ├── article_data1.json    # Raw scraped articles
│   └── articles_processed.json # LLM-analyzed articles
│
└── downloaded_htmls/         # Raw HTML cache (gitignored)
```

## 🛠️ **Features**

### **Phase 1: Web Scraping**
- **Multi-method approach**: Trafilatura → HTML fallback → Playwright
- **Google search integration**: Find news sites by keywords
- **Smart filtering**: Content length, headline validation
- **Robust error handling**: Graceful failures, retry logic
- **Progress tracking**: Per-site statistics

### **Phase 2: LLM Processing**
- **Sentiment analysis**: Positive/neutral/negative classification
- **Summarization**: Concise 1-3 sentence summaries
- **Retry logic**: Exponential backoff for network issues
- **Mock mode**: Testing without real LLM endpoint
- **Batch processing**: Progress bars for large datasets

## 🌐 **Network Requirements**

### **For Full Functionality:**
- Internet access (scraping)
- Access to `10.30.15.111:8080` (internal LLM)
- Google Custom Search API access

### **For Development/Testing:**
- Use `--endpoint 'mock'` for offline testing
- Mock mode provides realistic sentiment analysis

## 📊 **Usage Examples**

### **Basic Scraping**
```bash
# Manual URL entry
python main.py
# Enter URLs: https://www.semiconductors.org/news-events/latest-news/

# Google search mode  
python main.py
# Choose option 2, search: "semiconductor industry news"
```

### **LLM Processing**
```bash
# Real LLM endpoint
python process_articles.py --input data/article_data1.json

# Mock mode (for testing)
python process_articles.py --endpoint 'mock' --input data/article_data1.json

# Custom settings
python process_articles.py \
    --input data/article_data9.json \
    --output data/custom_processed.json \
    --model "Deepseek-r1:32b"
```

### **Diagnostics**
```bash
# Test LLM endpoint connectivity
python test_connection.py

# Test processing pipeline
python test_processing.py

# See sample output format
python demo_processing.py
```

## 💰 **Cost Estimation**

- **Internal LLM**: Free (if accessible)
- **OpenAI GPT-4o**: ~$0.0125 per article
- **Google Search**: ~$5 per 1000 queries

## 🚨 **Important for GitHub**

### **Before Pushing to GitHub:**
1. ✅ Ensure `config.py` is in `.gitignore`
2. ✅ Verify no API keys in source code
3. ✅ Include `config.example.py` for others
4. ✅ Test that `git status` doesn't show `config.py`

### **For Deployment:**
1. 📁 Clone repo on target machine
2. 📝 Copy `config.example.py` to `config.py`
3. 🔑 Add real API keys to `config.py`
4. 🌐 Test network connectivity to LLM endpoint
5. 🏃 Run the pipeline

## 📚 **Documentation**

- **[SETUP.md](SETUP.md)**: Deployment guide for new environments
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**: Common issues and solutions  
- **[README_PHASE2.md](README_PHASE2.md)**: Detailed Phase 2 documentation

## 🤝 **Contributing**

When contributing:
1. Never commit `config.py` with real API keys
2. Update `config.example.py` if new keys are needed
3. Test both real and mock modes
4. Update documentation for new features

---

**⚡ This approach is industry standard and will work perfectly for GitHub deployment!**
