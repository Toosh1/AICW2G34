'''
    1. Get all rids where from_crs is in the list of crs3 codes, excluding DT stations
    2. Loop through all rids
    3. Get the subsequent stops for each rid
    4. Check if stop is to_crs
    5. Else, get all rids where the stop is in the list of stops, excluding DT stations and repeat the process
'''
from collections import deque
import csv, psycopg2, os
from pathlib import Path
from dotenv import load_dotenv
import xml.etree.ElementTree as ET

load_dotenv()

STATION_CODES_PATH = "./src/data/csv/enhanced_stations.csv"
OLD_STATIONS_PATH = "./src/data/csv/stations.csv"
STATION_LINKS_PATH = "./src/data/static_feeds/routeing/RJRG0872.RGD"
LONDON_STATIONS_PATH = "./src/data/static_feeds/routeing/RJRG0872.RGC"
AWS_PATH = "./src/data/aws/"

station_graph = {}
london_stations = []

location_names = {}
late_reasons = {}
cancellation_reasons = {}
vias = {}
tocs = {}

intent_to_function = {
    "train_delays": "",#function to get train delays
    "route_details": "",#function to get route details
    "departure_time": "",#function to get departure time
    "arrival_times": "",#function to get arrival times
    "platform_details": "",#function to get platform details
    "address_details": ["database",["address1","address2","address3","address4","postcode"]],
    "train_operator": ["database",["operator"]],
    "ticket_off_hours": ["database",["ticket_office_hours"]],
    "ticket_machine": ["database",["ticket_machine_available"]],
    "seated_area": ["database",["seated_area_available"]],
    "waiting_area": ["database",["waiting_room_available"]],
    "toilets": ["database",["toilets_available"]],
    "baby_changing": ["database",["baby_change_available"]],
    "wifi": ["database",["wifi_available"]],
    "ramp_access": ["database",["ramp_for_train_access_available"]],
    "ticket_gates": ["database",["ticket_gates_available"]],
}

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="postgres",
    user="postgres",
    password=os.getenv("POSTGRES_PASSWORD")
)


def get_stops_from_departure(rid: str) -> list[str]:
    """
    Get all stops from a given rid (Route ID).
    :param rid: The rid to get stops from.
    :return: A list of tpl (Train Platform Location) for the stops.
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT tpl FROM stops
            WHERE rid = %s
            ORDER BY stop_id
        """, (rid,))
        rows = cur.fetchall()
        return [row[0] for row in rows]

def get_departures(from_tpl: str) -> list[str]:
    """
    Get all departures from a given tpl (Train Platform Location).
    :param from_tpl: The tpl to get departures from.
    :return: A list of rids (Route IDs) for the departures.
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT rid FROM stops 
            WHERE tpl = %s
            AND type != 'DT'
        """, (from_tpl,))
        rows = cur.fetchall()
        return [row[0] for row in rows]

def create_departure_table() -> None:
    with conn.cursor() as cur:
        # Delete the table if it exists
        cur.execute("DROP TABLE IF EXISTS departures")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS departures (
                rid VARCHAR(255) PRIMARY KEY,
                uid VARCHAR(255),
                train_id VARCHAR(255),
                ssd VARCHAR(255),
                toc VARCHAR(255),
                status VARCHAR(255),
                train_cat VARCHAR(255)
            )
        """)
        conn.commit()

def create_stops_table() -> None:
    with conn.cursor() as cur:
        # Delete the table if it exists
        cur.execute("DROP TABLE IF EXISTS stops")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS stops (
                stop_id SERIAL PRIMARY KEY,
                rid VARCHAR(255),
                tpl VARCHAR(255),
                act VARCHAR(255),
                ptd TIME,
                wtd TIME,
                pta TIME,
                wta TIME,
                plat VARCHAR(255),
                type VARCHAR(255)
            )
        """)
        conn.commit()

def insert_departure_data(rid: str, journey_dict: dict) -> None:
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO departures (rid, train_id, ssd, toc, status, train_cat)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING rid
        """, (
            rid,
            journey_dict.get("trainId"),
            journey_dict.get("ssd"),
            journey_dict.get("toc"),
            journey_dict.get("status"),
            journey_dict.get("trainCat")
        ))

        rid = cur.fetchone()[0]

        for stop in journey_dict.get("stops", []):
            if stop is None:
                continue
            cur.execute("""
                INSERT INTO stops (rid, tpl, act, ptd, wtd, pta, wta, plat, type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                rid,
                stop.get("tpl"),
                stop.get("act"),
                stop.get("ptd"),
                stop.get("wtd"),
                stop.get("pta"),
                stop.get("wta"),
                stop.get("plat"),
                stop.get("type")
            ))
        conn.commit()

