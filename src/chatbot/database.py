import csv, json

station_codes = {}
responses = {}
extraction_patterns = {}

STATION_CODES_PATH = './src/data/stations.csv'
RESPONSES_PATH = './src/data/intentions.json'
EXTRACTION_PATH = './src/data/extraction_patterns.json'


def load_station_codes() -> dict[str, str]:
    """
    Load station codes from a CSV file into a dictionary.
    :return: A dictionary where the keys are station names and the values are their corresponding codes.
    """
    global station_codes
    if not station_codes:
        with open(STATION_CODES_PATH, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                cleaned_name = get_processed_station_name(row['name'])
                station_codes[cleaned_name] = row['crs']
    return station_codes


def load_responses() -> dict[str, str]:
    """
    Load responses from a CSV file into a dictionary.
    :return: A dictionary where the keys are intents and the values are their corresponding responses.
    """
    global responses
    if not responses:
        with open(RESPONSES_PATH, mode='r') as file:
            data = json.load(file)
            for intent, details in data.items():
                responses[intent] = details
    return responses


def load_patterns() -> dict[str, str]:
    """
    Load patterns from a JSON file into a dictionary.
    :return: A dictionary where the keys are intents and the values are their corresponding patterns.
    """
    global extraction_patterns
    if not extraction_patterns:
        with open(EXTRACTION_PATH, mode='r') as file:
            data = json.load(file)
            for intent, details in data.items():
                extraction_patterns[intent] = details
    return extraction_patterns


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
    for intent, patterns in extraction_patterns.items():
        if "preposition" not in intent:
            continue
        dictionary[intent] = patterns[0]["LOWER"]["in"]
    return dictionary


def get_extraction_patterns() -> list[list]:
    '''
    Get all departure and arrival patterns.
    :return: A list of all patterns.
    '''
    all_patterns = []
    for name, patterns in extraction_patterns.items():
        if not "preposition" in name:
            continue
        all_patterns.extend([patterns])
    return all_patterns


def get_next_series_patterns() -> list[list]:
    '''
    Get all next series patterns.
    :return: A list of all next series patterns.
    '''
    return extraction_patterns["next_series"]


def get_month_patterns() -> list[list]:
    '''
    Get all month patterns.
    :return: A list of all month patterns.
    '''
    return extraction_patterns["months"]


def get_depart_after_patterns() -> list[list]:
    '''
    Get all departure patterns.
    :return: A list of all departure patterns.
    '''
    patterns = []
    for name, pattern in extraction_patterns.items():
        if "depart_" in name:
            patterns.extend([pattern])
    return patterns


def get_arrive_before_patterns() -> list[list]:
    '''
    Get all arrival after patterns.
    :return: A list of all arrival after patterns.
    '''
    patterns = []
    for name, pattern in extraction_patterns.items():
        if "arrive_" in name:
            patterns.extend([pattern])
    return patterns


station_codes = load_station_codes()
responses = load_responses()
extraction_patterns = load_patterns()