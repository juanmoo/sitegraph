import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from utils import normalize_url, valid_link
from collections import deque
import concurrent.futures
import logging
import time

# Create a logger object
logger = logging.getLogger('crawler')
logger.setLevel(logging.INFO)

# Create a file handler
handler = logging.FileHandler('crawler.log')
handler.setLevel(logging.INFO)

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(handler)

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
    start_time = time.time()
    logger.info(f"Start processing URL: {url}")
    visited.add(url)
    response = requests.get(url)
    if response.ok:
        soup = BeautifulSoup(response.text, 'html.parser')
        title = str(soup.title.string) if soup.title else "No title"
        links = list(extract_links(response.text, url, domain))
        logger.info(f"Found {len(links)} links on page {url}")
        site_structure[url] = {'title': title, 'links': links}
        end_time = time.time()
        elapsed = end_time - start_time
        logger.info(f"Finished processing URL: {url}. Time taken: {elapsed:.2f} seconds")
        return links
    else:
        logger.warning(f"Failed to retrieve URL: {url} with status code {response.status_code}")
    return []

def crawl_bfs(start_url, depth, domain):
    visited = set()
    site_structure = {}
    queue = deque([(start_url, depth)])
    total_urls = 0
    start_time = time.time()
    last_log_time = start_time

    logger.info(f"Starting BFS crawl from {start_url} with depth {depth}")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        while queue:
            url, current_depth = queue.popleft()
            logger.debug(f"Dequeued URL: {url} at depth {current_depth}")

            if current_depth == 0:
                logger.debug(f"Reached maximum depth at URL: {url}")
                continue
            if url in visited:
                logger.debug(f"Already visited URL: {url}")
                continue

            future = executor.submit(process_url, url, current_depth, domain, visited, site_structure)
            links = future.result()
            total_urls += len(links)

            current_time = time.time()
            if current_time - last_log_time >= 5:
                elapsed = current_time - start_time
                rate = total_urls / elapsed if elapsed > 0 else 0
                logger.info(f"Crawling rate: {rate:.2f} URLs/second after {elapsed:.2f} seconds")
                last_log_time = current_time

            for link in links:
                if link not in visited:
                    logger.debug(f"Enqueuing URL: {link} at depth {current_depth - 1}")
                    queue.append((link, current_depth - 1))

    end_time = time.time()
    total_time = end_time - start_time
    overall_rate = total_urls / total_time if total_time > 0 else 0
    logger.info(f"Finished BFS crawl. Total URLs processed: {total_urls}. Total time taken: {total_time:.2f} seconds. Overall rate: {overall_rate:.2f} URLs/second")

    logger.info("BFS crawl completed.")
    return site_structure

def crawl_dfs(url, depth, domain, visited=None, site_structure=None, start_time=None, total_urls=None, last_log_time=None):
    if visited is None:
        visited = set()
    if site_structure is None:
        site_structure = {}
    if start_time is None:
        start_time = time.time()
    if total_urls is None:
        total_urls = [0]
    if last_log_time is None:
        last_log_time = [start_time]

    if depth == 0 or url in visited:
        return site_structure

    logger.debug(f"Crawling (DFS) at depth {depth}: {url}")
    visited.add(url)
    response = requests.get(url)
    if response.ok:
        soup = BeautifulSoup(response.text, 'html.parser')
        title = str(soup.title.string) if soup.title else "No title"
        links = list(extract_links(response.text, url, domain))
        site_structure[url] = {'title': title, 'links': links}
        total_urls[0] += len(links)

        current_time = time.time()
        if current_time - last_log_time[0] >= 5:
            elapsed = current_time - start_time
            rate = total_urls[0] / elapsed if elapsed > 0 else 0
            logger.info(f"Crawling rate: {rate:.2f} URLs/second after {elapsed:.2f} seconds")
            last_log_time[0] = current_time

        for link in links:
            if link not in visited:
                crawl_dfs(link, depth - 1, domain, visited, site_structure, start_time, total_urls, last_log_time)
    else:
        logger.warning(f"Failed to retrieve URL: {url} with status code {response.status_code}")

    return site_structure