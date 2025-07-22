# MySQL Database Setup Guide

This guide will help you set up MySQL database integration for the Article Summary Pipeline. Perfect for users new to SQL!

## 📋 Prerequisites

- ✅ MySQL Server 5.7+ installed locally
- ✅ MySQL Workbench 6.3 CE installed
- ✅ Python 3.7+ with pip

## 🚀 Step-by-Step Setup

### Step 1: Install Python Dependencies

Open PowerShell and navigate to your project directory:

```powershell
cd "c:\Users\MaximeWang\Documents\maximecode\article-summary-autocrawler"
pip install -r requirements.txt
```

### Step 2: Set Up MySQL Database

1. **Open MySQL Workbench**
   - Launch MySQL Workbench 6.3 CE
   - Connect to your local MySQL server (usually `localhost:3306`)

2. **Run the Setup Script**
   - In MySQL Workbench, open the file: `database/setup.sql`
   - Click the ⚡ **Execute** button (or press Ctrl+Shift+Enter)
   - This will create:
     - Database: `article_summary_db`
     - Tables: `articles` and `quality_factors`
     - User: `article_user` with appropriate permissions

3. **Verify Setup**
   - In the left panel, refresh and look for `article_summary_db`
   - Expand it to see the `articles` and `quality_factors` tables

### Step 3: Configure Database Connection

1. **Set Your MySQL Password**
   - Remember the password you set for `article_user` in the setup script
   - You'll need this for all database operations

2. **Test Connection**
   - Run the test script to verify everything works:
   ```powershell
   python database/test_db.py
   ```
   - Choose option "2" for a quick status check
   - Enter your MySQL password when prompted

### Step 4: Migrate Existing Data

If you have existing article data in JSON files:

```powershell
python database/migrate_data.py
```

This will:
- Guide you through the migration process
- Move data from `data/articles_processed.json` to MySQL
- Show progress and summary

## 🗂️ Database Schema

### Articles Table
Stores main article information:
- `id` - Unique identifier (auto-increment)
- `date` - Article publication date
- `headline` - Article title
- `article_url` - Direct link to article
- `source_url` - Source page URL
- `content_hash` - Unique content identifier
- `quality_score` - Article quality rating (1-10)
- `content_length` - Text length in characters
- `sentence_count` - Number of sentences
- `tech_keyword_count` - Number of technical keywords
- `sentiment` - Sentiment analysis result
- `summary` - Article summary
- `relevant` - Relevance flag
- `processing_status` - Processing result status
- `created_at` - Record creation timestamp

### Quality Factors Table
Stores quality assessment tags:
- `id` - Unique identifier
- `article_id` - Reference to articles table
- `factor_name` - Quality factor name (e.g., "excellent_length")

## 🔧 Usage Examples

### Basic Operations

```python
from database.db_manager import DatabaseManager

# Initialize connection
db = DatabaseManager(password='your_mysql_password')

# Test connection
if db.test_connection():
    print("Connected successfully!")

# Get article count
count = db.count_articles()
print(f"Total articles: {count}")

# Get recent articles
recent = db.get_recent_articles(10)
for article in recent:
    print(f"{article['date']}: {article['headline']}")

# Get articles by date range
from datetime import datetime, timedelta
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
weekly_articles = db.get_articles_by_date_range(start_date, end_date)

# Clean up
db.disconnect()
```

### Integration with Existing Pipeline

```python
# In your processing script
from database.db_manager import DatabaseManager

def process_and_store_article(article_data):
    """Process article and store in database"""
    db = DatabaseManager(password='your_password')
    
    # Check if article already exists
    existing = db.get_article_by_hash(article_data['content_hash'])
    if existing:
        print("Article already processed")
        return
    
    # Insert new article
    if db.insert_article(article_data):
        print("Article stored successfully")
    else:
        print("Failed to store article")
    
    db.disconnect()
```

## 🔍 File Structure

After setup, your project will have:

```
article-summary-autocrawler/
├── database/
│   ├── __init__.py
│   ├── setup.sql           # Database schema and user setup
│   ├── db_manager.py       # Main database operations
│   ├── migrate_data.py     # JSON to MySQL migration
│   ├── test_db.py          # Testing and validation
│   └── db_config_template.py # Configuration template
├── data/
│   ├── articles_processed.json # Existing JSON data
│   └── ...
└── requirements.txt        # Updated with MySQL dependency
```

## 🛠️ Troubleshooting

### Common Issues

**1. Connection Failed**
- ✅ Check MySQL server is running
- ✅ Verify credentials (username: `article_user`)
- ✅ Ensure database `article_summary_db` exists
- ✅ Run `database/setup.sql` if tables are missing

**2. Permission Denied**
- ✅ Check user `article_user` has proper permissions
- ✅ Re-run the setup.sql script
- ✅ Verify password is correct

**3. Import Errors**
- ✅ Install dependencies: `pip install mysql-connector-python`
- ✅ Check Python path and project structure

**4. Migration Issues**
- ✅ Ensure JSON files exist in `data/` directory
- ✅ Check JSON format is valid
- ✅ Verify database connection before migration

### Testing Commands

```powershell
# Test database connection
python database/test_db.py

# Check if MySQL is running
mysql --version

# Test Python MySQL connector
python -c "import mysql.connector; print('MySQL connector installed')"
```

## 🎯 Next Steps

1. **✅ Complete Setup** - Follow all steps above
2. **🔄 Migrate Data** - Move existing JSON data to MySQL
3. **🧪 Test Operations** - Verify all database functions work
4. **🔗 Integrate** - Update your processing scripts to use MySQL
5. **📊 Build API** - Create REST endpoints for frontend access

## 💡 Pro Tips

- **Backup**: Always backup your JSON data before migration
- **Security**: Use strong passwords and consider SSL for production
- **Performance**: Add indexes for frequently queried columns
- **Monitoring**: Use MySQL Workbench to monitor database performance
- **Scaling**: Consider connection pooling for high-volume applications

## 📞 Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Run the test script: `python database/test_db.py`
3. Verify MySQL server status in MySQL Workbench
4. Check the database logs for error messages

Happy coding! 🚀
