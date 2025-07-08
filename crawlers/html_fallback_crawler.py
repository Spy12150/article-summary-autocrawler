from typing import List, Dict
import requests
from bs4 import BeautifulSoup

class HTMLFallbackCrawler:
    def extract_articles(self, url: str, max_articles: int = 3, html_dir: str = "downloaded_htmls") -> List[Dict]:
        events = []
        try:
            response = requests.get(url, timeout=30)
            html = response.text
            # Save HTML for user inspection in a dedicated folder
            import os
            os.makedirs(html_dir, exist_ok=True)
            html_filename = f"downloaded_{url.replace('https://','').replace('http://','').replace('/','_')}.html"
            html_path = os.path.join(html_dir, html_filename)
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"[HTML FALLBACK] Saved HTML to {html_path}. Attempting article extraction...")
            soup = BeautifulSoup(html, 'html.parser')
            homepage_domain = url.split('/')[2]
            candidate_links = set()
            for a in soup.find_all('a', href=True):
                href = a['href']
                if not href.startswith('http'):
                    continue
                if homepage_domain not in href:
                    continue
                if any(x in href for x in ['#', 'login', 'signup', 'register', 'mailto:', 'javascript:']):
                    continue
                candidate_links.add(href)
            print(f"[HTML FALLBACK] Found {len(candidate_links)} candidate article links.")
            extracted = 0
            for article_url in list(candidate_links)[:max_articles]:
                try:
                    article_resp = requests.get(article_url, timeout=20)
                    article_html = article_resp.text
                    article_soup = BeautifulSoup(article_html, 'html.parser')
                    headline_tag = article_soup.find(['h1', 'h2'])
                    headline = headline_tag.get_text(strip=True) if headline_tag else ''
                    content_tag = article_soup.find('article') or article_soup.find('main') or article_soup.find('div', class_=lambda x: x and 'content' in x)
                    content = content_tag.get_text(separator=' ', strip=True) if content_tag else ''
                    date_tag = article_soup.find('time')
                    date = date_tag.get_text(strip=True) if date_tag else ''
                    events.append({
                        'date': date,
                        'headline': headline,
                        'content': content,
                        'article_url': article_url,
                        'source_url': url
                    })
                    extracted += 1
                except Exception as e:
                    print(f"[HTML FALLBACK][ERROR] Failed to extract {article_url}: {e}")
            print(f"[HTML FALLBACK] Extracted {extracted} articles from HTML fallback.")
        except Exception as e:
            print(f"[HTML FALLBACK][ERROR] Failed to download or analyze HTML for {url}: {e}")
        return events
