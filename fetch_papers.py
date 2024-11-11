import requests
import json
from datetime import datetime

def fetch_papers():
    keyword = "backdoor"
    query = f"search_query=all:{keyword}"
    url = f"http://export.arxiv.org/api/query?{query}&start=0&max_results=5"
    
    response = requests.get(url)
    papers = []

    if response.status_code == 200:
        data = response.text
        # Parse XML response (use xml.etree.ElementTree or similar library)
        # Here we only illustrate appending paper info
        papers.append({
            "title": "Example Title",
            "authors": ["Author 1", "Author 2"],
            "url": "http://example.com",
            "published_date": datetime.now().isoformat(),
        })
    
    with open("papers.json", "w") as file:
        json.dump(papers, file)

fetch_papers()

