from crawler import crawl_dfs, crawl_bfs
from utils import save_json, generate_graphml
import os

def main():
    start_url = "https://www.joingivers.com/"
    max_depth = 10
    domain = "joingivers.com"
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
    # site_structure = crawl(start_url, max_depth, domain)  # For DFS
    site_structure = crawl_bfs(start_url, max_depth, domain)  # For BFS
    
    # Save the site structure to a JSON file
    save_json(site_structure, os.path.join(output_directory, "site_structure.json"))
    
    # Generate a GraphML file for visualization
    generate_graphml(site_structure, os.path.join(output_directory, "site_structure.graphml"))

if __name__ == "__main__":
    main()
