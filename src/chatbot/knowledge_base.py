import csv

STATION_CODES_PATH = "./src/data/csv/enhanced_stations.csv"
STATION_LINKS_PATH = "./src/data/static_feeds/routeing/RJRG0872.RGD"
LONDON_STATIONS_PATH = "./src/data/csv/london_stations.csv"

station_codes = {}
station_graph = {}
london_stations = []

def get_processed_station_name(name: str) -> str:
    """
    Process the station name to ensure it is in the correct format.
    :param station_name: The name of the station.
    :return: The processed station name.
    """
    name = name.replace(" Rail Station", "").strip()
    name = name.replace("-", " ")
    name = name.replace("(", "").replace(")", "")

    return name.lower().strip()

def load_station_codes() -> dict[str, str]:
    """
    Load station codes from a CSV file into a dictionary.
    :return: A dictionary where the keys are station names and the values are their corresponding codes.
    """
    global station_codes
    if not station_codes:
        with open(STATION_CODES_PATH, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                cleaned_name = get_processed_station_name(row["Station Name"])
                station_codes[cleaned_name] = row["CRS Code"]
    return station_codes

def get_london_stations() -> list[str]:
    """
    Get a list of London stations from the CSV file.
    :return: A list of London station names.
    """
    global london_stations
    if not london_stations:
        with open(LONDON_STATIONS_PATH, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                london_stations.append(row["Station Code"])
    return london_stations

def get_station_links(station_name: str) -> dict[str, dict[str, str]]:
    """
    Get the links for a given station from the station graph.
    :param station_name: The name of the station.
    :return: A dictionary of links for the given station.
    """
    global station_graph
    if not station_graph:
        station_graph = generate_station_graph()
    
    if station_name in station_graph:
        return station_graph[station_name]
    
    return {}

def generate_station_graph() -> dict[str, str]:
    """
    Generate a graph of stations and their links from the RGD file.
    Then add all London stations as links to each other.
    :return: A dictionary representing the graph of stations and their links.
    """
    graph = {}
    
    # Load the station links from the RGD file
    with open(STATION_LINKS_PATH, mode="r") as file:
        lines = file.readlines()
        
        # Skip the first 5 lines and ignore last line
        lines = lines[5:-1]
        for line in lines:
            # Split the line by comma and remove \n
            arr = line.strip().split(",")
        
            from_station = arr[0].strip()
            to_station = arr[1].strip()
            distance = arr[2].strip()
            
            if from_station not in graph:
                graph[from_station] = {}
            
            if to_station not in graph[from_station]:
                graph[from_station][to_station] = {
                    "fare": 0,
                    "distance": distance
                }
    
    # Loop through london stations and add them to the graph, if they are not already present
    # Then add all the other stations as a link to that station
    for station in london_stations:
        if station not in graph:
            graph[station] = {}
        for other_station in graph.keys():
            if other_station != station and other_station not in graph[station]:
                graph[station][other_station] = {
                    "fare": 0,
                    "distance": 0
                }
    
    return graph

station_codes = load_station_codes()
london_stations = get_london_stations()
station_graph = generate_station_graph()