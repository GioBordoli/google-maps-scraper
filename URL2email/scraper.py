import requests
import re
from urllib.parse import urljoin, urlparse
import sys

def find_emails(url, max_pages=10):
    """
    Crawls a website to find email addresses.

    Args:
        url: The starting URL to crawl.
        max_pages: The maximum number of pages to crawl.

    Returns:
        A set of unique email addresses found.
    """
    visited_urls = set()
    emails = set()
    urls_to_visit = [url]

    while urls_to_visit and len(visited_urls) < max_pages:
        current_url = urls_to_visit.pop(0)
        if current_url in visited_urls:
            continue

        try:
            response = requests.get(current_url, timeout=5)
            response.raise_for_status()  # Raise an exception for bad status codes
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {current_url}: {e}")
            continue

        visited_urls.add(current_url)

        # Find emails
        found_emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", response.text)
        emails.update(found_emails)

        # Find links
        links = re.findall(r"href=['\"]?([^'\"] >)+", response.text)
        for link in links:
            absolute_link = urljoin(current_url, link)
            if urlparse(absolute_link).netloc == urlparse(url).netloc:
                if absolute_link not in visited_urls and len(urls_to_visit) + len(visited_urls) < max_pages:
                    urls_to_visit.append(absolute_link)

    return emails

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scraper.py <URL>")
        sys.exit(1)

    start_url = sys.argv[1]
    found_emails = find_emails(start_url)

    if found_emails:
        print("Found the following email addresses:")
        for email in found_emails:
            print(email)
    else:
        print("No email addresses found.")