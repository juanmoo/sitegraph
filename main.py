from crawler import crawl_dfs, crawl_bfs
from utils import save_json, generate_graphml
import os
import logging

def main():
    # Set up logging
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

    start_url = "https://www.abbycare.org/"
    max_depth = 2
    domain = "abbycare.org"
    output_directory = f"{domain}_depth={max_depth}"

    # Ensure the output directory exists and delete previous content if re-running
    if os.path.exists(output_directory):
        for filename in os.listdir(output_directory):
            file_path = os.path.join(output_directory, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
    else:
        os.makedirs(output_directory, exist_ok=True)
    
    # Choose either DFS or BFS crawling
    # site_structure = crawl_dfs(start_url, max_depth, domain)  # For DFS
    site_structure = crawl_bfs(start_url, max_depth, domain)  # For BFS
    
    # Save the site structure to a JSON file
    save_json(site_structure, os.path.join(output_directory, "site_structure.json"))
    
    # Generate a GraphML file for visualization
    generate_graphml(site_structure, os.path.join(output_directory, "site_structure.graphml"))

if __name__ == "__main__":
    main()
