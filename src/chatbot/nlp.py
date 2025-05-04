"""
# Pisces: A Train Travel Assistant

## Checklist
- Extract Date and Time [✔]
    - Get to_train date and time and return_train date and time […]
    - TODO Assume Date = TODAY and Time = NOW for the outbound journey if not found

## NOTE Limitation of `get_journey_times`
    - Assumes first instance of date and time is the outbound journey and the second instance is the return journey
        - This won't work if the user only enters the date and time for the return journey
## NOTE Current Assumptions
    - No railcards
    - Only 1 adult
    - No children
"""

import sys, os, re, spacy
from spacy.matcher import Matcher
from rapidfuzz import process

# Merge the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chatbot.database import *
from utils.input_handler import *

# Load spaCy's English model
nlp = spacy.load("en_core_web_sm")
preposition_matcher = None
constraint_matcher = None
return_matcher = None

TIME_ENTITIES = ["TIME", "DATE", "ORDINAL", "SERIES", "MONTH"]
TIME_CONSTRAINTS = ["DEPARTING", "ARRIVING"]
departure_terms = get_prepositions("departure")
arrival_terms = get_prepositions("arrival")

def setup() -> None:
    add_stations_to_vocab()
    add_to_vocabulary(get_dates())
    add_series_entity_ruler()
    add_station_entity_ruler()
    add_matcher_patterns()

def add_stations_to_vocab() -> None:
    """
    Add station names to the spaCy vocabulary for spell checking.
    :return: None
    """
    stations_list = [station.lower() for station in station_codes.keys()]
    station_words = {token for station in stations_list for token in station.split()}
    add_to_vocabulary(station_words)
    add_to_vocabulary(stations_list)

def add_station_entity_ruler() -> None:
    """
    Add a custom entity ruler to the spaCy pipeline for station names.
    :return: None
    """
    ruler = nlp.add_pipe(
        "entity_ruler",
        config={"overwrite_ents": True},
        name="station_ruler",
        after="ner",
    )


    stations = [station.upper() for station in station_codes.keys()]
    places = {processed.upper() for station in stations for processed in process_station_name(station, nlp)}

    # Remove any overlapping names
    places = places.difference(stations)

    station_patterns = [{"label": "STATION", "pattern": station.upper()} for station in stations]
    place_patterns = [{"label": "PLACE", "pattern": place.upper()} for place in places]

    ruler.add_patterns(station_patterns)
    ruler.add_patterns(place_patterns)

def add_series_entity_ruler() -> None:
    """
    Add a custom entity ruler to the spaCy pipeline for series names.
    :return: None
    """
    ruler = nlp.add_pipe("entity_ruler", name="series_ruler", before="ner")
    series_pattern = [{"label": "SERIES", "pattern": get_next_series_patterns()}]
    ruler.add_patterns(series_pattern)

    ruler = nlp.add_pipe("entity_ruler", name="month_ruler", after="ner")
    month_pattern = [{"label": "MONTH", "pattern": get_month_patterns()}]
    ruler.add_patterns(month_pattern)

def add_matcher_patterns() -> None:
    """
    Add custom patterns to the spaCy matcher for train routes.
    This includes departure and arrival patterns.
    The patterns are defined in the knowledge base.
    :return: None
    """
    global constraint_matcher, preposition_matcher, return_matcher

    constraint_matcher = Matcher(nlp.vocab)
    preposition_matcher = Matcher(nlp.vocab)
    return_matcher = Matcher(nlp.vocab)

    preposition_matcher.add("PREPOSITIONS", get_extraction_patterns(), greedy="LONGEST")
    constraint_matcher.add("GENERAL", [get_default_time_constraint()], greedy="LONGEST")
    constraint_matcher.add("DEPARTING", get_depart_after_patterns(), greedy="LONGEST")
    constraint_matcher.add("ARRIVING", get_arrive_before_patterns(), greedy="LONGEST")
    return_matcher.add("RETURN", get_return_patterns(), greedy="LONGEST")

def extract_split_term(text: str, variations: list) -> str:
    return min(
        variations,
        key=lambda variation: abs(
            len([ent for ent in nlp(text.split(variation)[0]).ents if ent.label_ in TIME_ENTITIES]) -
            len([ent for ent in nlp(text.split(variation)[1]).ents if ent.label_ in TIME_ENTITIES])
        ),
        default=None
    )

def extract_date_and_time(text: str) -> dict:
    """
    Extract date and time from the text using spaCy's NER.
    :param text: The input text to search for date and time.
    :return: A dictionary containing date and time.
    """

    # Get the entities from the text
    doc = nlp(text)

    # Ignore if no entities are found
    if not doc.ents:
        return None

    journey = {"DATE": [], "TIME": []}

    for ent in doc.ents:
        if ent.label_ in TIME_ENTITIES:
            journey["DATE" if ent.label_ != "TIME" else "TIME"].append(ent.text)

    return journey

