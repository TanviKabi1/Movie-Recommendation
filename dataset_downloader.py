import os
import requests
import zipfile
from io import BytesIO

DATA_URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
DATA_DIR = "data"

def download_and_extract():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    csv_path = os.path.join(DATA_DIR, "ml-latest-small", "ratings.csv")
    if os.path.exists(csv_path):
        print("Dataset already exists.")
        return

    print(f"Downloading dataset from {DATA_URL}...")
    response = requests.get(DATA_URL)
    response.raise_for_status()

    print("Extracting dataset...")
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        z.extractall(DATA_DIR)
    
    print("Download and extraction complete.")

if __name__ == "__main__":
    download_and_extract()
