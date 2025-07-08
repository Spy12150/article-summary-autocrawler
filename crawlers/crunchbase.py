"""
CrunchbaseCrawler scrapes timeline events from a Crunchbase organization page using Playwright for JavaScript rendering.
"""
from typing import List, Dict
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import trafilatura
import requests
from urllib.parse import urljoin

class CrunchbaseCrawler:
    def extract_events(self, url: str) -> List[Dict]:
        """
        Extracts news articles from the EETimes GaN tag page by visiting each article link.
        Returns a list of dicts with date, headline, content, article_url, and source_url.
        """
        import random
        import time
        import re
        events = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=[
                '--disable-blink-features=AutomationControlled',
                '--start-maximized',
            ])
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                locale="en-US"
            )
            page = context.new_page()
            print(f"[DEBUG] Navigating to {url}")
            page.goto(url, timeout=60000)
            time.sleep(2)
            # Collect article links and dates from the listing page, deduplicate URLs
            article_info = []
            seen_urls = set()
            cards = page.query_selector_all('a.article-links')
            for link in cards:
                href = link.get_attribute('href')
                date = ''
                try:
                    card = link.evaluate_handle('el => el.closest(".card")')
                    if card:
                        card_info = card.query_selector('.card-info')
                        if card_info:
                            card_info_text = card_info.inner_text().strip()
                            m = re.search(r'(\d{2}\.\d{2}\.\d{4})', card_info_text)
                            if m:
                                date = m.group(1)
                except Exception:
                    pass
                if href and href.startswith('http'):
                    article_url = href
                elif href:
                    article_url = page.url.rstrip('/') + '/' + href.lstrip('/')
                else:
                    continue
                if article_url in seen_urls:
                    continue
                seen_urls.add(article_url)
                article_info.append({'url': article_url, 'date': date})
            print(f"[DEBUG] Total unique article links found: {len(article_info)}")
            # Visit each article and extract details
            for idx, info in enumerate(article_info):
                article_url = info['url']
                date = info['date']
                print(f"[DEBUG] Opening article {idx+1}/{len(article_info)}: {article_url}")
                article_page = context.new_page()
                try:
                    article_page.goto(article_url, timeout=30000)
                    article_page.wait_for_selector('h1, h2', timeout=10000)
                    time.sleep(random.uniform(1, 2))
                    headline = ''
                    content = ''
                    # Headline
                    h_tag = article_page.query_selector('h1, h2')
                    if h_tag:
                        headline = h_tag.inner_text().strip()
                    # Main content (try several selectors)
                    content_tag = article_page.query_selector('div.article-content, div.entry-content, article, main')
                    if content_tag:
                        content = content_tag.inner_text().strip()
                    # If date is still empty, try to extract from article page
                    if not date:
                        # Try .articleHeader-date
                        date_tag = article_page.query_selector('span.articleHeader-date')
                        if date_tag:
                            date_raw = date_tag.inner_text().strip()
                        else:
                            # Try .podcastHeader-date
                            date_tag = article_page.query_selector('span.podcastHeader-date')
                            date_raw = date_tag.inner_text().strip() if date_tag else ''
                        # Normalize date to MM.DD.YYYY if possible
                        if date_raw:
                            # Accepts MM.DD.YYYY, MM.DD.YY, or MM.DD.YY (with/without leading zero)
                            m = re.match(r'^(\d{2})\.(\d{2})\.(\d{4})$', date_raw)
                            if m:
                                date = date_raw
                            else:
                                # Try to convert MM.DD.YY or MM.DD.YY to MM.DD.20YY
                                m2 = re.match(r'^(\d{2})\.(\d{2})\.(\d{2})$', date_raw)
                                if m2:
                                    mm, dd, yy = m2.groups()
                                    date = f"{mm}.{dd}.20{yy}"
                                else:
                                    # Try YYYY-MM-DD or similar
                                    m3 = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', date_raw)
                                    if m3:
                                        yyyy, mm, dd = m3.groups()
                                        date = f"{mm}.{dd}.{yyyy}"
                                    else:
                                        date = date_raw  # fallback, keep as is
                    print(f"[DEBUG] Extracted: headline='{headline[:30]}', date='{date}', content length={len(content)}")
                    events.append({
                        'date': date,
                        'headline': headline,
                        'content': content,
                        'article_url': article_url,
                        'source_url': url
                    })
                except Exception as e:
                    print(f"[ERROR] Failed to extract {article_url}: {e}")
                finally:
                    article_page.close()
            browser.close()
        return events

    def extract_events_from_html(self, html_path: str) -> List[Dict]:
        """
        Extracts news articles from a saved EETimes GaN tag HTML file.
        Returns a list of dicts with date, headline, content, and source_url.
        """
        events = []
        with open(html_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            # EETimes article cards: typically <article> or <div class="river-item"> or similar
            for article in soup.select('article, .river-item'):
                # Headline: usually in <h2> or <h3> with a link
                headline_tag = article.find(['h2', 'h3'])
                headline = headline_tag.get_text(strip=True) if headline_tag else ''
                link_tag = headline_tag.find('a') if headline_tag else None
                url = link_tag['href'] if link_tag and link_tag.has_attr('href') else ''
                # Date: often in <time> or a <span> with date class
                date_tag = article.find('time') or article.find('span', class_='date')
                date = date_tag.get_text(strip=True) if date_tag else ''
                # Content/summary: often in <p> or <div class="excerpt">
                content_tag = article.find('p') or article.find('div', class_='excerpt')
                content = content_tag.get_text(strip=True) if content_tag else ''
                events.append({
                    'date': date,
                    'headline': headline,
                    'content': content,
                    'article_url': url,
                    'source_url': html_path
                })
        return events

    def extract_articles_trafilatura(self, url: str, testing_mode: bool = False) -> List[Dict]:
        """
        Extracts articles from a general news homepage using trafilatura and BeautifulSoup for link discovery.
        If testing_mode is True, only extracts 3 articles and prints debug output.
        """
        import requests
        from urllib.parse import urljoin, urlparse
        events = []
        print(f"[DEBUG] Downloading {url}")
        response = requests.get(url, timeout=30)
        if not response.ok:
            print(f"[ERROR] Failed to fetch {url}: {response.status_code}")
            return events
        soup = BeautifulSoup(response.text, 'html.parser')
        homepage_domain = urlparse(url).netloc
        # Collect all candidate article links
        candidate_links = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Make absolute URL
            full_url = urljoin(url, href)
            # Only keep links on the same domain, not navigation, not login, not duplicate
            if homepage_domain not in urlparse(full_url).netloc:
                continue
            if any(x in full_url for x in ['#', 'login', 'signup', 'register', 'mailto:', 'javascript:']):
                continue
            if full_url in candidate_links:
                continue
            # Heuristic: likely article if:
            # - contains /news/, /article/, /story/
            # - ends with .html, .shtml, .shtm
            # - parent div class contains 'teaser'
            # - link class contains 'heading-link' or 'teaser'
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
        print(f"[DEBUG] Found {len(candidate_links)} candidate links on {url}")
        count = 0
        for article_url in candidate_links:
            downloaded = trafilatura.fetch_url(article_url)
            if not downloaded:
                print(f"[DEBUG] Skipping (no content): {article_url}")
                continue
            data = trafilatura.extract(downloaded, output_format='json', with_metadata=True)
            if not data:
                print(f"[DEBUG] Skipping (not an article): {article_url}")
                continue
            import json as _json
            article = _json.loads(data)
            headline = article.get('title', '')
            content = article.get('text', '')
            date = article.get('date', '')
            print(f"[DEBUG] Extracted: headline='{headline[:30]}', date='{date}', url={article_url}")
            events.append({
                'date': date,
                'headline': headline,
                'content': content,
                'article_url': article_url,
                'source_url': url
            })
            count += 1
            if testing_mode and count >= 3:
                break
        print(f"[DEBUG] Total articles extracted from {url}: {len(events)}")
        return events
