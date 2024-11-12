import requests
import random

def fetch_dblp_data(query, max_results=1):
    base_url = "https://dblp.org/search/publ/api"
    params = {
        "q": query,
        "h": max_results,
        "format": "json"
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Failed to fetch data. HTTP Status code: {response.status_code}")
        return None

queries = [
    "Agricultural","Bio", "Arts","Human",
    "Business, Management","Account", "Chem", "Computer", "Decision",
    "Dentist", "Earth", "Economic","Finance", "Energy", "Engineering",
    "Environment", "Health", "Immun", "Material", "Math", "Science",
    "Medicine", "Neuroscience", "Nursing", "Pharma", "Physic",
    "Psychology", "Social", "Veterinary", "Multidisciplinary"
]

results = []


while len(results) < 10:
    query = random.choice(queries)
    dblp_data = fetch_dblp_data(query)
    if dblp_data and 'result' in dblp_data and 'hits' in dblp_data['result'] and 'hit' in dblp_data['result']['hits']:
        hit = dblp_data['result']['hits']['hit'][0]
        info = hit['info']
        title = info.get('title', 'N/A')
        authors = info.get('authors', {}).get('author', [])
        if isinstance(authors, list):
            author_names = [author['text'] for author in authors]
        else:
            author_names = [authors['text']]
        venue = info.get('venue', 'N/A')
        date = info.get('year', 'N/A')
        results.append({
            "title": title,
            "authors": author_names,
            "year": date,
            "date": None,
            "language": "eng",
            "authkeywords": venue,
            "subject_areas": query,
            
        })

print(results)