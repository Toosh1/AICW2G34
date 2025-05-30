import json

INTENTIONS_PATH = "./src/data/json/intentions.json"
EXTRACTION_PATH = "./src/data/json/extraction_patterns.json"
CONSTRAINTS_path = "./src/data/json/constraints.json"
FAQ_PATH = "./src/data/json/station_intentions.json"

intentions = {}
extraction_patterns = {}
constraints = {}
station_faqs = {}

def load_station_faqs() -> dict[str, str]:
    """
    Load station FAQs from a JSON file into a dictionary.
    :return: A dictionary where the keys are station names and the values are their corresponding FAQs.
    """
    global station_faqs
    if not station_faqs:
        with open(FAQ_PATH, mode="r") as file:
            station_faqs = json.load(file)
    return station_faqs
    

def load_constraints() -> dict[str, list]:
    """
    Load constraints from a JSON file into a dictionary.
    :return: A dictionary where the keys are constraint types and the values are lists of patterns.
    """
    global constraints
    if not constraints:
        with open(CONSTRAINTS_path, mode="r") as file:
            constraints = json.load(file)
    return constraints

def load_intentions() -> dict[str, str]:
    """
    Load intentions from a CSV file into a dictionary.
    :return: A dictionary where the keys are intents and the values are their corresponding intentions.
    """
    global intentions
    if not intentions:
        with open(INTENTIONS_PATH, mode="r") as file:
            data = json.load(file)
            for intent, details in data.items():
                intentions[intent] = details
    return intentions

def load_patterns() -> dict[str, str]:
    """
    Load patterns from a JSON file into a dictionary.
    :return: A dictionary where the keys are intents and the values are their corresponding patterns.
    """
    global extraction_patterns
    if not extraction_patterns:
        with open(EXTRACTION_PATH, mode="r") as file:
            data = json.load(file)
            for intent, details in data.items():
                extraction_patterns[intent] = details
    return extraction_patterns

def get_prepositions(term: str) -> dict[str, list]:
    """
    Get the prepositions for a given term.
    :param term: The term to get prepositions for.
    :return: A dictionary of prepositions for the term.
    """
    return extraction_patterns["words"]["synonyms"][term]

def get_extraction_patterns() -> list[list]:
    """
    Get all extraction patterns.
    :return: A list of all extraction patterns.
    """
    global extraction_patterns
    all_patterns = []

    for station_bound in ["departure", "arrival"]:
        pattern = []
        synonyms = extraction_patterns["words"]["synonyms"][station_bound]
        synonyms_pattern = get_pattern_array(synonyms)
        pattern.append(synonyms_pattern)
        pattern.append(extraction_patterns["patterns"]["station_prepositions"][0])
        all_patterns.append(pattern)
    return all_patterns

def get_next_series_patterns() -> list[list]:
    """
    Get all next series patterns.
    :return: A list of all next series patterns.
    """
    patterns = extraction_patterns["patterns"]["next_series"]
    time_series = extraction_patterns["words"]["synonyms"]["time"]
    time_series_pattern = get_pattern_array(time_series)
    patterns.append(time_series_pattern)
    return patterns

def get_month_patterns() -> list[list]:
    """
    Get all month patterns.
    :return: A list of all month patterns.
    """
    return [get_pattern_array(extraction_patterns["words"]["synonyms"]["months"])]

def get_dates() -> list:
    """
    Gets all dates from the 1st of the month to the 31st.
    :return: A list of all dates
    """
    return extraction_patterns["words"]["dates"]

def get_default_time_constraint() -> list:
    """
    Get the default time constraint pattern.
    """
    return extraction_patterns["patterns"]["time_constraint_default"]

def get_time_constraint_patterns(synonyms_name: str) -> list[list]:
    """
    Get all time constraint patterns.
    :param synonyms_name: The name of the synonyms to use.
    :return: A list of all time constraint patterns.
    """
    patterns = []
    synonyms = extraction_patterns["words"]["synonyms"][synonyms_name]
    synonyms_pattern = get_pattern_array(synonyms)

    default_pattern = extraction_patterns["patterns"]["time_constraint_default"][0]
    location_patterns = extraction_patterns["patterns"]["time_constraint_locations"]

    place_pattern = [synonyms_pattern, location_patterns[0], default_pattern]
    general_pattern = [synonyms_pattern, location_patterns[1], default_pattern]

    patterns.append(general_pattern)
    patterns.append(place_pattern)

    return patterns

def get_depart_after_patterns() -> list[list]:
    """
    Get all departure patterns.
    :return: A list of all departure patterns.
    """
    return get_time_constraint_patterns("depart") + [extraction_patterns["patterns"]["time_constraint_depart"]]

def get_arrive_before_patterns() -> list[list]:
    """
    Get all arrival patterns.
    :return: A list of all arrival patterns.
    """
    return get_time_constraint_patterns("arrive") + [extraction_patterns["patterns"]["time_constraint_arrive"]]

def get_return_patterns() -> list[list]:
    """
    Get all return patterns.
    :return: A list of all return patterns.
    """
    return [[get_pattern_array(extraction_patterns["words"]["synonyms"]["return"])]]

def get_pattern_array(arr: list) -> dict:
    """
    Get the pattern array for a given list.
    :param arr: The list to get the pattern array for.
    :return: The pattern array.
    """
    return {"LOWER": {"in": arr}}

def get_intentions_training_data() -> list:
    training_sentences = []
    intent_labels = []
    
    for key in intentions:
        for pattern in intentions[key]["patterns"]:
            training_sentences.append(pattern.lower())
            intent_labels.append(key.lower())
    return training_sentences, intent_labels

def get_constraint_training_data() -> list:
    training_sentences = []
    intent_labels = []
    
    for key in constraints:
        for pattern in constraints[key]:
            training_sentences.append(pattern.lower())
            intent_labels.append(key.lower())
    return training_sentences, intent_labels

def get_faq_training_data() -> list:
    training_sentences = []
    intent_labels = []
    
    for key in station_faqs:
        for pattern in station_faqs[key]["patterns"]:
            training_sentences.append(pattern.lower())
            intent_labels.append(key.lower())
    return training_sentences, intent_labels

intentions = load_intentions()
extraction_patterns = load_patterns()
constraints = load_constraints()
station_faqs = load_station_faqs()