import csv
import json

station_codes = {}
responses = {}
dep_arr_patterns = {}


def process_station_name(name: str) -> str:
    """
    Process the station name to ensure it is in the correct format.
    :param station_name: The name of the station.
    :return: The processed station name.
    """
    name = name.replace(" Rail Station", "").strip()
    name = name.replace("-", " ")
    name = name.replace("(", "").replace(")", "")
        
    return name.lower().strip()


def get_station_code(station_name: str) -> str:
    """
    Get the station code for a given station name.
    :param station_name: The name of the station.
    :return: The station code.
    """
    global station_codes
    station_name = station_name.lower().strip()
    return station_codes.get(station_name, None)


def get_prepositions() -> dict[str, list]:
    """
    Get the prepositions used in the patterns.
    :return: A dictionary where the keys are intents and the values are lists of prepositions.
    """
    dictionary = {}
    for intent, patterns in dep_arr_patterns.items():
        dictionary[intent] = patterns[0]["LOWER"]["in"]
    return dictionary


def get_departure_arrival_patterns() -> list[list]:
    '''
    Get all departure and arrival patterns.
    :return: A list of all patterns.
    '''
    all_patterns = []
    for _, patterns in dep_arr_patterns.items():
        all_patterns.extend([patterns])
    return all_patterns


def load_station_codes() -> dict[str, str]:
    """
    Load station codes from a CSV file into a dictionary.
    :return: A dictionary where the keys are station names and the values are their corresponding codes.
    """
    global station_codes
    if not station_codes:
        with open('./src/data/stations.csv', mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                cleaned_name = process_station_name(row['name'])
                station_codes[cleaned_name] = row['crs']
    return station_codes


def load_responses() -> dict[str, str]:
    """
    Load responses from a CSV file into a dictionary.
    :return: A dictionary where the keys are intents and the values are their corresponding responses.
    """
    global responses
    if not responses:
        with open('./src/data/intentions.json', mode='r') as file:
            data = json.load(file)
            for intent, details in data.items():
                responses[intent] = details
    return responses


def load_patterns() -> dict[str, str]:
    """
    Load patterns from a JSON file into a dictionary.
    :return: A dictionary where the keys are intents and the values are their corresponding patterns.
    """
    global dep_arr_patterns
    if not dep_arr_patterns:
        with open('./src/data/departure_arrival_patterns.json', mode='r') as file:
            data = json.load(file)
            for intent, details in data.items():
                dep_arr_patterns[intent] = details
    return dep_arr_patterns


station_codes = load_station_codes()
responses = load_responses()
dep_arr_patterns = load_patterns()

get_prepositions()