'''
Pisces: A Train Travel Assistant

Checklist

- Extract Stations ✔
- Extract Date and Time ✔
    - Check if single or return
- Departing After or Arriving Before ✔
- Cleanup `train_ticket_handler.py` ✔
- Run Test Cases on nlp.py ✔
    - Add more test case parameters

# Current assumptions
    - No railcards
    - Only 1 adult
    - No children
    - No extra time
    - No journey options
'''

import sys, os, re, spacy
from spacy.matcher import Matcher
from rapidfuzz import process

# Merge the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from chatbot.database import *
from utils.input_handler import *

# Load spaCy's English model
nlp = spacy.load("en_core_web_sm")
preposition_matcher = None
type_matcher = None


def setup() -> None:
    add_stations_to_vocab()
    add_series_entity_ruler()
    add_station_entity_ruler()
    add_matcher_patterns()


def add_stations_to_vocab() -> None:
    '''
    Add station names to the spaCy vocabulary for spell checking.
    :return: None
    '''
    stations_list = [station.lower() for station in station_codes.keys()]
    station_words = {token for station in stations_list for token in station.split()}
    add_to_vocabulary(station_words)
    add_to_vocabulary(stations_list)


def add_station_entity_ruler() -> None:
    '''
    Add a custom entity ruler to the spaCy pipeline for station names.
    :return: None
    '''
    ruler = nlp.add_pipe("entity_ruler", config={"overwrite_ents": True}, name="station_ruler", after="ner")
    
    stations = [station.upper() for station in station_codes.keys()]
    # Remove any overlapping names
    places = {station.split(" ")[0] for station in stations} - set(stations)

    station_patterns = [{"label": "STATION", "pattern": station} for station in stations]
    place_patterns = [{"label": "PLACE", "pattern": place} for place in places]
    
    ruler.add_patterns(station_patterns)
    ruler.add_patterns(place_patterns)        


def add_series_entity_ruler() -> None:
    '''
    Add a custom entity ruler to the spaCy pipeline for series names.
    :return: None
    '''
    ruler = nlp.add_pipe("entity_ruler", name="series_ruler", before="ner")
    series_pattern = [{"label": "SERIES", "pattern": get_next_series_patterns()}]
    ruler.add_patterns(series_pattern)

    ruler = nlp.add_pipe("entity_ruler", name="month_ruler", after="ner")
    month_pattern = [{"label": "MONTH", "pattern": get_month_patterns()}]
    ruler.add_patterns(month_pattern)


def add_matcher_patterns() -> None:
    '''
    Add custom patterns to the spaCy matcher for train routes.
    This includes departure and arrival patterns.
    The patterns are defined in the knowledge base.
    :return: None
    '''
    global type_matcher, preposition_matcher
    type_matcher = Matcher(nlp.vocab)
    preposition_matcher = Matcher(nlp.vocab)
    preposition_matcher.add("PREPOSITIONS", get_extraction_patterns(), greedy="LONGEST")
    type_matcher.add("DEPARTING", get_depart_after_patterns(), greedy="LONGEST")
    type_matcher.add("ARRIVING", get_arrive_before_patterns(), greedy="LONGEST")


def extract_date_time(text: str) -> str:
    '''
    Extract date and time from the text using regex.
    :param text: The input text to search for date and time.
    :return: The extracted date and time or None if not found.
    '''
    
    TIME_ENTITIES = ["TIME", "DATE", "ORDINAL", "SERIES", "MONTH"]
    
    text = preprocess_time(text)
    doc = nlp(text)
    journeys = {"DATE": [], "TIME": []}
    
    for ent in doc.ents:
        if not ent.label_ in TIME_ENTITIES:
            continue
        
        match ent.label_:
            case "DATE":
                journeys["DATE"].append(ent.text)
            case "TIME":
                journeys["TIME"].append(ent.text)
            case "ORDINAL":
                journeys["DATE"].append(ent.text)
            case "SERIES":
                journeys["DATE"].append(ent.text)
            case "MONTH":
                journeys["DATE"].append(ent.text)

    return journeys, parse_time(journeys)


