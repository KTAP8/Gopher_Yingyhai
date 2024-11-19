import requests
import random
import time
import xmltodict  # For converting XML to JSON
import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import re

# MongoDB URI and client setup
uri = "mongodb+srv://KTAP8:JhpxOn0CFlXE5mty@dsdedata.hv1co.mongodb.net/?retryWrites=true&w=majority&appName=DsdeData"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['DsdeData']  # Database name
collection = db['arxivScraped']  # New collection to store scraped data

# Function to fetch and parse data as JSON


def fetch_arxiv_data_as_json(query, max_results=10, max_retries=5):
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
            # Convert XML to JSON
            data_dict = xmltodict.parse(response.content)
            # Convert dict to JSON-compatible format
            return json.loads(json.dumps(data_dict))
        elif response.status_code == 429:
            print("Rate limit hit. Retrying...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff
            retry_count += 1
        else:
            print(
                f"Failed to fetch data. HTTP Status code: {response.status_code}")
            return None
    print("Max retries exceeded.")
    return None


# Example usage
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


def drop_arxiv():
    db['arxivScraped'].drop()

    print("The 'arxivScraped' collection has been dropped.")


# in the journal ref --> pattern for the year of the ref is different, we gotta extract the year and the text this way
def extract_year_and_text(text):
    if (text == None):
        return [None, None]
    # Regular expression to find a year between 1800 and 2024
    year_pattern = r'\b(14[0-9]{2}|15[0-9]{2}|16[0-9]{2}|17[0-9]{2}|18[0-9]{2}|19[0-9]{2}|20[0-2][0-4])\b'

    # Search for the year in the text
    match = re.search(year_pattern, text)

    if match:
        year = match.group(0)  # Extract the matched year
        # Remove the year from the text
        remaining_text = text.replace(year, '').strip()
        return [year, remaining_text]
    else:
        return ["Unknown", text]  # No year found, return the original text


drop_arxiv()

results = []
while len(results) < 1000:
    query = random.choice(queries)
    arxiv_data = fetch_arxiv_data_as_json(query, max_results=25)
    if arxiv_data is not None:
        batch = []
        for entry in arxiv_data['feed']['entry']:
            if ('title' in entry) and ('author' in entry) and ('summary' in entry) and ('published' in entry) and ('arxiv:journal_ref' in entry):
                title = entry['title']
                authors = entry['author']
                if (type(authors) == list):
                    author_names = [author['name'] for author in authors]
                else:
                    author_names = [authors['name']]
                summary = entry['summary']
                publishing_date = (str(entry['published']).split('T'))[0]
                if '#text' in entry['arxiv:journal_ref']:
                    journal_ref = entry['arxiv:journal_ref']['#text']
                else:
                    journal_ref = None

                ref_year, ref_text = extract_year_and_text(journal_ref)
                if ((ref_year == None) and (ref_text == None)):
                    ref = None
                else:
                    ref = {ref_year: ref_text}

                coredata = {"title": title}

                document = {
                    "reference": ref,
                    "abstracts": summary,  # corrected typo
                    "correspondences": None,
                    "affiliation": None,
                    "publishedDate": publishing_date,
                    "coredata": coredata,
                    "language": "eng",
                    "authorKeywords": None,
                    "subjectArea": {map_subject(query): list()},
                    "authors": author_names
                }
                print(f'inserting: {title}')
                batch.append(document)
            else:
                pass
        # Insert batch into collection
        if batch:
            collection.insert_many(batch)
            results.extend(batch)
            print(f'Inserted batch of {len(batch)} documents.')

    # Delay between requests to prevent rate limits
    time.sleep(2)  # Increase delay slightly if rate limit is still an issue

print("Data insertion complete!")
print(len(results))