def get_journey_interpoints(ns: dict, journey: ET.Element) -> list[dict[str, str]]:
    stops = []
    for ip_elem in journey.findall('ns:IP', ns):
        stops.append({
            "tpl": ip_elem.attrib.get('tpl'),
            "act": ip_elem.attrib.get('act'),
            "ptd": ip_elem.attrib.get('ptd'),
            "wtd": ip_elem.attrib.get('wtd'),
            "pta": ip_elem.attrib.get('pta'),
            "wta": ip_elem.attrib.get('wta'),
            "type": "IP",
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
        return {
            "tpl": elem.attrib.get('tpl'),
            "act": elem.attrib.get('act'),
            "ptd": elem.attrib.get('ptd'),
            "wtd": elem.attrib.get('wtd'),
            "plat": elem.attrib.get('plat'),
            "type": boundary,
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

def process_aws_departure_file(folder: str):
    folder = Path(folder)
    files = sorted([f for f in folder.iterdir() if f.is_file()])
    if not files:
        raise FileNotFoundError("No files found in the specified folder.")
    
    file_path = files[-1]
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    ns = {'ns': 'http://www.thalesgroup.com/rtti/XmlTimetable/v8'}
    
    # Loop through all the journeys in the XML file
    for journey in root.findall('ns:Journey', ns):
        
        isPassenger = journey.attrib.get('isPassenger')
        if isPassenger is not None and isPassenger != "true":
            continue
        
        rid, journey_dict = process_journey_metadata(journey)
        origin = get_journey_boundary(ns, journey, "OR")
        stops = get_journey_interpoints(ns, journey)
        destination = get_journey_boundary(ns, journey, "DT")
        
        journey_dict["stops"].append(origin)
        journey_dict["stops"].extend(stops)
        journey_dict["stops"].append(destination)
        
        insert_departure_data(rid, journey_dict)
    print(f"Processed {len(root.findall('ns:Journey', ns))} journeys from {file_path.name}.")

def generate_departure_table() -> None:
    """
    Deletes and creates the departure table in the PostgreSQL database.
    Should be called once to set up the table.
    :return: None
    """
    create_departure_table()
    create_stops_table()
    process_aws_departure_file(AWS_PATH)

#endregion AWS Departure Table Creation ---

#region Station Codes Table Creation ---

def get_station_code_from_name(name: str) -> str:
    """
    Get the station code from the station name.
    :param name: The name of the station.
    :return: The CRS code of the station.
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT crs FROM station_codes
            WHERE name = %s
        """, (name,))
        row = cur.fetchone()
        if row is not None:
            return row[0]
        return "Invalid station name."

def get_all_station_details(crs: str) -> str:
    """
    Get all station details from the database.
    :param crs: The CRS code of the station.
    :return: A sentence summarizing the station's details.
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT * FROM station_codes
            WHERE crs = %s
        """, (crs,))
        row = cur.fetchone()
        if row is None:
            return "Invalid station code."

        (
            crs_code, name, crs3, longitude, latitude, operator, location_code, address1, address3,
            address2, address4, postcode, ticket_office_hours, ticket_machine_available,
            seated_area_available, waiting_room_available, toilets_available,
            baby_change_available, wifi_available, ramp_for_train_access_available,
            ticket_gates_available
        ) = row
        
        operator_name = tocs.get(operator, operator)

        sentence = f"{name} station ({crs_code}) is operated by {operator_name}.\n" 
        sentence += f"It is located at {address1}, {address2}, {address3}, {address4}, {postcode}.\n"
        
        if ticket_office_hours:
            # Convert "06:00:00.000" → "06:00" and "00.000" → "00"
            parts = ticket_office_hours.replace(".", ":").split(":")
            start = f"{int(parts[0]):02d}:{int(parts[1]):02d}"
            end = f"{int(parts[2]):02d}:{int(parts[3]):02d}"
            sentence += f"The ticket office is open from {start} to {end}\n\n"

        features = [
            feature for feature, available in [
            ("a ticket machine", ticket_machine_available),
            ("a seated area", seated_area_available),
            ("a waiting room", waiting_room_available),
            ("toilets", toilets_available),
            ("baby changing facilities", baby_change_available),
            ("Wi-Fi", wifi_available),
            ("a ramp for train access", ramp_for_train_access_available),
            ("ticket gates", ticket_gates_available),
            ] if available
        ]

        if features:
            sentence += "The station has the following facilities:\n"
            for feature in features:
                sentence += f"  • {feature.capitalize()}\n"
        else:
            sentence += "\n\nThis station does not list any specific facilities."

        return sentence

def get_station_info(crs: str, column: str) -> str:
    """
    Get the station information from the database.
    :param crs: The CRS code of the station.
    :param column: The column to retrieve from the database.
    :return: The station information.
    """
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT {column} FROM station_codes
            WHERE crs = %s
        """, (crs,))
        row = cur.fetchone()
        if row is not None:
            return row[0]
        return "Invalid station code."

def create_station_codes_table() -> None:
    with conn.cursor() as cur:
        # Delete the table if it exists
        cur.execute("DROP TABLE IF EXISTS station_codes")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS station_codes (
                crs VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255),
                crs3 VARCHAR(255)[],
                longitude FLOAT,
                latitude FLOAT,
                operator VARCHAR(255),
                location_code VARCHAR(255),
                address1 VARCHAR(255),
                address2 VARCHAR(255),
                address3 VARCHAR(255),
                address4 VARCHAR(255),
                postcode VARCHAR(255),
                ticket_office_hours VARCHAR(255),
                ticket_machine_available BOOLEAN,
                seated_area_available BOOLEAN,
                waiting_room_available BOOLEAN,
                toilets_available BOOLEAN,
                baby_change_available BOOLEAN,
                wifi_available BOOLEAN,
                ramp_for_train_access_available BOOLEAN,
                ticket_gates_available BOOLEAN
            )
        """)
        conn.commit()

