from typing import List, Dict
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
import time
import random
from urllib.parse import urljoin

class PlaywrightCrawler:
    def extract_articles(self, url: str, max_articles: int = 3, filter_func=None) -> List[Dict]:
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
            article_info = []
            seen_urls = set()
            # IMPROVED: Find <a> tags with likely article links, including those with h2/h3 children or special classes
            links = page.query_selector_all('a, a.article-links, a[target], a[href]')
            for link in links:
                href = link.get_attribute('href')
                if not href:
                    continue
                # Accept if:
                # - href matches news/article/story/date pattern
                # - OR has class 'article-links'
                # - OR contains h2/h3 child (headline in link)
                # - OR parent has class 'resource-item-meta' or 'card-title'
                is_article = False
                class_attr = link.get_attribute('class') or ''
                if re.search(r'/news/|/article/|/story/|/202\\d|/20\\d\\d', href) and not href.startswith('#') and not href.startswith('javascript:'):
                    is_article = True
                if 'article-links' in class_attr:
                    is_article = True
                # Check for h2/h3 child (headline in link)
                if link.query_selector('h2, h3'):
                    is_article = True
                # Check for parent with resource/card class
                parent_class = link.evaluate('el => el.parentElement ? el.parentElement.className : ""')
                if 'resource-item-meta' in parent_class or 'card-title' in parent_class:
                    is_article = True
                if not is_article:
                    continue
                # Make absolute URL
                if href.startswith('http'):
                    article_url = href
                else:
                    article_url = urljoin(page.url, href)
                if article_url in seen_urls:
                    continue
                seen_urls.add(article_url)
                article_info.append({'url': article_url, 'date': ''})
            print(f"[PLAYWRIGHT] Total unique article links found: {len(article_info)}")
            usable_events = []
            for idx, info in enumerate(article_info):
                if len(usable_events) >= max_articles:
                    break
                article_url = info['url']
                date = info['date']
                print(f"[PLAYWRIGHT] Opening article {idx+1}/{len(article_info)}: {article_url}")
                article_page = context.new_page()
                try:
                    article_page.goto(article_url, timeout=30000)
                    # Try multiple headline selectors, including h2/h3 in <a>
                    headline = ''
                    for selector in ['h1', 'h2', 'h3', 'meta[property="og:title"]', 'meta[name="twitter:title"]']:
                        el = article_page.query_selector(selector)
                        if el:
                            if selector.startswith('meta'):
                                headline = el.get_attribute('content') or ''
                            else:
                                headline = el.inner_text().strip()
                            if headline:
                                break
                    # Try multiple content selectors
                    content = ''
                    for selector in ['article', 'div[class*="content"]', 'div[class*="body"]', 'div[class*="main"]', 'section[class*="content"]', 'main', 'body']:
                        el = article_page.query_selector(selector)
                        if el:
                            content = el.inner_text().strip()
                            if len(content) > 200:
                                break
                    # Try to extract date from meta tags or <time> or from referring page (resource-item-meta)
                    if not date:
                        date_selectors = [
                            'meta[property="article:published_time"]',
                            'meta[name="datePublished"]',
                            'meta[name="pubdate"]',
                            'time',
                            'span[class*="date"]',
                        ]
                        for selector in date_selectors:
                            el = article_page.query_selector(selector)
                            if el:
                                if selector.startswith('meta'):
                                    date_raw = el.get_attribute('content') or ''
                                else:
                                    date_raw = el.inner_text().strip()
                                if date_raw:
                                    date = date_raw
                                    break
                    event = {
                        'date': date,
                        'headline': headline,
                        'content': content,
                        'article_url': article_url,
                        'source_url': url
                    }
                    # Filtering here
                    if filter_func:
                        if filter_func(event):
                            usable_events.append(event)
                    else:
                        if event.get('content') and len(event['content'].strip()) >= 200 and event.get('headline') and len(event['headline'].strip()) > 0:
                            usable_events.append(event)
                    print(f"[PLAYWRIGHT] Extracted: headline='{headline[:30]}', date='{date}', content length={len(content)}")
                except Exception as e:
                    print(f"[PLAYWRIGHT][ERROR] Failed to extract {article_url}: {e}")
                finally:
                    article_page.close()
            browser.close()
        return usable_events
