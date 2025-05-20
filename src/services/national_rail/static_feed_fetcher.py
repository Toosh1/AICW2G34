"""
Extracts static data from the National Rail API and stores it in the src/data/fares directory.
"""

import requests
import zipfile
import io
import os

FARES_URL = "https://opendata.nationalrail.co.uk/api/staticfeeds/2.0/fares"
FARES_STORE = "src/data/static_feeds/fares/"

ROUTING_URL = "https://opendata.nationalrail.co.uk/api/staticfeeds/2.0/routeing"
ROUTING_STORE = "src/data/static_feeds/routeing/"

STATIONS_URL = "https://opendata.nationalrail.co.uk/api/staticfeeds/4.0/stations"
STATIONS_STORE = "src/data/static_feeds/stations/"

# Ensure directories exist
os.makedirs(FARES_STORE, exist_ok=True)
os.makedirs(ROUTING_STORE, exist_ok=True)
os.makedirs(STATIONS_STORE, exist_ok=True)

def get_data(url, token = None):
    # Get authentication token, if not provided
    if token is None:
        import token_generator
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

def extract_data(url: str, store: str, token: str) -> None:
    """
    Extracts data from the given URL and stores it in the specified directory.
    
    Args:
        url (str): The URL to fetch data from.
        store (str): The directory to store the extracted data.
    """
    response = get_data(url, token)
    if response is not None:
        extract_response_contents(response, store)
        print(f"+ Data extracted to {store}")
    else:
        print(f"* Failed to fetch data from {url}")

def extract_all_data(token=None) -> None:
    """
    Extracts all static data from the National Rail API and stores it in the specified directories.
    """
    extract_data(FARES_URL, FARES_STORE, token)
    extract_data(ROUTING_URL, ROUTING_STORE, token)
    extract_data(STATIONS_URL, STATIONS_STORE, token)