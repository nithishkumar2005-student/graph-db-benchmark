import urllib.request
import gzip
import shutil
import os

def download_dataset():
    url = "https://snap.stanford.edu/data/amazon0302.txt.gz"
    filename = "amazon_data.txt.gz"
    output = "amazon_relationships.csv"

    print("Downloading dataset (this might take a minute)...")
    urllib.request.urlretrieve(url, filename)

    print("Unzipping...")
    with gzip.open(filename, 'rb') as f_in:
        with open(output, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    print(f"Dataset saved as {output}")
    # Remove the compressed file to save space
    os.remove(filename)

if __name__ == "__main__":
    download_dataset()