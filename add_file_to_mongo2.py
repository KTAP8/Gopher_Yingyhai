import os
import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi


uri = "mongodb+srv://KTAP8:JhpxOn0CFlXE5mty@dsdedata.hv1co.mongodb.net/?retryWrites=true&w=majority&appName=DsdeData"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['DsdeData']  # Replace with your database name


def drop_database():
    # Drop the database
    client.drop_database('DsdeData')

    print("All data has been deleted from the database!")


# Define the base path of the folders
# Replace with the actual path to your folders (2018-2023)
base_path = "/Users/ktap8/Library/CloudStorage/SynologyDrive-KTAP8/second year/Data Science/project/Data"


def add_mongo():
    # Iterate over each year's folder (2018 to 2023)
    for year in range(2018, 2024):
        year_folder = os.path.join(base_path, str(year))
        Collection = db['papers']
        authors_map = db['authors']
        # Iterate over each JSON file in the year folder
        for filename in os.listdir(year_folder):
            if filename.endswith(".json"):
                file_path = os.path.join(year_folder, filename)

                # Open and parse the JSON file
                with open(file_path, 'r') as file:
                    data = json.load(file)

                    # Extract specific keys
                    abstract_response = data['abstracts-retrieval-response']
                    coredata = abstract_response['coredata']
                    authors = abstract_response['authors']['author']
                    au_ids = []
                    for author in authors:
                        au_id = author['@auid']
                        first_name = author['preferred-name']["ce:given-name"]
                        last_name = author['preferred-name']["ce:surname"]
                        if ((type(first_name) == str) and (type(last_name) == str)):
                            full_name = first_name + ' ' + last_name
                            author_map = {"au_id": au_id,
                                          "full_name": full_name}
                            authors_map.insert_one(author_map)
                            au_ids.append(au_id)
                    date = coredata["prism:coverDate"]
                    language = abstract_response['language']
                    auth_key = abstract_response['authkeywords']
                    subject_areas = abstract_response['subject-areas']

                    if 'dc:title' in coredata.keys():
                        title = coredata['dc:title']
                    else:
                        title = None

                    # Prepare document with selected fields
                    document = {
                        "title": title,
                        "authors": au_ids,
                        "year": str(year),
                        "date": date,
                        "language": language,
                        "authkeywords": auth_key,
                        "subject_areas": subject_areas
                    }

                    # Insert the document if title exists
                    if title:
                        Collection.insert_one(document)
                        print('inserting: '+title)

    print("Data insertion complete!")


# drop_database()
add_mongo()
