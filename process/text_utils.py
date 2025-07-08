"""
Text cleaning utilities for web-scraped content.
"""
import re
from bs4 import BeautifulSoup

def clean_text(text: str) -> str:
    """
    Cleans and normalizes text by removing HTML tags, excess whitespace, and unwanted characters.
    """
    # Remove HTML tags
    text = BeautifulSoup(text, 'html.parser').get_text()
    # Remove excess whitespace
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    return text.strip()

