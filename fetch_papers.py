import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import os
import sys
import re
from colorama import Fore, Style, init
from scholarly import scholarly

# Initialize colorama for cross-platform support
init(autoreset=True)

# Keywords for identifying relevant papers
ATTACK_KEYWORDS = [
    "backdoor attack", "trojan attack", "poisoning attack",
    "trigger-based attack", "data poisoning", "backdoor attacks"
]

DEFENSE_KEYWORDS = [
    "backdoor defense", "trigger detection", "poison detection",
    "model sanitization", "robustness against backdoors", "backdoor defenses"
]

def preprocess_string(string):
    """
    Removes special characters and converts the string to lowercase.
    """
    return re.sub(r'[^a-zA-Z0-9\s]', '', string).lower()

def check_topic(title):
    """
    Determines if a paper's title relates to attack, defense, or both based on predefined keywords.
    """
    title_lower = preprocess_string(title)
    is_attack = any(keyword in title_lower for keyword in ATTACK_KEYWORDS)
    is_defense = any(keyword in title_lower for keyword in DEFENSE_KEYWORDS)

    if is_attack and is_defense:
        return "both"
    elif is_attack:
        return "attack"
    elif is_defense:
        return "defense"
    return None

def cleanup_missing_files(conferences):
    """
    Removes existing missing.txt files for all conferences.
    """
    for conf in conferences:
        missing_file = f"public/missing_{conf}.txt"
        if os.path.exists(missing_file):
            print(f"{Fore.YELLOW}[!] Removing existing {missing_file}")
            os.remove(missing_file)

def fetch_conference_papers(conf, name, year):
    """
    Fetches papers from a specified conference and year from DBLP.
    """
    url = f"https://dblp.org/db/conf/{conf}/{conf}{year}.html"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"{Fore.RED}[✘] Error fetching {name} {year}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    blocks = soup.find_all("cite", class_="data tts-content", itemprop="headline")
    
    papers = []
    for block in blocks:
        title_elem = block.find("span", class_="title", itemprop="name")
        if not title_elem:
            continue

        title = title_elem.text.strip()
        topic_type = check_topic(title)
        if not topic_type:
            continue

        authors = [author.text for author in block.find_all("span", itemprop="author")]
        papers.append({
            "title": title,
            "authors": authors,
            "year": year,
            "proceedings": name,
            "type": topic_type
        })
    return papers

def save_to_file(data, filepath, as_json=True):
    """
    Saves data to a file in JSON or CSV format.
    """
    try:
        if as_json:
            with open(filepath, "w") as f:
                json.dump(data, f, indent=4)
        else:
            pd.DataFrame(data).to_csv(filepath, index=False)
        print(f"{Fore.GREEN}[✔] Data saved to {filepath}")
    except Exception as e:
        print(f"{Fore.RED}[✘] Error saving to file {filepath}: {e}")

def fetch_arxiv_pdf(title):
    """
    Searches for a paper on arXiv and returns the PDF link if found.
    """
    url = "http://export.arxiv.org/api/query"
    params = {'search_query': title, 'start': 0, 'max_results': 1}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "xml")
        arxiv_title = soup.find_all("title")[1].text
        if preprocess_string(arxiv_title) == preprocess_string(title):
            return soup.find("link", title="pdf").get("href")
    return None

def fetch_semantic_scholar_pdf(title):
    """
    Searches for a paper on Semantic Scholar and returns the PDF link if found.
    """
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {'query': title, 'fields': 'openAccessPdf'}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["data"]:
            pdf_url = data["data"][0].get("openAccessPdf")
            if pdf_url is not None:
                pdf_url = pdf_url['url']
            return pdf_url
    return None

def fetch_google_scholar_pdf(title):
    """
    Searches for a paper on Google Scholar and returns the PDF link if found.
    """
    try:
        search_query = scholarly.search_pubs(title)
        paper = next(search_query)
        pdf_url = paper.get("eprint_url", None)
        return pdf_url
    except StopIteration:
        print(f"{Fore.YELLOW}[!] No Google Scholar result for: {title}")
        return None
    except Exception as e:
        print(f"{Fore.RED}[✘] Error searching Google Scholar: {e}")
        return None

def download_paper(title, proceedings, link):
    """
    Downloads a paper from the provided link.
    """
    conf_folder = f"public/papers/{proceedings}"
    os.makedirs(conf_folder, exist_ok=True)
    try:
        response = requests.get(link, timeout=10)
        with open(f"{conf_folder}/{title}.pdf", "wb") as f:
            f.write(response.content)
        print(f"{Fore.GREEN}[✔] Downloaded: {title}")
    except Exception as e:
        print(f"{Fore.RED}[✘] Failed to download {title}: {e}")

def download_papers(papers_info):
    """
    Downloads papers from arXiv or Semantic Scholar based on metadata.
    Creates a missing.txt file for each conference if papers cannot be found.
    """
    os.makedirs("public/papers", exist_ok=True)


    for paper in papers_info:
        title = paper["title"]
        proceedings = paper["proceedings"]
        missing_file = f"public/missing_{proceedings}.txt"

        link = fetch_arxiv_pdf(title)
        if not link:
            link = fetch_semantic_scholar_pdf(title)
        if not link:
            link = fetch_google_scholar_pdf(title)

        if link:
            download_paper(title, proceedings, link)
        else:
            print(f"{Fore.RED}[✘] Could not find a PDF for: {title}")
            with open(missing_file, "a") as f:
                f.write(f"{title}\n")

def fetch_papers(conferences, conference_names, years):
    """
    Fetches paper metadata for given conferences and years.
    """
    papers_info = []
    for conf, name in zip(conferences, conference_names):
        print(f"{Fore.BLUE}Crawling {name} {years}...")
        for year in years:
            papers = fetch_conference_papers(conf, name, year)
            papers_info.extend(papers)
    return papers_info

def main():
    """
    Main function for fetching or downloading papers.
    """
    if len(sys.argv) != 2 or sys.argv[1] not in ['fetch', 'download']:
        print(f"{Fore.RED}Usage: python script.py [fetch|download]")
        sys.exit(1)

    years = range(2017, datetime.now().year + 1)
    confs = ["ndss", "uss", "ccs", "sp", "cvpr", "nips", "iclr", "icml", "aaai"]
    conf_names = ["NDSS", "Usenix", "CCS", "S&P", "CVPR", "NeurIPS", "ICLR", "ICML", "AAAI"]
    mode = sys.argv[1]
    papers_file = "public/papers.json"

    # Cleanup old missing files
    cleanup_missing_files(conf_names)

    if mode == 'fetch':
        papers_info = fetch_papers(confs, conf_names, years)
        os.makedirs("public", exist_ok=True)
        save_to_file(papers_info, papers_file)
    elif mode == 'download':
        if not os.path.exists(papers_file):
            print(f"{Fore.RED}[✘] No papers data found at {papers_file}. Run 'fetch' first.")
            sys.exit(1)
        with open(papers_file, "r") as f:
            papers_info = json.load(f)
        download_papers(papers_info)

if __name__ == "__main__":
    main()
