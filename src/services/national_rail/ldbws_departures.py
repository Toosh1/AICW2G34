import json
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

def get_departing_time(cliemt, from_station, to_station) -> str:
    data = get_next_departure(client, from_station, to_station)
    if data:
        return data.get("scheduled_departure_time")
    return None

def get_arrival_time(client, from_station, to_station) -> str:
    data = get_next_departure(client, from_station, to_station)
    last_calling_point = data.get("calling_points", [])[-1] if data.get("calling_points") else None
    if last_calling_point:
        return last_calling_point.get("scheduled_arrival_time")
    return None

def get_next_departure(client, from_station, to_station):
    response = get_direct_depature_board(client, from_station, to_station)
    
    if not (response and response.trainServices):
        return []
    
    services = response.trainServices.service
    if not services:
        return []
    
    next_service = services[0]
    data = {
        "scheduled_departure_time": next_service.std,
        "estimated_departure_time": next_service.etd,
        "platform_number": next_service.platform,
        "train_operator": next_service.operator,
        "destination_name": next_service.destination.location[0].locationName,
    }
    
    if hasattr(next_service, "subsequentCallingPoints"):
        calling_points = next_service.subsequentCallingPoints.callingPointList[0].callingPoint
        data["calling_points"] = [
            {
                "location_name": cp.locationName,
                "departure_time": cp.et,
                "scheduled_arrival_time": cp.st,
            }   
            for cp in calling_points
        ]
    return data

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

client = setup_client()

if __name__ == "__main__":
    from_station = "LST"
    to_station = "NRW"
    print(json.dumps(get_next_departure(client, from_station, to_station), indent=4))