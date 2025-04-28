import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_URL = 'https://isss.umbc.edu/'
HEADERS = {"User-Agent": "Mozilla/5.0"}
VISITED = set()
OUTPUT_DIR = 'isss_scraped_pages'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def is_valid_url(url):
    # Only follow links within the base domain
    parsed = urlparse(url)
    return url.startswith(BASE_URL) and not any([
        url.startswith("mailto:"),
        url.endswith(".pdf"),
        parsed.path.startswith("/calendar")
    ])

def sanitize_filename(url):
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "_") or "home"
    return path if path.endswith(".txt") else path + ".txt"

def scrape_page(url):
    if url in VISITED:
        return
    try:
        print(f"Scraping: {url}")
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"Skipped {url}: status code {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        VISITED.add(url)

        # Extract meaningful text
        content = []
        for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'li']):
            text = tag.get_text(strip=True)
            if text:
                content.append(text)

        # Save unique content
        if content:
            file_name = sanitize_filename(url)
            with open(os.path.join(OUTPUT_DIR, file_name), "w", encoding='utf-8') as f:
                for line in content:
                    f.write(line + "\n")

        # Recurse into valid links
        for a in soup.find_all("a", href=True):
            next_url = urljoin(url, a['href'].split('#')[0])
            if is_valid_url(next_url) and next_url not in VISITED:
                time.sleep(0.5)
                scrape_page(next_url)

    except Exception as e:
        print(f"Error scraping {url}: {e}")

# Start scraping
scrape_page(BASE_URL)
print(f"✅ Scraping complete. {len(VISITED)} pages visited.")
