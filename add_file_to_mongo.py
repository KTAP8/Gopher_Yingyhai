import os
import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi


uri = "mongodb+srv://<username>:<password>@dsdedata.hv1co.mongodb.net/?retryWrites=true&w=majority&appName=DsdeData"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['DsdeData']  # Replace with your database name

# # Drop the database
# client.drop_database('DsdeData')

# print("All data has been deleted from the database!")


# Define the base path of the folders
# Replace with the actual path to your folders (2018-2023)
base_path = "/Users/ktap8/Library/CloudStorage/SynologyDrive-KTAP8/second year/Data Science/project/Data"

# Iterate over each year's folder (2018 to 2023)
for year in range(2018, 2024):
    year_folder = os.path.join(base_path, str(year))
    collection = db[str(year)]  # Use a separate collection for each year

    # Iterate over each JSON file in the year folder
    for filename in os.listdir(year_folder):
        if filename.endswith(".json"):
            file_path = os.path.join(year_folder, filename)

            # Open and parse the JSON file
            with open(file_path, 'r') as file:
                data = json.load(file)

                # Extract specific keys
                abstract_response = data.get(
                    'abstracts-retrieval-response', {})
                coredata = abstract_response.get('coredata')
                language = abstract_response.get('language')
                subject_areas = abstract_response.get(
                    'subject-areas', {}).get('subject-area', {})

                # Prepare document with selected fields
                document = {
                    "coredata": coredata,
                    "language": language,
                    "subject_areas": subject_areas
                }

                # Insert the document if coredata exists
                if coredata:
                    collection.insert_one(document)

print("Data insertion complete!")
