import requests
import random
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import time

# MongoDB URI and client setup
uri = "mongodb+srv://KTAP8:JhpxOn0CFlXE5mty@dsdedata.hv1co.mongodb.net/?retryWrites=true&w=majority&appName=DsdeData"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['DsdeData']  # Database name
collection = db['scraped']  # New collection to store scraped data

# Function to fetch data from DBLP API with retry and exponential backoff
def fetch_dblp_data(query, max_results=10, max_retries=5):
    base_url = "https://dblp.org/search/publ/api"
    params = {
        "q": query,
        "h": max_results,
        "format": "json"
    }
    retry_count = 0
    delay = 1  # Initial delay in seconds

    while retry_count < max_retries:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print("Rate limit hit. Retrying...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff
            retry_count += 1
        else:
            print(f"Failed to fetch data. HTTP Status code: {response.status_code}")
            return None
    print("Max retries exceeded.")
    return None

# Query terms and subject mapping
queries = [
    "Agricultural", "Bio", "Arts", "Human", "Business", "Management", "Account",
    "Chemical Engineering", "Computer", "Decision", "Dentist", "Earth", "Economic",
    "Finance", "Energy", "Engineering", "Environment", "Health", "Immun",
    "Material science", "Math", "Medicine", "Neuroscience", "Nursing", "Pharma",
    "Physic", "Psychology", "Social", "Veterinary", "Multidisciplinary"
]

subject_map = {
    "AGRI": ["Agricultural", "Bio"], "ARTS": ["Arts"], "BIOC": ["Human"],
    "BUSI": ["Business", "Management", "Account"], "CENG": ["Chemical Engineering"],
    "CHEM": ["Chem"], "COMP": ["Computer"], "DECI": ["Decision"], "DENT": ["Dentist"],
    "EART": ["Earth"], "ECON": ["Economic", "Finance"], "ENER": ["Energy"],
    "ENGI": ["Engineering"], "ENVI": ["Environment"], "HEAL": ["Health"],
    "IMMU": ["Immun"], "MATE": ["Material science"], "MATH": ["Math"],
    "MEDI": ["Medicine"], "NEUR": ["Neuroscience"], "NURS": ["Nursing"],
    "PHAR": ["Pharma"], "PHYS": ["Physic"], "PSYC": ["Psychology"],
    "SOCI": ["Social"], "VETE": ["Veterinary"], "MULT": ["Multidisciplinary"]
}

def map_subject(value):
    for key, values in subject_map.items():
        if value in values:
            return key
    return value

def drop_scrape():
    db['scraped'].drop()

    print("The 'scraped' collection has been dropped.")


# Fetch and insert data in batches
results = []
while len(results) < 1000:
    query = random.choice(queries)
    dblp_data = fetch_dblp_data(query, max_results=25)
    
    if dblp_data and 'result' in dblp_data and 'hits' in dblp_data['result'] and 'hit' in dblp_data['result']['hits']:
        hits = dblp_data['result']['hits']['hit']
        batch = []
        
        for hit in hits:
            info = hit['info']
            title = info.get('title', None)
            authors = info.get('authors', {}).get('author', [])
            if isinstance(authors, list):
                author_names = [author['text'] for author in authors]
            else:
                author_names = [authors['text']]
            
            venue = info.get('venue', None)
            year = info.get('year', None)
            
            # Prepare document to insert
            if(title and venue and year):
                document = {
                    "title": title,
                    "authors": author_names,
                    "year": year,
                    "date": None,
                    "language": {"@xml:lang": "eng"},
                    "authkeywords": {"author-keyword": venue},
                    "subject_areas": {"subject-area": map_subject(query)}
                }
                batch.append(document)
        
        # Insert batch into collection
        if batch:
            collection.insert_many(batch)
            results.extend(batch)
            print(f'Inserted batch of {len(batch)} documents.')
    
    # Delay between requests to prevent rate limits
    time.sleep(2)  # Increase delay slightly if rate limit is still an issue

print("Data insertion complete!")
#print(results)
print(len(results))
