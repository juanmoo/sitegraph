from urllib.parse import urlparse, urlunparse

def normalize_url(url, base_url):
    parsed = urlparse(url)
    normalized = parsed._replace(fragment='')
    return urlunparse(normalized)

def valid_link(link, domain):
    parsed_link = urlparse(link)
    return domain in parsed_link.netloc and '/blog/' in parsed_link.path

def save_json(data, filename):
    import json
    with open(filename,'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def generate_graphml(site_structure, filename):
    import networkx as nx
    G = nx.DiGraph()
    for page, data in site_structure.items():
        G.add_node(page, label=page, title=data['title'])
        for link in data['links']:
            G.add_edge(page, link)
    nx.write_graphml(G, filename)