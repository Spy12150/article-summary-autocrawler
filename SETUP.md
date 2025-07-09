# Setup Guide for Running on Network-Connected Computer

This guide explains how to set up and run the semiconductor news scraper on a computer with network access to the internal LLM endpoint.

## 📋 **Prerequisites**

- Python 3.8 or higher
- Network access to `10.30.15.111:8080`
- Git (for cloning the repository)

## 🚀 **Setup Steps**

### 1. **Clone the Repository**
```bash
git clone <your-github-repo-url>
cd "Innosci Internship Projects"
```

### 2. **Set Up Python Environment**
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install manually:
```bash
pip install requests trafilatura playwright beautifulsoup4 tqdm
```

### 4. **Configure API Keys**
```bash
# Copy the example config file
cp config.example.py config.py

# Edit config.py with your actual API keys
nano config.py  # or use your preferred editor
```

Update `config.py` with:
```python
# LLM API Configuration
INS_API_KEY = "your_actual_ins_api_key_here"

# Google Custom Search API Configuration  
GOOGLE_API_KEY = "your_google_api_key_here"
GOOGLE_CSE_ID = "your_google_cse_id_here"
```

### 5. **Test Network Connectivity**
```bash
# Test the LLM endpoint
python test_connection.py
```

You should see:
```
✅ Main endpoint is accessible
```

## 🏃 **Running the Pipeline**

### **Phase 1: Scrape Articles**
```bash
# Interactive mode - manual URLs
python main.py

# Or with Google search
python main.py
# Choose option 2, enter keywords like "semiconductor news"
```

### **Phase 2: Process with LLM**
```bash
# Process the latest scraped articles
python process_articles.py --input data/article_data1.json

# Or specify exact files
python process_articles.py \
    --input data/article_data9.json \
    --output data/processed_articles.json
```

## 🔧 **Troubleshooting**

### **If LLM Endpoint Still Fails:**
```bash
# Test with mock mode first
python process_articles.py --endpoint 'mock' --input data/article_data1.json

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

## 📊 **Expected Output**

### **Phase 1 Output:**
- `data/article_dataN.json` (where N increments)
- `downloaded_htmls/` folder with raw HTML files

### **Phase 2 Output:**
- `data/articles_processed.json` with sentiment and summaries
- Console output showing processing progress

## 🔒 **Security Notes**

- **Never commit `config.py`** - it's in `.gitignore`
- **Use `config.example.py`** as a template for others
- **Rotate API keys** if they're accidentally exposed
- **Use environment variables** in production environments

## 📈 **Performance Tips**

- **Batch Processing**: Process articles in smaller batches if memory is limited
- **Network Timeouts**: Increase timeout if network is slow:
  ```bash
  # Edit process_articles.py, increase timeout parameter
  ```
- **Parallel Processing**: For large datasets, consider splitting files and running multiple processes

## 🐛 **Common Issues**

| Issue | Solution |
|-------|----------|
| `ImportError: No module named 'config'` | Copy `config.example.py` to `config.py` |
| `Connection refused` | Check VPN/network access to `10.30.15.111` |
| `API key invalid` | Verify API key in `config.py` |
| `FileNotFoundError` | Run Phase 1 first to generate article data |

## 📞 **Support**

If you encounter issues:
1. Check the `TROUBLESHOOTING.md` file
2. Run `python test_connection.py` for diagnostics
3. Verify `config.py` has correct API keys
4. Ensure you're on the correct network for LLM access
