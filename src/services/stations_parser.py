import xml.etree.ElementTree as ET
import pandas as pd

csv_file = 'src/data/csv/enhanced_stations.csv'

namespaces = {
    'ns': 'http://nationalrail.co.uk/xml/station',
    'com': 'http://nationalrail.co.uk/xml/common',
    'add': 'http://www.govtalk.gov.uk/people/AddressAndPersonalDetails'
}

def find_text(station, path):
    el = station.find(path, namespaces)
    return el.text.strip() if el is not None and el.text else None

def get_address_line(station, index):
    lines = station.findall('.//add:Line', namespaces)
    return lines[index].text if len(lines) > index else None

def get_ticket_hours(station) -> list[str]:
    """
    Extracts ticket office hours from the station element.
    Returns a dictionary with the ticket office hours for each day of the week.
    """
    
    # Ticket office hours
    ticket_hours = {
        'Mon-Fri': [None, None],
        'Saturday': [None, None],
        'Sunday': [None, None]
    }
    
    for availability in station.findall('.//ns:TicketOffice/com:Open/com:DayAndTimeAvailability', namespaces):
        days = availability.find('com:DayTypes', namespaces)
        open_period = availability.find('com:OpeningHours/com:OpenPeriod', namespaces)
        if open_period is None:
            continue
        
        start = open_period.find('com:StartTime', namespaces)
        end = open_period.find('com:EndTime', namespaces)

        if days is None:
            continue

        if days.find('com:MondayToFriday', namespaces) is not None:
            ticket_hours['Mon-Fri'] = [start.text if start is not None else None, end.text if end is not None else None]
        elif days.find('com:Saturday', namespaces) is not None:
            ticket_hours['Saturday'] = [start.text if start is not None else None, end.text if end is not None else None]
        elif days.find('com:Sunday', namespaces) is not None:
            ticket_hours['Sunday'] = [start.text if start is not None else None, end.text if end is not None else None]
    return ticket_hours

def get_row_data(station, ticket_hours) -> dict[str, str]:
    """
    Extracts relevant data from a station element and returns it as a dictionary.
    """
    return {
        'CRS Code': find_text(station, 'ns:CrsCode'),
        'Station Name': find_text(station, 'ns:Name'),
        'Sixteen Character Name': find_text(station, 'ns:SixteenCharacterName'),
        'Longitude': find_text(station, 'ns:Longitude'),
        'Latitude': find_text(station, 'ns:Latitude'),
        'Station Operator': find_text(station, 'ns:StationOperator'),
        'National Location Code': find_text(station, 'ns:AlternativeIdentifiers/ns:NationalLocationCode'),
        'Address Line 1': get_address_line(station, 0),
        'Address Line 2': get_address_line(station, 1),
        'Address Line 3': get_address_line(station, 2),
        'Address Line 4': get_address_line(station, 3),
        'Postcode': find_text(station, './/add:PostCode'),
        'Ticket Machine Available': find_text(station, './/ns:TicketMachine/com:Available'),
        'Seated Area Available': find_text(station, './/ns:SeatedArea/com:Available'),
        'Waiting Room Available': find_text(station, './/ns:WaitingRoom/com:Available'),
        'Toilets Available': find_text(station, './/ns:Toilets/com:Available'),
        'Baby Change Available': find_text(station, './/ns:BabyChange/com:Available'),
        'WiFi Available': find_text(station, './/ns:WiFi/com:Available'),
        'Ramp For Train Access Available': find_text(station, './/ns:RampForTrainAccess/com:Available'),
        'Ticket Gates Available': find_text(station, './/ns:TicketGates/com:Available'),
        'Cycle Storage Spaces': find_text(station, './/ns:CycleStorage/Spaces'),
        'Ticket Office Hours': find_text(station, './/ns:TicketOffice/com:Open/com:DayAndTimeAvailability/com:OpeningHours/com:OpenPeriod/com:StartTime'),
    }

def get_enhanced_stations() -> None:
    xml_file = 'src/data/static_feeds/stations/tocs.xml'
    tree = ET.parse(xml_file)
    root = tree.getroot()
    rows = []

    for station in root.findall('.//ns:Station', namespaces):
        ticket_hours = get_ticket_hours(station)
        rows.append(get_row_data(station, ticket_hours))

    stations_df = pd.DataFrame(rows)
    stations_df.to_csv(csv_file, index=False)
    print(f"+ Stations data saved to {csv_file}")
