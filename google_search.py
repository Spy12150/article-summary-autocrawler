import requests

"""
This file allows the user to input search term and the program will use google custom search API to access the links
"""


# Try to import config, fall back to environment variables
try:
    from config import GOOGLE_API_KEY, GOOGLE_CSE_ID
    API_KEY = GOOGLE_API_KEY
    SEARCH_ENGINE_ID = GOOGLE_CSE_ID
except ImportError:
    import os
    API_KEY = os.getenv("GOOGLE_API_KEY", "your_google_api_key_here")
    SEARCH_ENGINE_ID = os.getenv("GOOGLE_CSE_ID", "your_google_cse_id_here")


def google_search(query, total_results=10):
    """
    Perform a Google search using the Custom Search JSON API.
    Returns a list of result URLs, up to total_results.
    """
    all_links = []
    results_per_page = 10  # Google API max per page
    num_pages = (total_results + results_per_page - 1) // results_per_page
    for page in range(num_pages):
        start = page * results_per_page + 1
        num = min(results_per_page, total_results - len(all_links))
        url = (
            f"https://www.googleapis.com/customsearch/v1?key={API_KEY}"
            f"&cx={SEARCH_ENGINE_ID}&q={query}&start={start}&num={num}"
        )
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"[ERROR] Google API error: {resp.status_code} {resp.text}")
            break
        data = resp.json()
        items = data.get("items", [])
        for item in items:
            link = item.get("link")
            if link:
                all_links.append(link)
        if len(all_links) >= total_results or len(items) < num:
            break  # Got enough or no more results
    return all_links


def prompt_google_search():
    query = input("Enter a Google search keyword (e.g. 'Semiconductor news'): ").strip()
    while not query:
        print("Keyword cannot be empty.")
        query = input("Enter a Google search keyword: ").strip()
    while True:
        try:
            total_results = int(input("How many Google search results to fetch? (e.g. 17): ").strip())
            if total_results < 1:
                print("Please enter a positive integer.")
                continue
            break
        except ValueError:
            print("Please enter a valid integer.")
    print(f"[GOOGLE] Searching for '{query}' (fetching {total_results} results)...")
    links = google_search(query, total_results=total_results)
    print(f"[GOOGLE] Found {len(links)} links.")
    for i, link in enumerate(links, 1):
        print(f"  {i}. {link}")
    return links
