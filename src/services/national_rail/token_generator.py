import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Endpoint for authentication
AUTH_URL = "https://opendata.nationalrail.co.uk/authenticate"

# Your API credentials
USERNAME = os.getenv("NATIONAL_RAIL_USERNAME")
PASSWORD = os.getenv("NATIONAL_RAIL_PASSWORD")

def get_auth_token():
    """
    Authenticate with the National Rail API and get an access token.
    """
    # URL-encoded form data
    payload = {
        "username": USERNAME,
        "password": PASSWORD
    }

    # Headers to specify URL-encoded form data
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        # Send POST request to authenticate
        response = requests.post(AUTH_URL, data=payload, headers=headers)
        response.raise_for_status()  # Raise error for bad responses (4xx, 5xx)

        # Extract and return token
        token = response.text  # Token is returned as plain text
        return json.loads(token)["token"]  # Parse JSON and extract token

    except requests.exceptions.RequestException as e:
        return None