"""
Extracts static data from the National Rail API and stores it in the src/data/fares directory.
"""

import services.national_rail.token_generator as token_generator
import requests
import zipfile
import io
import os

FARES_URL = "https://opendata.nationalrail.co.uk/api/staticfeeds/2.0/fares"
FARES_STORE = "src/data/fares/"

ROUTING_URL = "https://opendata.nationalrail.co.uk/api/staticfeeds/2.0/routeing"
ROUTING_STORE = "src/data/routeing/"

# Ensure directories exist
os.makedirs(FARES_STORE, exist_ok=True)
os.makedirs(ROUTING_STORE, exist_ok=True)

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
    print(f"Response Content-Type: {response.headers.get('Content-Type')}")
    if response.headers.get("Content-Type") == "application/zip":
        zip_bytes = io.BytesIO(response.content)
        os.makedirs(destination, exist_ok=True)
        with zipfile.ZipFile(zip_bytes) as zip_ref:
            zip_ref.extractall(destination)
    
    if response.headers.get("Content-Type") == "application/xml;charset=UTF-8":
        filename = os.path.join(destination, "tocs.xml")
        with open(filename, "wb") as f:
            f.write(response.content)

if __name__ == "__main__":
    data = get_data(FARES_URL)

    if data is not None:
        extract_response_contents(data, FARES_STORE)
        print(f"Fares data extracted to {FARES_STORE}")

    data = get_data(ROUTING_URL)
    if data is not None:
        extract_response_contents(data, ROUTING_STORE)
        print(f"Routing data extracted to {ROUTING_STORE}")
        
    data = get_data(TOC_URL)
    if data is not None:
        extract_response_contents(data, TOC_STORE)
        print(f"TOC data extracted to {TOC_STORE}")
    else:
        print("Failed to retrieve TOC data.")