import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from utils import normalize_url, valid_link
from collections import deque
import concurrent.futures


def extract_links(html_content, base_url, domain):
    soup = BeautifulSoup(html_content, 'html.parser')
    seen_links = set()

    for a_tag in soup.select('a[href]'):
        href = a_tag.get('href')
        absolute_url = urljoin(base_url, href)
        parsed_url = urlparse(absolute_url)

        if parsed_url.netloc.endswith(domain):
            normalized_url = normalize_url(absolute_url, base_url)
            if normalized_url not in seen_links:
                seen_links.add(normalized_url)
                yield normalized_url

def process_url(url, current_depth, domain, visited, site_structure):
    print(f"Crawling (BFS) at depth {current_depth}: {url}")
    visited.add(url)
    response = requests.get(url)
    if response.ok:
        soup = BeautifulSoup(response.text, 'html.parser')
        title = str(soup.title.string) if soup.title else "No title"
        links = list(extract_links(response.text, url, domain))
        print(f"Found {len(links)} links on page {url}")
        site_structure[url] = {'title': title, 'links': links}
        return links
    return []

def crawl_bfs(start_url, depth, domain):
    visited = set()
    site_structure = {}
    queue = deque([(start_url, depth)])

    with concurrent.futures.ThreadPoolExecutor() as executor:
        while queue:
            url, current_depth = queue.popleft()
            if current_depth == 0 or url in visited:
                continue
            future_to_url = {executor.submit(process_url, url, current_depth, domain, visited, site_structure): url for url in queue}
            for future in concurrent.futures.as_completed(future_to_url):
                links = future.result()
                for link in links:
                    if link not in visited:
                        queue.append((link, current_depth - 1))

    return site_structure

def crawl_dfs(url, depth, domain, visited=None, site_structure=None):
    if visited is None:
        visited = set()
    if site_structure is None:
        site_structure = {}
    
    if depth == 0 or url in visited:
        return site_structure
    print(f"Crawling (DFS) at depth {depth}: {url}")
    visited.add(url)
    response = requests.get(url)
    if response.ok:
        soup = BeautifulSoup(response.text, 'html.parser')
        title = str(soup.title.string) if soup.title else "No title"
        links = list(extract_links(response.text, url, domain))
        site_structure[url] = {'title': title, 'links': links}
        for link in links:
            if link not in visited:
                crawl_dfs(link, depth - 1, domain, visited, site_structure)
    
    return site_structure
