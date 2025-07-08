"""
BaseCrawler provides common HTTP fetching utilities and error handling for all crawlers.
"""
import requests
from typing import Optional

class BaseCrawler:
    def __init__(self, headers: Optional[dict] = None):
        self.session = requests.Session()
        # Set a default browser-like User-Agent if not provided
        default_headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/124.0.0.0 Safari/537.36'
            ),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
        }
        self.session.headers.update(default_headers)
        if headers:
            self.session.headers.update(headers)

    def fetch(self, url: str, timeout: int = 10) -> Optional[str]:
        """Fetches the content of a URL with error handling."""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
