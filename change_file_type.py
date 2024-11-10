import os

# Path to the main folder
main_folder_path = "/Users/ktap8/Library/CloudStorage/SynologyDrive-KTAP8/second year/Data Science/project/Data"

# Loop through each subfolder in the main folder
for subfolder in os.listdir(main_folder_path):
    subfolder_path = os.path.join(main_folder_path, subfolder)

    # Check if it is a directory
    if os.path.isdir(subfolder_path):
        # Loop through each file in the subfolder
        for filename in os.listdir(subfolder_path):
            file_path = os.path.join(subfolder_path, filename)

            # Check if the file does not already have a .json extension
            if os.path.isfile(file_path) and not filename.endswith(".json"):
                new_file_path = f"{file_path}.json"
                os.rename(file_path, new_file_path)
                print(f"Renamed: {file_path} -> {new_file_path}")
