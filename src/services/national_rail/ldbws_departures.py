import os
from zeep import Client
from dotenv import load_dotenv
from collections import deque

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

def get_all_routes_from_station_bfs(client, start_station, depth=2):
    # Queue for BFS, stores tuples of (current_station, current_path, current_depth)
    queue = deque([(start_station, [start_station], 0)])
    visited = set()  # To keep track of visited stations
    routes = []  # To store all routes

    while queue:
        current_station, current_path, current_depth = queue.popleft()

        # If we've reached the desired depth, stop expanding further
        if current_depth >= depth:
            continue

        # Mark the station as visited
        visited.add(current_station)

        # Get departure board for the current station
        departures = get_departure_board(client, current_station)

        # Explore each service's calling points
        for service in departures.trainServices.service:
            for calling_point in service.subsequentCallingPoints.callingPointList[0].callingPoint:
                station_code = calling_point.crs
                if station_code not in visited:
                    new_path = current_path + [station_code]
                    routes.append(new_path)  # Add the new path to the routes list
                    queue.append((station_code, new_path, current_depth + 1))  # Add the new station to the queue

    return routes

if __name__ == "__main__":
    client = setup_client()
    start_station = "SOU"  # Southampton
    end_station = "MAN"  # Nottingham
    
    # departure_board = get_departure_board(client, start_station)
    # direct_board = get_direct_depature_board(client, start_station, end_station)
    
    # for service in direct_board.trainServices.service:
    #     print(service.std, service.destination.location[0].locationName)
    #     for stop in service.subsequentCallingPoints.callingPointList[0].callingPoint:
    #         print(stop.locationName)
    #     print("\n")
    
    routes_start = get_all_routes_from_station_bfs(client, start_station, depth=2)

    if routes_start:
        print(f"All possible routes from {start_station} (depth=2):")
        for route in routes_start:
            print(" -> ".join(route))
    else:
        print(f"No routes found from {start_station}.")