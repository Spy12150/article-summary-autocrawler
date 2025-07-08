"""
Playwright-based article extraction for dynamic news sites (EETimes example).
"""
from typing import List, Dict
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
import time
import random

class PlaywrightNewsScraper:
    def extract_events(self, url: str, max_articles: int = 3) -> List[Dict]:
        """
        Extracts news articles from a news site using Playwright for JavaScript rendering.
        Returns a list of dicts with date, headline, content, article_url, and source_url.
        """
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
            print(f"[PLAYWRIGHT] Navigating to {url}")
            page.goto(url, timeout=60000)
            time.sleep(2)
            # Example: Collect article links and dates from the listing page, deduplicate URLs
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
            print(f"[PLAYWRIGHT] Total unique article links found: {len(article_info)}")
            # Visit each article and extract details
            for idx, info in enumerate(article_info[:max_articles]):
                article_url = info['url']
                date = info['date']
                print(f"[PLAYWRIGHT] Opening article {idx+1}/{len(article_info)}: {article_url}")
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
                        date_tag = article_page.query_selector('span.articleHeader-date')
                        if date_tag:
                            date_raw = date_tag.inner_text().strip()
                        else:
                            date_tag = article_page.query_selector('span.podcastHeader-date')
                            date_raw = date_tag.inner_text().strip() if date_tag else ''
                        if date_raw:
                            m = re.match(r'^(\d{2})\.(\d{2})\.(\d{4})$', date_raw)
                            if m:
                                date = date_raw
                            else:
                                m2 = re.match(r'^(\d{2})\.(\d{2})\.(\d{2})$', date_raw)
                                if m2:
                                    mm, dd, yy = m2.groups()
                                    date = f"{mm}.{dd}.20{yy}"
                                else:
                                    m3 = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', date_raw)
                                    if m3:
                                        yyyy, mm, dd = m3.groups()
                                        date = f"{mm}.{dd}.{yyyy}"
                                    else:
                                        date = date_raw
                    print(f"[PLAYWRIGHT] Extracted: headline='{headline[:30]}', date='{date}', content length={len(content)}")
                    events.append({
                        'date': date,
                        'headline': headline,
                        'content': content,
                        'article_url': article_url,
                        'source_url': url
                    })
                except Exception as e:
                    print(f"[PLAYWRIGHT][ERROR] Failed to extract {article_url}: {e}")
                finally:
                    article_page.close()
            browser.close()
        return events
