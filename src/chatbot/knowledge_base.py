'''
    TODO - Implement max changes to the get_shortest_path function
'''
import csv, heapq
from collections import defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

STATION_CODES_PATH = "./src/data/csv/enhanced_stations.csv"
OLD_STATIONS_PATH = "./src/data/csv/stations.csv"
STATION_LINKS_PATH = "./src/data/static_feeds/routeing/RJRG0872.RGD"
LONDON_STATIONS_PATH = "./src/data/static_feeds/routeing/RJRG0872.RGC"
AWS_PATH = "./src/data/aws/"

station_codes = {}
station_graph = {}
london_stations = []
departure_table = {}

location_names = {}
late_reasons = {}
cancellation_reasons = {}
vias = {}
tocs = {}

def get_shortest_path(from_station: str, to_station: str) -> list[str]:
    global station_graph
    if not station_graph:
        station_graph = generate_station_graph()
    
    # Priority queue: (total_distance, current_station, path)
    heap = [(0, from_station, [])]
    visited = set()

    while heap:
        total_distance, current_station, path = heapq.heappop(heap)
        
        if current_station in visited:
            continue
        visited.add(current_station)
        
        path = path + [current_station]

        if current_station == to_station:
            return path
        
        for neighbor, data in station_graph.get(current_station, {}).items():
            if neighbor not in visited:
                distance = float(data['distance'])
                heapq.heappush(heap, (total_distance + distance, neighbor, path))
    
    return []  # No path found

def get_station_name_from_crs(crs: str) -> str:
    """
    Get the station name from the CRS code.
    :param crs: The CRS code.
    :return: The station name.
    """
    for _, data in station_codes.items():
        if crs in data.get("crs3"):
            return data["names"]
    return None

def get_crs_code_from_tpl(tpl: str) -> str:
    """
    Get the CRS code from the TPL code.
    :param tpl: The TPL code.
    :return: The CRS code.
    """
    for crs, data in station_codes.items():
        if tpl in data.get("crs3"):
            return crs
    return None

def get_departure_journey(rid: str) -> list[str]:
    journey_dict = departure_table.get(rid, None)
    
    if journey_dict is None:
        return []
    
    stops = journey_dict.get("stops", [])
    
    # Convert TPL codes to CRS codes
    crs_codes = [
        get_crs_code_from_tpl(stop["tpl"]) or stop["tpl"]
        for stop in stops if "tpl" in stop
    ]
    
    # Convert CRS Codes to names
    for i, crs in enumerate(crs_codes):
        if crs in location_names:
            locnames = location_names[crs]["locnames"]
            if locnames:
                crs_codes[i] = locnames[0]
    
    return crs_codes

def get_journey_interpoints(ns: dict, journey: ET.Element) -> list[dict[str, str]]:
    stops = []
    for ip_elem in journey.findall('ns:IP', ns):
        tpl = ip_elem.attrib.get('tpl')
        act = ip_elem.attrib.get('act')
        pta = ip_elem.attrib.get('pta')
        ptd = ip_elem.attrib.get('ptd')
        wta = ip_elem.attrib.get('wta')
        wtd = ip_elem.attrib.get('wtd')
        
        stops.append({
            "tpl": tpl,
            "act": act,
            "ptd": ptd,
            "wtd": wtd,
            "pta": pta,
            "wta": wta,
        })
    return stops

def get_journey_boundary(ns: dict, journey: ET.Element, boundary: str) -> dict[str, str]:
    """
    Get the origin of the journey from the XML element.
    :param ns: The namespace dictionary for XML parsing.
    :param journey: The XML element representing the journey.
    :return: The origin of the journey.
    """
    for elem in journey.findall(f'ns:{boundary}', ns):
        tpl = elem.attrib.get('tpl')
        act = elem.attrib.get('act')
        ptd = elem.attrib.get('ptd')
        wtd = elem.attrib.get('wtd')
        
        return {
            "tpl": tpl,
            "act": act,
            "ptd": ptd,
            "wtd": wtd,
        }

def process_journey_metadata(journey: ET.Element) -> tuple[str, dict[str, str]]:
    """
    Process the journey metadata to extract relevant information.
    :param journey: The XML element representing the journey.
    :return: A tuple containing the journey ID and a dictionary with journey details.
    """
    rid = journey.attrib.get('rid')
    train_id = journey.attrib.get('trainId')
    toc = journey.attrib.get('toc')
    status = journey.attrib.get('status')
    train_cat = journey.attrib.get('trainCat')
    
    return rid, {
        "trainId": train_id,
        "toc": toc,
        "status": status,
        "trainCat": train_cat,
        "stops": []
    }

def process_vias(root: ET.Element, ns) -> dict[str, dict[str, str]]:
    """
    Process the XML tree to extract Vias and their corresponding details.
    :param root: The root element of the XML tree.
    :return: A dictionary where the keys are Via codes and the values are dictionaries with Via details.
    """
    vias_dict = {}
    
    for via in root.findall('ns:Via', ns):
        via_at = via.attrib.get('at')
        via_dest = via.attrib.get('dest')
        via_loc1 = via.attrib.get('loc1')
        via_text = via.attrib.get('viatext')
        
        vias_dict.setdefault(via_at, {})[via_dest] = {"loc1": via_loc1, "viatext": via_text}
    
    return vias_dict

