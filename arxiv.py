import requests
import random
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import time
import xml.etree.ElementTree as ET

# Get data from Arxiv API

# MongoDB URI and client setup
uri = "mongodb+srv://Unun:DqAXUqXArT6n9tev@dsdedata.hv1co.mongodb.net/?retryWrites=true&w=majority&appName=DsdeData"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['DsdeData']  # Database name
collection = db['arxivScraped']  # New collection to store scraped data

# Function to fetch data from DBLP API with retry and exponential backoff
def fetch_arxiv_data(query, max_results=10, max_retries=5):
    base_url = "https://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{query}",
        "max_results": max_results,
    }
    retry_count = 0
    delay = 1  # Initial delay in seconds

    while retry_count < max_retries:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            return ET.fromstring(response.content)
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
while len(results) < 5:
    query = random.choice(queries)
    arxiv_data = fetch_arxiv_data(query, max_results=25)
    
    if arxiv_data is not None:
        entries = arxiv_data.findall('.//entry')
        batch = []
        
        for entry in entries:
            title = entry.find('title').text if entry.find('title') is not None else None
            authors = entry.findall('author')
            author_names = [author.find('name').text for author in authors if author.find('name') is not None]
            summary = entry.find('summary').text if entry.find('summary') is not None else None
            publishing_date = entry.find('published').text if entry.find('published') is not None else None
            journal_ref = entry.find('arxiv:journal_ref', namespaces={'arxiv': 'http://arxiv.org/schemas/atom'}).text if entry.find('arxiv:journal_ref', namespaces={'arxiv': 'http://arxiv.org/schemas/atom'}) is not None else None
        # for entry in entries:
        #     title = entry.get('title', None)
        #     authors = entry.get('author', [])
        #     if not isinstance(authors, list):  # Handle single author as a list
        #         authors = [authors]
        #     author_names = [author['name'] for author in authors]
        #     summary = entry.get('summary', None)
        #     publishing_date = entry.get('published', None)
        #     journal_ref = entry.get('arxiv_journal_ref', None)
            # Prepare document to insert
            if(title and author_names and summary and publishing_date and journal_ref):
                document = {
                    "title": title,
                    "abstracts": summary,  # corrected typo
                    "authors": author_names,
                    "date": publishing_date,
                    "language": {"@xml:lang": "eng"},
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
