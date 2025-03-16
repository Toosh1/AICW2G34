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


def get_depature_board(client, from_station, to_station):
    try:
        # Get departure board info
        response = client.service.GetDepBoardWithDetails(
            numRows=10,
            crs=from_station,
            filterCrs=to_station,
            filterType="to",
        )
        print("🚆 Departure Board Info Found")
        return response
    
    except Exception as e:
        print("🚨 Error: ", e)
        return None


client = setup_client()

specific_departure_board = get_depature_board(client, "NRW", "LST")

if specific_departure_board:
    for service in specific_departure_board.trainServices.service:
        print(service.std, service.destination.location[0].locationName)
        for stop in service.subsequentCallingPoints.callingPointList[0].callingPoint:
            print(stop.locationName)
        print("\n")