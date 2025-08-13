import os
import requests
from tqdm import tqdm

# --- Configuration ---
# Directory to save the data
output_dir = "data/raw"

# URLs for the SPARC data files
urls = {
    "SPARC_Lelli2016c.mrt.txt": "http://astroweb.cwru.edu/SPARC/data/Lelli2016c/SPARC_Lelli2016c.mrt.txt",
    "MassModels_Lelli2016c.mrt.txt": "http://astroweb.cwru.edu/SPARC/data/Lelli2016c/MassModels/MassModels_Lelli2016c.mrt.txt",
}

# --- Main Download Function ---
def download_file(url, filepath):
    """Downloads a file with a progress bar."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes
        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte

        with open(filepath, 'wb') as file, tqdm(
            desc=os.path.basename(filepath),
            total=total_size_in_bytes,
            unit='iB',
            unit_scale=True,
        ) as bar:
            for data in response.iter_content(block_size):
                bar.update(len(data))
                file.write(data)

        if total_size_in_bytes != 0 and bar.n != total_size_in_bytes:
            print("ERROR, something went wrong")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        # Clean up partial file if download failed
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == "__main__":
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    print(f"Data will be saved to '{output_dir}/'")

    # Download each file
    for filename, url in urls.items():
        filepath = os.path.join(output_dir, filename)
        if not os.path.exists(filepath):
            print(f"Downloading {filename}...")
            download_file(url, filepath)
        else:
            print(f"'{filename}' already exists. Skipping.")

    print("\nData download process finished.")
