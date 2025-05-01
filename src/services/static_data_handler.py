"""
Extracts static data from the National Rail API and stores it in the src/data/fares directory.
"""

import token_generator
import requests
import zipfile
import io
import os

FARES_URL = "https://opendata.nationalrail.co.uk/api/staticfeeds/2.0/fares"
FARES_STORE = "src/data/fares/"

ROUTING_URL = "https://opendata.nationalrail.co.uk/api/staticfeeds/2.0/routeing"
ROUTING_STORE = "src/data/routeing/"

def get_data(url):
    # Get authentication token
    token = token_generator.get_auth_token()
    headers = {"X-Auth-Token": token}
    
    try:
        # Send GET request to get fares data
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise error for bad responses (4xx, 5xx)
        return response
    
    except requests.exceptions.RequestException as e:
        return None

def extract_response_contents(response, destination):
    if response.headers.get("Content-Type") == "application/zip":
        zip_bytes = io.BytesIO(response.content)

        os.makedirs(destination, exist_ok=True)
        
        with zipfile.ZipFile(zip_bytes) as zip_ref:
            zip_ref.extractall(destination)

if __name__ == "__main__":
    data = get_data(FARES_URL)

    if data is not None:
        extract_response_contents(data, FARES_STORE)
        print(f"Fares data extracted to {FARES_STORE}")

    data = get_data(ROUTING_URL)
    if data is not None:
        extract_response_contents(data, ROUTING_STORE)
        print(f"Routing data extracted to {ROUTING_STORE}")