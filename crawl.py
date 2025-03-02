import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from utils import normalize_url, valid_link

visited = set()
site_structure = {}

def extract_links(html, base_url, domain):
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for a in soup.find_all('a', href=True):
        link = href = urljoin(base_url, a['href'])
        link = normalize_url(link, base_url)
        if valid_link(link, domain):
            links.add(link)
    return links

def crawl(url, depth, domain):
    if depth == 0 or url in visited:
        return
    print(f"Crawling: {url}")
    visited.add(url)
    response = requests.get(url)
    if response.ok:
        links = extract_links(response.text, url, domain)
        site_structure[url] = list(links)
        for link in links:
            crawl(link, depth-1, domain)