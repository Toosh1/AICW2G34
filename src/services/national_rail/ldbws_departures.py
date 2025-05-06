import os
from zeep import Client
from dotenv import load_dotenv

def setup_client():
    load_dotenv()
    API_KEY = os.getenv("OPENLDBWS_API_KEY")
    WSDL_URL = "https://realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx?ver=2021-11-01"
    client = Client(wsdl=WSDL_URL)
    header = {'AccessToken': {'TokenValue': API_KEY}}
    client.set_default_soapheaders(header)
    return client

def get_direct_depature_board(client, from_station, to_station):
    try:
        # Get departure board info
        response = client.service.GetDepBoardWithDetails(
            numRows=10,
            crs=from_station,
            filterCrs=to_station,
            filterType="to",
        )
        return response
    
    except Exception as e:
        return None

def get_departure_board(client, from_station):
    try:
        response = client.service.GetDepBoardWithDetails(numRows=10, crs=from_station,filterType="from")
        return response
    except Exception as e:
        return []