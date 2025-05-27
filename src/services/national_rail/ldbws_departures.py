import os, chatbot.journey_planner as journey_planner
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

def get_departing_time(from_station, to_station) -> str:
    optimal_route = journey_planner.get_optimal_path(from_station, to_station)
    leg = optimal_route[0]
    
    if not leg:
        return None
    
    data = get_next_departure(leg[0][0], leg[1][[0]])
    
    if data:
        return data.get("scheduled_departure_time")
    return None

def get_next_departure(from_station, to_station):
    response = get_direct_depature_board(from_station, to_station)
    
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

def get_direct_depature_board(from_station, to_station):
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

def get_departure_board(from_station):
    try:
        response = client.service.GetDepBoardWithDetails(numRows=10, crs=from_station,filterType="from")
        return response
    except Exception as e:
        return []

client = setup_client()