def extract_station(type: str, text: str, terms: list) -> str:
    '''
    Extract the station name from the text using regex.
    :param type: The type of station (departure or arrival).
    :param text: The input text to search for the station name.
    :param terms: The list of terms to search for.
    :return: The extracted station name or None if not found.
    '''
    # Return station name if already found
    if not (type is None):
        return type
    
    for term in terms:
        match = re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE)
        if match:
            return re.sub(rf"\b{re.escape(term)}\b", "", text, count=1, flags=re.IGNORECASE).strip()


def find_closest_stations(query: str) -> list:
    '''
    Suggest the closest matching station names based on the query.
    :param query: The input query string
    :return: A list of similar station names
    '''
    station_names = [station.lower() for station in station_codes.keys()]
    similar_stations = process.extract(query.lower(), station_names, limit=3)
    # Return only the station names
    return [station[0] for station in similar_stations]


def extract_train_info(text: str) -> tuple:
    '''
    Extract train information from the user input using spaCy's matcher.
    :param user_input: The input text from the user.
    :return: A tuple containing the departure and arrival stations and similar stations.
    '''
    
    # Preprocess the input text
    text = preprocess_text(text)
    doc = nlp(text)
    
    # Modify the text, based off the tense of the text and re-process
    text = modify_tenses(doc)
    doc = nlp(text)
    
    # Apply the matcher to the document
    matches = preposition_matcher(doc)
    departure = None
    arrival = None
    
    prepositions = get_prepositions()
    departure_terms = prepositions.get("departure_prepositions", [])
    arrival_terms = prepositions.get("arrival_prepositions", [])
    
    for match_id, start, end in matches:
        if not nlp.vocab.strings[match_id] == "PREPOSITIONS":
            continue
        span = doc[start:end]
        departure = extract_station(departure, span.text.lower(), departure_terms)
        arrival = extract_station(arrival, span.text.lower(), arrival_terms)
    
    similar_stations = []
    
    for ent in doc.ents:
        if not (departure is None or arrival is None):
            continue
        if not ent.label_ == "PLACE":
            continue
        similar_stations.append(find_closest_stations(ent.text))
    
    return departure, arrival, similar_stations    


def extract_after_before(text: str) -> str:
    '''
    Extract the time from the text using regex.
    :param text: The input text to search for time.
    :return: The extracted time or None if not found.
    '''
    text = preprocess_time(text).upper()
    doc = nlp(text)
    text = lemmatize_text(doc).upper()
    doc = nlp(text)
    print(f"Pisces: Preprocessed Text: {text}")
    
    matches = type_matcher(doc)
    
    patterns = []
    
    for match_id, _, _ in matches:
        if not nlp.vocab.strings[match_id] in ["DEPARTING", "ARRIVING"]:
            continue
        patterns.append(nlp.vocab.strings[match_id])
    return patterns

setup()


if __name__ == "__main__":
    print("Pisces: Hello There, I am Pisces, your travel assistant. How can I help you today?")
    print("--" * 30)
    
    while True:
        user_input = input("You: ")
        departure, arrival, similar_stations = extract_train_info(user_input)
        journeys, date_time = extract_date_time(user_input)
        before_after = extract_after_before(user_input)
        print(f"Pisces: Departure: {departure}")
        print(f"Pisces: Arrival: {arrival}")
        print(f"Pisces: Similar Stations: {similar_stations}")
        print(f"Pisces: Journey Date: {journeys['DATE']}")
        print(f"Pisces: Journey Time: {journeys['TIME']}")
        print(f"Pisces: Date and Time: {date_time}")
        print(f"Pisces: Before/After: {before_after}")
        print("--" * 30)