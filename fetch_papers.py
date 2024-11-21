import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
# from sentence_transformers import SentenceTransformer, util


# def check_topic_nlp(title):
#     # Return attack, defense, both, or None
#     model = SentenceTransformer('all-MiniLM-L6-v2')

#     backdoor_topic = "Research on backdoor attacks in machine learning"
#     backdoor_topic_defense = "Research on backdoor attacks in machine learning"

#     paper_embedding = model.encode(title, convert_to_tensor=True)
#     topic_embedding = model.encode(backdoor_topic, convert_to_tensor=True)
#     topic_embedding_defense = model.encode(backdoor_topic_defense, convert_to_tensor=True)

#     # Compute cosine similarity
#     cosine_sim = util.cos_sim(paper_embedding, topic_embedding)
#     cosine_sim_defense = util.cos_sim(paper_embedding, topic_embedding_defense)

#     if cosine_sim > 0.5 and cosine_sim_defense > 0.5:
#         return "both"
#     elif cosine_sim > 0.5:
#         return "attack"
#     elif cosine_sim_defense > 0.5:
#         return "defense"
#     else:
#         return None

def check_topic(title):
    attack_keywords = ["backdoor attack", "trojan attack", "poisoning attack", "trigger-based attack", "data poisoning", "backdoor attacks"]
    defense_keywords = ["backdoor defense", "trigger detection", "poison detection", "model sanitization", "robustness against backdoors", "backdoor defenses"]

    is_attack = any(keyword in title.lower() for keyword in attack_keywords)
    is_defense = any(keyword in title.lower() for keyword in defense_keywords)

    if is_attack and is_defense:
        return "both"
    elif is_attack:
        return "attack"
    elif is_defense:
        return "defense"
    else:
        return None

def crawl_conf(conf="", year=2020, papers_info=None):
    url = f"https://dblp.org/db/conf/{conf}/{conf}{year}.html"

    response = requests.get(url)
 
    if response.status_code == 200:
        data = response.text
        soup = BeautifulSoup(data, 'html.parser')
        # class data tts-content contains the authors and title of the paper
        blocks = soup.find_all("cite", class_="data tts-content", itemprop="headline")
    
    
        for block in blocks:
            # itemprop="author" contains the author of the paper, there are more than one in each block

            authors = block.find_all("span", itemprop="author")
            # for the title class="title" and  itemprop="name"
            title = block.find("span", class_="title", itemprop="name")

            # See if the word "backdoor" is in the title
            backdoor = check_topic(title.text)

            if backdoor is not None:
                # Check if authors is empty
                if len(authors) > 0:
                    data = {
                        "title": title.text,
                        "authors": [author.text for author in authors],
                        "year": year,
                        "proceedings": conf,
                        "type": backdoor
                    }
                    
                    papers_info = pd.concat([papers_info, pd.DataFrame([data])], ignore_index=True)
            else:
                # Paper is not a backdoor paper
                continue
            
    return papers_info


#fetch_papers()
def main():
    years = range(2017, datetime.now().year + 1)
    # uss = Usenix
    confs = ["ndss", "uss", "ccs", "sp"]

    papers_info = pd.DataFrame(columns=['title', 'authors', 'year', 'proceedings', 'type'])

    # Create a data structure to store the papers and authors and year and conference

    for conf in confs:
        for year in years:
            print(f"Crawling {conf} {year}")
            papers_info = crawl_conf(conf, year, papers_info)

    # Save the pandas
    csv = papers_info.to_csv("public/papers.csv", index=False)
    papers_list = papers_info.to_dict(orient="records")

    #  Save as a proper JSON file
    with open("public/papers.json", "w") as json_file:
        json.dump(papers_list, json_file, indent=4)

if __name__ == "__main__":
    main()