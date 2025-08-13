import os
import requests
from tqdm import tqdm

# Directory to save the data
output_dir = "data/raw"

# URLs for the SPARC data files
urls = {
    "SPARC_Lelli2016c.mrt.txt": "http://astroweb.cwru.edu/SPARC/data/Lelli2016c/SPARC_Lelli2016c.mrt.txt",
    "MassModels_Lelli2016c.mrt.txt": "http://astroweb.cwru.edu/SPARC/data/Lelli2016c/MassModels/MassModels_Lelli2016c.mrt.txt",
}

def download_file(url, filepath):
    """Downloads a file with a progress bar."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        with open(filepath, 'wb') as file, tqdm(
            desc=os.path.basename(filepath),
            total=total_size,
            unit='iB',
            unit_scale=True,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                bar.update(len(data))
                file.write(data)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == "__main__":
    os.makedirs(output_dir, exist_ok=True)
    for filename, url in urls.items():
        filepath = os.path.join(output_dir, filename)
        if not os.path.exists(filepath):
            print(f"Downloading {filename}...")
            download_file(url, filepath)
        else:
            print(f"'{filename}' already exists. Skipping.")
    print("\nData download process finished.")
