import os
import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd


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
# add_mongo()

def update_author(collection, new_field_name):
    for document in collection.find():
        # Get the value from the document or DataFrame
        values = document.get(new_field_name)
        if not values:
            continue  # Skip if the new_field_name is not in the document

        new_value = {}
        i = 0
        for value in values:
            temp = {"name": value, "afid": None}
            new_value[str(i)] = temp  # Convert the key to a string
            i += 1

        # Update the document in MongoDB
        collection.update_one(
            {"_id": document["_id"]},  # Match by document ID
            # Update the field with new_value
            {"$set": {"author": new_value}}
        )


arxiv = db['arxivScraped']
arxiv2 = db['arxivScrapedCopy']
papers = db['papers']
# update_author(arxiv, "authors")

# arxiv.update_many({}, {"$unset": {"authors": ""}})


def update_ref(collection, new_field_name, original):
    for document in original.find():
        # Get the value from the document or DataFrame
        values = document.get(new_field_name)
        if not values:
            continue  # Skip if the new_field_name is not in the document
        temp = {}
        ref_count = len(values.keys())
        for k, v in values.items():
            inside = [v]
            temp[k] = inside  # Convert the key to a string
        new_value = {"ref_count": ref_count, "ref_publishYear_titleText": temp}

        # Update the document in MongoDB
        collection.update_one(
            {"_id": document["_id"]},  # Match by document ID
            # Update the field with new_value
            {"$set": {"reference": new_value}}
        )
        print("setting " + str(document['_id']))


#update_ref(arxiv, "reference", arxiv2)

def drop_column(collection, column):
    collection.update_many({}, {"$unset": {column: ""}})
    print(f"Column '{column}' has been dropped from the database!")

#drop_column(arxiv2, 'Predictions_area')
#drop_column(arxiv, 'Predictions_area')
#drop_column(papers, 'Predictions_area')