def extract_time_constraints(text: str, departure: str, arrival: str) -> str:
    doc = nlp(text)
    matches = constraint_matcher(doc)

    patterns = [nlp.vocab.strings[match_id] for match_id, _, _ in matches if nlp.vocab.strings[match_id] in TIME_CONSTRAINTS]

    if len(patterns) > 0:
        return patterns

    # Check for matches
    if not matches:
        return None

    # If the departing station is found in the text, return "DEPART"
    if departure is not None and departure in text:
        return ["DEPARTING"]

    # If the arrival station is found in the text, return "ARRIVE"
    if arrival is not None and arrival in text:
        return ["ARRIVING"]

    return ["DEPARTING"]

def find_closest_stations(query: str) -> list:
    """
    Suggest the closest matching station names based on the query.
    :param query: The input query string
    :return: A list of similar station names
    """
    station_names = [station.lower() for station in station_codes.keys()]
    similar_stations = process.extract(query.lower(), station_names, limit=3)
    return [station[0] for station in similar_stations]

def extract_station(type: str, text: str, terms: list) -> str:
    """
    Extract the station name from the text using regex.
    :param type: The type of station (departure or arrival).
    :param text: The input text to search for the station name.
    :param terms: The list of terms to search for.
    :return: The extracted station name or None if not found.
    """
    # Return station name if already found
    if not (type is None):
        return type

    for term in terms:
        match = re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE)
        if match:
            return re.sub(rf"\b{re.escape(term)}\b", "", text, count=1, flags=re.IGNORECASE).strip()
    return None

def get_time_constraints(text: str, return_phrase: str, departure: str, arrival: str) -> str:
    """
    Extract the time from the text using regex.
    :param text: The input text to search for time.
    :return: The extracted time or None if not found.
    """

    text = preprocess_text(text, nlp, True, True)
    split_text = text.split(return_phrase) if return_phrase else [text]

    # Loop through the split text and extract time constraints
    constraints = []
    for segment in split_text:
        if constraint := extract_time_constraints(segment, departure, arrival):
            constraints.extend(constraint)
    constraints = [c for c in constraints if c is not None]

    constraints.extend(["DEPARTING", "DEPARTING"])
    constraints = constraints[:2]

    return constraints

def get_journey_times(text: str, return_phase: str, departure: str, arrival: str) -> tuple:
    """
    Extract date and time from the text using regex.
    :param text: The input text to search for date and time.
    :param return_variations: List of return ticket variations.
    :return: A tuple containing date and time for first and second journeys.
    """

    split_text = text.split(return_phase) if return_phase else [text]

    journeys = []

    # Loop through the split text and extract date and time
    for segment in split_text:
        if journey := extract_date_and_time(segment):
            journeys.append(journey)

    return journeys[0] if journeys else None, journeys[1] if len(journeys) > 1 else None

def get_station_data(text: str) -> tuple:
    """
    Extract train information from the user input using spaCy's matcher.
    :param user_input: The input text from the user.
    :return: A tuple containing the departure and arrival stations and similar stations.
    """

    text = preprocess_text(text, nlp, True, True)
    text = preprocess_text(text, nlp, True, False).upper()
    doc = nlp(text)
    
    # Modify the text, based off the tense of the text and re-process
    text = modify_tenses(doc)
    doc = nlp(text)

    # Apply the matcher to the document
    matches = preposition_matcher(doc)
    departure = None
    arrival = None

    for _, start, end in matches:
        span = doc[start:end]
        departure = extract_station(departure, span.text.lower(), departure_terms)
        arrival = extract_station(arrival, span.text.lower(), arrival_terms)

    similar_stations = []
    
    for ent in doc.ents:
        if not (departure is None or arrival is None):
            continue
        if not ent.label_ == "PLACE":
            continue
        similar_stations.extend(find_closest_stations(ent.text))

    return departure, arrival, similar_stations

def get_return_ticket(text: str) -> str:
    """
    Extract if the user is looking for a return ticket.
    :param text: The input text to search for return ticket.
    :return: True if a return ticket is found, False otherwise.
    """

    text = preprocess_text(text, nlp, True, True)
    doc = nlp(text)
    matches = return_matcher(doc)
    variations = [doc[start:end].text.lower() for _, start, end in matches]
    return extract_split_term(text, variations)

setup()

if __name__ == "__main__":
    print("Pisces: Hello There, I am Pisces, your travel assistant. How can I help you today?")
    print("--" * 30)

    while True:
        user_input = input("You: ")
        return_phrase = get_return_ticket(user_input)
        departure, arrival, similar_stations = get_station_data(user_input)
        outbound, inbound = get_journey_times(user_input, return_phrase, departure, arrival)
        time_constraints = get_time_constraints(user_input, return_phrase, departure, arrival)
        print(f"Return Phrases: {return_phrase}")
        print(f"Departure: {departure}")
        print(f"Arrival: {arrival}")
        print(f"Similar Stations: {similar_stations}")
        print(f"Outbound: {outbound}")
        print(f"Inbound: {inbound}")
        print(f"Time Constraints: {time_constraints}")
        print("--" * 30)