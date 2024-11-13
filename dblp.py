import requests
import random
from pymongo import MongoClient
from pymongo.server_api import ServerApi


uri = "mongodb+srv://KTAP8:JhpxOn0CFlXE5mty@dsdedata.hv1co.mongodb.net/?retryWrites=true&w=majority&appName=DsdeData"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['DsdeData']  # Replace with your database name


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
        print(
            f"Failed to fetch data. HTTP Status code: {response.status_code}")
        return None


queries = [
    "Agricultural", "Bio", "Arts", "Human",
    "Business", "Management", "Account", "Chemical Engineering", "Computer", "Decision",
    "Dentist", "Earth", "Economic", "Finance", "Energy", "Engineering",
    "Environment", "Health", "Immun", "Material science", "Math",
    "Medicine", "Neuroscience", "Nursing", "Pharma", "Physic",
    "Psychology", "Social", "Veterinary", "Multidisciplinary"
]

subject_map = {
    "AGRI": ["Agricultural", "Bio"],
    "ARTS": ["Arts"],
    "BIOC": ["Human"],
    "BUSI": ["Business", "Management", "Account"],
    "CENG": ["Chemical Engineering"],
    "CHEM": ["Chem"],
    "COMP": ["Computer"],
    "DECI": ["Decision"],
    "DENT": ["Dentist"],
    "EART": ["Earth"],
    "ECON": ["Economic", "Finance"],
    "ENER": ["Energy"],
    "ENGI": ["Engineering"],
    "ENVI": ["Environment"],
    "HEAL": ["Health"],
    "IMMU": ["Immun"],
    "MATE": ["Material science"],
    "MATH": ["Math"],
    "MEDI": ["Medicine"],
    "NEUR": ["Neuroscience"],
    "NURS": ["Nursing"],
    "PHAR": ["Pharma"],
    "PHYS": ["Physic"],
    "PSYC": ["Psychology"],
    "SOCI": ["Social"],
    "VETE": ["Veterinary"],
    "MULT": ["Multidisciplinary"]
}


def map_subject(value):
    for key, values in subject_map.items():
        if value in values:
            return key
    return value


Collection = db['papers']
results = []


while len(results) < 5:
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
        year = info.get('year', 'N/A')
        document = {
            "title": title,
            "authors": author_names,
            "year": year,
            "date": None,
            "language": {"@xml:lang": "eng"},
            "authkeywords": {"author-keyword": venue},
            "subject_areas": {"subject-area": map_subject(query)},
        }
        results.append(document)
        Collection.insert_one(document)
        print('inserting: '+title)


print("Data insertion complete!")
