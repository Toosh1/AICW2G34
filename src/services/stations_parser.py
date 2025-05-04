import xml.etree.ElementTree as ET
import pandas as pd

# Path to your XML file
xml_file = 'src/data/static_feeds/stations/tocs.xml'

# Parse the XML file
tree = ET.parse(xml_file)
root = tree.getroot()

# Define namespaces
namespaces = {
    'ns': 'http://nationalrail.co.uk/xml/station',
    'com': 'http://nationalrail.co.uk/xml/common',
    'add': 'http://nationalrail.co.uk/xml/address'
}

# Lists to hold data
rows = []

for station in root.findall('.//ns:Station', namespaces):
    def find_text(path):
        el = station.find(path, namespaces)
        return el.text.strip() if el is not None and el.text else None

    def get_address_line(index):
        lines = station.findall('.//add:Line', namespaces)
        return lines[index].text if len(lines) > index else None

    # Ticket office hours
    ticket_hours = {
        'Mon-Fri': [None, None],
        'Saturday': [None, None],
        'Sunday': [None, None]
    }

    for availability in station.findall('.//ns:TicketOffice/com:Open/com:DayAndTimeAvailability', namespaces):
        days = availability.find('com:DayTypes', namespaces)
        open_period = availability.find('com:OpeningHours/com:OpenPeriod', namespaces)
        if open_period is not None:
            start = open_period.find('com:StartTime', namespaces)
            end = open_period.find('com:EndTime', namespaces)

            if days is not None:
                if days.find('com:MondayToFriday', namespaces) is not None:
                    ticket_hours['Mon-Fri'] = [start.text if start is not None else None, end.text if end is not None else None]
                elif days.find('com:Saturday', namespaces) is not None:
                    ticket_hours['Saturday'] = [start.text if start is not None else None, end.text if end is not None else None]
                elif days.find('com:Sunday', namespaces) is not None:
                    ticket_hours['Sunday'] = [start.text if start is not None else None, end.text if end is not None else None]

    # Append extracted info
    rows.append({
        'CRS Code': find_text('ns:CrsCode'),
        'Station Name': find_text('ns:Name'),
        'Sixteen Character Name': find_text('ns:SixteenCharacterName'),
        'Longitude': find_text('ns:Longitude'),
        'Latitude': find_text('ns:Latitude'),
        'Station Operator': find_text('ns:StationOperator'),
        'National Location Code': find_text('ns:AlternativeIdentifiers/ns:NationalLocationCode'),
        'Address Line 1': get_address_line(0),
        'Address Line 2': get_address_line(1),
        'Address Line 3': get_address_line(2),
        'Address Line 4': get_address_line(3),
        'Postcode': find_text('.//add:PostCode'),
        'Ticket Office Mon-Fri Start': ticket_hours['Mon-Fri'][0],
        'Ticket Office Mon-Fri End': ticket_hours['Mon-Fri'][1],
        'Ticket Office Sat Start': ticket_hours['Saturday'][0],
        'Ticket Office Sat End': ticket_hours['Saturday'][1],
        'Ticket Office Sun Start': ticket_hours['Sunday'][0],
        'Ticket Office Sun End': ticket_hours['Sunday'][1],
        'Toilets Available': find_text('ns:StationFacilities/ns:Toilets/com:Available'),
        'Wheelchairs Available': find_text('ns:Accessibility/ns:WheelchairsAvailable/com:Available'),
    })

# Convert to DataFrame
stations_df = pd.DataFrame(rows)

# Save to CSV
stations_df.to_csv('src/data/csv/enhanced_stations.csv', index=False)

print("Data extraction complete. CSV file saved as 'enhanced_stations.csv'.")