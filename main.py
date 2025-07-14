import os
import json
import requests
import time
from crawlers.trafilatura_crawler import TrafilaturaCrawler
from crawlers.playwright_crawler import PlaywrightCrawler
from crawlers.html_fallback_crawler import HTMLFallbackCrawler
from playwright_scraper import PlaywrightNewsScraper
from bs4 import BeautifulSoup

"""Entry point for web scraper, which accesses all three crawlers and logs progress for the user"""

# TODO:
# Single-threaded: No concurrent processing for multiple sites
# Memory usage: Loads all articles into memory at once
# No caching: Re-scrapes same URLs every time

# Time handling: Allow user to control time value handling in future
# Error handling: Using print statements instead of proper logging

# Increase endpoint count: consider scraping multiple or multiple LLM endpoints at the same time
# API limiting: a potential concern but likely not
# API verification: verify api keys before processing

# LLM prompts: Need to make much better prompts to improve result gathering, and also translate to chinese

def main():
    # Pseudo frontend for now in the terminal
    # Allows the user to either enter links for now or use search terms to grab sites
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
    trafilatura_count = 0
    playwright_count = 0
    html_count = 0
    start_time = time.time()
    # A triple approach to cover as many articles as possible
    # In my testing so far trafilatura captures roughly half successfully, HTML captures 40% of what's left, and playwright covers 40% of what's left after, so about 80% of all links it can capture
    # However none of the solutions can overcome anti bot verifications
    for url, n in zip(urls, num_articles):
        print(f"\n[SCRAPE] {url} (max {n} usable articles)...")
        usable_events = []
        used_trafilatura = 0
        used_html = 0
        used_playwright = 0
        # Here I use trafilatura first because it takes the least time and file size
        try:
            events = crawler.extract_articles(url, max_articles=n*3)  # Fetch more to allow for filtering
            # Filter out all content below 200 characters (non-articles)
            filtered = [event for event in events if event.get('content') and len(event['content'].strip()) >= 200 and event.get('headline') and len(event['headline'].strip()) > 0]
            for event in filtered:
                if len(usable_events) >= n:
                    break
                usable_events.append(event)
                used_trafilatura += 1
        except Exception as e:
            print(f"[ERROR] Trafilatura failed for {url}: {e}")
        if len(usable_events) < n:
            print(f"[INFO] Trafilatura found {len(usable_events)} usable articles for {url}, trying HTML fallback...")
            #try HTML next because it is the second fastest, although needs to download files
            try:
                events = html_fallback_crawler.extract_articles(url, max_articles=(n-len(usable_events))*3, html_dir=HTML_DIR)
                filtered = [event for event in events if event.get('content') and len(event['content'].strip()) >= 200 and event.get('headline') and len(event['headline'].strip()) > 0]
                for event in filtered:
                    if len(usable_events) >= n:
                        break
                    usable_events.append(event)
                    used_html += 1
            except Exception as e:
                print(f"[ERROR] HTML fallback failed for {url}: {e}")
        # Next is playwright, which with headless mode off opens a physical page using chromium, which simulates a real human more than the other methods, which bypasses SOME anti-scraper measures
        # This is the slowest, and will not work without a GUI on cloud networks
        if len(usable_events) < n:
            print(f"[INFO] Trafilatura and HTML fallback found {len(usable_events)} usable articles for {url}, trying Playwright...")
            try:
                def filter_func(event):
                    return event.get('content') and len(event['content'].strip()) >= 200 and event.get('headline') and len(event['headline'].strip()) > 0
                events = playwright_crawler.extract_articles(url, max_articles=(n-len(usable_events)), filter_func=filter_func)
                for event in events:
                    if len(usable_events) >= n:
                        break
                    usable_events.append(event)
                    used_playwright += 1
            except Exception as e:
                print(f"[ERROR] Playwright failed for {url}: {e}")
        # Track effectiveness of each method for future improvements and debugging
        trafilatura_count += used_trafilatura
        html_count += used_html
        playwright_count += used_playwright
        all_events.extend(usable_events[:n])
    print(f"\n[SCRAPE] Total articles extracted from all sites: {len(all_events)}")
    filtered_events = []
    short_or_empty_count = 0
    per_site_counts = []
    idx = 0
    # Track filtering statistics
    for url, n in zip(urls, num_articles):
        site_events = all_events[idx:idx+n]
        site_filtered = [
            event for event in site_events
            if event.get('content') and len(event['content'].strip()) >= 200 and event.get('headline') and len(event['headline'].strip()) > 0
        ]
        filtered_events.extend(site_filtered)
        cut_count = len(site_events) - len(site_filtered)
        short_or_empty_count += cut_count
        per_site_counts.append((url, len(site_events), len(site_filtered), cut_count))
        idx += n
    # Reporting to user, could improve with propper logging in future
    print(f"[SCRAPE] Articles after filtering short/empty content: {len(filtered_events)}")
    print(f"[SCRAPE] Filtered out {short_or_empty_count} articles for being too short or empty.")
    print("[SCRAPE] Per-site extraction summary:")
    for url, total, kept, cut in per_site_counts:
        print(f"  {url}\n    Extracted: {total}, Usable: {kept}, Filtered: {cut}")
    print(f"[SCRAPE] Final usable articles: {len(filtered_events)} out of {len(all_events)} extracted, out of {sum(num_articles)} requested.")
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
    end_time = time.time()
    print(f"[SCRAPE] Trafilatura scraped: {trafilatura_count}")
    print(f"[SCRAPE] HTML fallback scraped: {html_count}")
    print(f"[SCRAPE] Playwright scraped: {playwright_count}")
    print(f"[SCRAPE] Total scraping time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
