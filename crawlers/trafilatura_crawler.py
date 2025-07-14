from typing import List, Dict
import trafilatura
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse

"""The default crawler, the fastest and most efficient, good enough for most articles"""

class TrafilaturaCrawler:
    def extract_articles(self, url: str, max_articles: int = 3) -> List[Dict]:
        events = []
        print(f"[TRAFILATURA] Downloading {url}")
        try:
            response = requests.get(url, timeout=30)
        except Exception as e:
            print(f"[TRAFILATURA][ERROR] Failed to fetch {url}: {e}")
            return events
        if not response.ok:
            print(f"[TRAFILATURA][ERROR] Failed to fetch {url}: {response.status_code}")
            return events
        soup = BeautifulSoup(response.text, 'html.parser')
        homepage_domain = urlparse(url).netloc
        candidate_links = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(url, href)
            if homepage_domain not in urlparse(full_url).netloc:
                continue
            if any(x in full_url for x in ['#', 'login', 'signup', 'register', 'mailto:', 'javascript:']):
                continue
            if full_url in candidate_links:
                continue
            parent = a.find_parent()
            parent_class = ' '.join(parent.get('class', [])) if parent else ''
            link_class = ' '.join(a.get('class', []))
            if (
                any(x in full_url for x in ['/news/', '/article/', '/story/']) or
                full_url.endswith('.html') or full_url.endswith('.shtml') or full_url.endswith('.shtm') or
                'teaser' in parent_class or
                'teaser' in link_class or
                'heading-link' in link_class
            ):
                candidate_links.add(full_url)
        print(f"[TRAFILATURA] Found {len(candidate_links)} candidate links on {url}")
        count = 0
        for article_url in candidate_links:
            downloaded = trafilatura.fetch_url(article_url)
            if not downloaded:
                continue
            data = trafilatura.extract(downloaded, output_format='json', with_metadata=True)
            if not data:
                continue
            import json as _json
            article = _json.loads(data)
            headline = article.get('title', '')
            content = article.get('text', '')
            date = article.get('date', '')
            events.append({
                'date': date,
                'headline': headline,
                'content': content,
                'article_url': article_url,
                'source_url': url
            })
            count += 1
            if count >= max_articles:
                break
        print(f"[TRAFILATURA] Total articles extracted from {url}: {len(events)}")
        return events
