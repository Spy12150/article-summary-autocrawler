"""
General-purpose news article scraper using trafilatura, with interactive CLI for user input.
"""
import os
import json
import requests
from crawlers.crunchbase import CrunchbaseCrawler
from crawlers.trafilatura_crawler import TrafilaturaCrawler
from crawlers.playwright_crawler import PlaywrightCrawler
from crawlers.html_fallback_crawler import HTMLFallbackCrawler
from playwright_scraper import PlaywrightNewsScraper
from bs4 import BeautifulSoup

def main():
    print("Welcome to the General News Article Scraper (trafilatura + Playwright fallback)")
    print("Choose input method:")
    print("  1. Enter news homepage URLs manually")
    print("  2. Search Google for news sites by keyword")
    method = input("Enter 1 or 2: ").strip()
    urls = []
    num_articles = []
    if method == '2':
        from google_search import prompt_google_search
        links = prompt_google_search()
        if not links:
            print("[ERROR] No links found from Google search. Exiting.")
            return
        while True:
            try:
                per_page = int(input("How many articles to pull from each found site? (e.g. 3): ").strip())
                if per_page < 1:
                    print("Please enter a positive integer.")
                    continue
                break
            except ValueError:
                print("Please enter a valid integer.")
        for link in links:
            urls.append(link)
            num_articles.append(per_page)
    else:
        print("You can add as many news homepages as you like.")
        while True:
            url = input("Enter a news homepage URL: ").strip()
            if not url:
                print("URL cannot be empty. Please try again.")
                continue
            while True:
                try:
                    n = int(input(f"How many articles to pull from {url}? (e.g. 3): ").strip())
                    if n < 1:
                        print("Please enter a positive integer.")
                        continue
                    break
                except ValueError:
                    print("Please enter a valid integer.")
            urls.append(url)
            num_articles.append(n)
            more = input("Do you have more websites to add? (y/n): ").strip().lower()
            if more != 'y':
                break
    all_events = []
    crawler = TrafilaturaCrawler()
    playwright_crawler = PlaywrightCrawler()
    html_fallback_crawler = HTMLFallbackCrawler()
    HTML_DIR = os.path.join(os.path.dirname(__file__), 'downloaded_htmls')
    os.makedirs(HTML_DIR, exist_ok=True)
    for url, n in zip(urls, num_articles):
        print(f"\n[SCRAPE] {url} (max {n} articles)...")
        # Try trafilatura first
        try:
            events = crawler.extract_articles(url, max_articles=n)
        except Exception as e:
            print(f"[ERROR] Trafilatura failed for {url}: {e}")
            events = []
        if not events:
            print(f"[INFO] Trafilatura found no articles for {url}, trying Playwright...")
            try:
                events = playwright_crawler.extract_articles(url, max_articles=n)
            except Exception as e:
                print(f"[ERROR] Playwright failed for {url}: {e}")
                events = []
        if not events:
            print(f"[INFO] Both trafilatura and Playwright failed for {url}. Using HTML fallback...")
            events = html_fallback_crawler.extract_articles(url, max_articles=n, html_dir=HTML_DIR)
        all_events.extend(events[:n])
    print(f"\n[SCRAPE] Total articles extracted from all sites: {len(all_events)}")
    # Filter out short or empty articles (e.g., content < 200 chars or missing headline/content)
    filtered_events = [
        event for event in all_events
        if event.get('content') and len(event['content'].strip()) >= 200 and event.get('headline') and len(event['headline'].strip()) > 0
    ]
    print(f"[SCRAPE] Articles after filtering short/empty content: {len(filtered_events)}")
    # Save to a test output file with incrementing number (no repeats) in data folder
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(DATA_DIR, exist_ok=True)
    base = os.path.join(DATA_DIR, 'article_data')
    n = 1
    while os.path.exists(f"{base}{n}.json"):
        n += 1
    test_output = f"{base}{n}.json"
    with open(test_output, 'w', encoding='utf-8') as f:
        json.dump(filtered_events, f, ensure_ascii=False, indent=2)
    print(f"[SCRAPE] Saved results to {test_output}")

if __name__ == "__main__":
    main()