def insert_station_codes_data(crs: str, data: dict) -> None:
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO station_codes (crs, name, crs3, longitude, latitude, operator, location_code, address1, address2, address3, address4, postcode, ticket_office_hours, 
                ticket_machine_available, seated_area_available, waiting_room_available, toilets_available, baby_change_available, 
                wifi_available, ramp_for_train_access_available, ticket_gates_available)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            crs,
            data.get("name"),
            data.get("crs3", []),
            data.get("longitude"),
            data.get("latitude"),
            data.get("operator"),
            data.get("location_code"),
            data.get("address1"),
            data.get("address2"),
            data.get("address3"),
            data.get("address4"),
            data.get("postcode"),
            data.get("ticket_office_hours"),
            bool(data.get("ticket_machine_available", False)),
            bool(data.get("seated_area_available", False)),
            bool(data.get("waiting_room_available", False)),
            bool(data.get("toilets_available", False)),
            bool(data.get("baby_change_available", False)),
            bool(data.get("wifi_available", False)),
            bool(data.get("ramp_for_train_access_available", False)),
            bool(data.get("ticket_gates_available", False)),
        ))
        conn.commit()

def add_crs3_to_table(crs: str, crs3: str) -> None:
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE station_codes
            SET crs3 = array_append(crs3, %s)
            WHERE crs = %s
        """, (crs3, crs))
        conn.commit()

def process_station_csv() -> None:
    with open(STATION_CODES_PATH, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            crs = row["CRS Code"]
            station_dict = {
                "name": row["Station Name"],
                "longitude": row["Longitude"],
                "latitude": row["Latitude"],
                "operator": row["Station Operator"],
                "location_code": row["National Location Code"],
                "address1": row["Address Line 1"],
                "address2": row["Address Line 2"],
                "address3": row["Address Line 3"],
                "address4": row["Address Line 4"],
                "postcode": row["Postcode"],
                "ticket_office_hours": row["Ticket Office Hours"],
                "ticket_machine_available": row["Ticket Machine Available"],
                "seated_area_available": row["Seated Area Available"],
                "waiting_room_available": row["Waiting Room Available"],
                "toilets_available": row["Toilets Available"],
                "baby_change_available": row["Baby Change Available"],
                "wifi_available": row["WiFi Available"],
                "ramp_for_train_access_available": row["Ramp For Train Access Available"],
                "ticket_gates_available": row["Ticket Gates Available"],
                "cycle_storage_spaces": row["Cycle Storage Spaces"],
            }
            insert_station_codes_data(crs, station_dict)
    
    with open(OLD_STATIONS_PATH, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            add_crs3_to_table(row["crs"], row["crs3"])

def generate_station_codes_table() -> None:
    """
    Deletes and creates the station codes table in the PostgreSQL database.
    Should be called once to set up the table.
    :return: None
    """
    create_station_codes_table()
    process_station_csv()
    print("Station codes table created and populated successfully.")

#endregion Station Codes Table Creation ---

#region AWS Reference File Creation ---

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
    
    ns = {
            'ns': 'http://www.thalesgroup.com/rtti/XmlTimetable/v99/rttiCTTReferenceSchema.xsd',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsd': 'http://www.w3.org/2001/XMLSchema'
        }
    
    locs_dict = process_location_names(root, ns)
    tocs_dict = process_tocref(root, ns)
    late_reasons_dict = process_reasons(root, ns, 'LateRunningReasons')
    cancellation_reasons_dict = process_reasons(root, ns, 'CancellationReasons')
    vias_dict = process_vias(root, ns)
    return locs_dict, tocs_dict, late_reasons_dict, cancellation_reasons_dict, vias_dict

#endregion AWS Reference File Creation ---

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

def get_all_station_names() -> list[str]:
    """
    Get all station names from the station codes table.
    :return: A list of all station names.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT name FROM station_codes")
        rows = cur.fetchall()
        return [get_processed_station_name(row[0]) for row in rows]

# Main ------------------------------------------------------

# generate_station_codes_table()
# generate_departure_table()

london_stations = get_london_stations()
location_names, tocs, late_reasons, cancellation_reasons, vias = process_aws_ref_file(AWS_PATH)
station_graph = generate_station_graph()