def process_reasons(root: ET.Element, ns, reason: str) -> dict[str, str]:
    """
    Process the XML tree to extract reasons and their corresponding codes and descriptions.
    :param root: The root element of the XML tree.
    :param reason: The reason type to process (e.g., 'RunningLateReasons', 'CancellationReasons').
    :return: A dictionary where the keys are reason codes and the values are their corresponding descriptions.
        """
    reasons_dict = {}
    
    for reason in root.findall(f'ns:{reason}', ns):
        for reason_elem in reason.findall('ns:Reason', ns):
            reason_code = reason_elem.attrib.get('code')
            reason_desc = reason_elem.attrib.get('reasontext')
            reasons_dict[reason_code] = reason_desc
    
    return reasons_dict

def process_tocref(root: ET.Element, ns) -> dict[str, str]:
    """
    Process the XML tree to extract TOC references and their corresponding names.
    :param root: The root element of the XML tree.
    :return: A dictionary where the keys are TOC codes and the values are their corresponding names.
    """
    tocs_dict = {}
    
    for tocref in root.findall('ns:TocRef', ns):
        toc = tocref.attrib.get('toc')
        tocname = tocref.attrib.get('tocname')
        tocs_dict[toc] = tocname
    
    return tocs_dict

def process_location_names(root: ET.Element, ns) -> dict[str, dict[str, str]]:
    """
    Process the XML tree to extract location names and their corresponding codes.
    :param root: The root element of the XML tree.
    :return: A dictionary where the keys are location codes and the values are dictionaries with location names.
    """
    locations = {}
    
    for loc in root.findall('ns:LocationRef', ns):
        tpl = loc.attrib.get('tpl')
        crs = loc.attrib.get('crs')
        locname = loc.attrib.get('locname')
        locations.setdefault(crs, {"tpl": tpl, "locnames": []})["locnames"].append(locname)
    return locations

def get_all_station_names() -> list[str]:
    """
    Get all station names from the station codes dictionary.
    :return: A list of all station names.
    """
    return [data["name"] for data in station_codes.values()]

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

def process_aws_departure_file(folder: str):
    folder = Path(folder)
    files = sorted([f for f in folder.iterdir() if f.is_file()])
    if not files:
        raise FileNotFoundError("No files found in the specified folder.")
    
    file_path = files[-1]
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    ns = {'ns': 'http://www.thalesgroup.com/rtti/XmlTimetable/v8'}
    departure_table = defaultdict(dict)
    
    # Loop through all the journeys in the XML file
    for journey in root.findall('ns:Journey', ns):
        
        isPassenger = journey.attrib.get('isPassenger')
        if isPassenger is not None and isPassenger != "true":
            continue
        
        rid, journey_dict = process_journey_metadata(journey)
        departure_table[rid] = journey_dict
        
        origin = get_journey_boundary(ns, journey, "OR")
        departure_table[rid]["stops"].append(origin)
        
        stops = get_journey_interpoints(ns, journey)
        departure_table[rid]["stops"].extend(stops)
        
        destination = get_journey_boundary(ns, journey, "DT")
        departure_table[rid]["stops"].append(destination)
    
    return departure_table

def process_aws_ref_file(folder: str):
    """
    Process the AWS reference file to extract location names, TOC references, and reasons.
    :param folder: The folder containing the XML files.
    :return: A tuple containing dictionaries for location names, TOC references, reasons, and vias.
    """
    folder = Path(folder)
    files = sorted([f for f in folder.iterdir() if f.is_file()])
    if not files:
        raise FileNotFoundError("No files found in the specified folder.")
    
    file_path = files[0]
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Example: parse LocationRef tags
    ns = {'ns': 'http://www.thalesgroup.com/rtti/XmlRefData/v3'}
    
    locs_dict = process_location_names(root, ns)
    tocs_dict = process_tocref(root, ns)
    late_reasons_dict = process_reasons(root, ns, 'RunningLateReasons')
    cancellation_reasons_dict = process_reasons(root, ns, 'CancellationReasons')
    vias_dict = process_vias(root, ns)
    return locs_dict, tocs_dict, late_reasons_dict, cancellation_reasons_dict, vias_dict

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

def get_london_stations() -> list[str]:
    """
    Get a list of London stations from the CSV file.
    :return: A list of London station names.
    """
    stations = []

    # Load the station links from the RGD file
    with open(LONDON_STATIONS_PATH, mode="r") as file:
        lines = file.readlines()
        
        # Skip the first 5 lines and ignore last line
        lines = lines[5:-1]
        for line in lines:
            # Split the line by comma and remove \n
            arr = line.strip().split(",")
            stations.append(arr[0].strip())
        
    return stations

def load_station_codes() -> dict[str, str]:
    """
    Load station codes from a CSV file into a dictionary.
    :return: A dictionary where the keys are station names and the values are their corresponding codes.
    """
    codes = {}
        
    with open(STATION_CODES_PATH, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            crs = row["CRS Code"]
            if crs == "":
                continue
            cleaned_name = get_processed_station_name(row["Station Name"])
            codes[crs] = {"name": cleaned_name}
            codes[crs]["crs3"] = []
    
    with open(OLD_STATIONS_PATH, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            crs3 = row["crs3"]
            crs = row["crs"]
            
            if crs not in codes:
                continue
            
            cleaned_name = get_processed_station_name(row["name"])
            codes[crs]["crs3"].append(crs3)
    
    return codes

# Main ------------------------------------------------------

station_codes = load_station_codes()
london_stations = get_london_stations()
station_graph = generate_station_graph()
location_names, tocs, late_reasons, cancellation_reasons, vias = process_aws_ref_file(AWS_PATH)
departure_table = process_aws_departure_file(AWS_PATH)