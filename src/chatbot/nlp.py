"""
# Pisces: A Train Travel Assistant
## NOTE Current Assumptions
    - No railcards
    - Only 1 adult
    - No children
"""

import sys, os, re, spacy
from spacy.matcher import Matcher
from rapidfuzz import process
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Merge the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from chatbot.database import *
from chatbot.knowledge_base import *
from utils.input_handler import *

#region Setup the NLP pipeline ------

def create_pipeline() -> Pipeline:
    tfidf = TfidfVectorizer()
    logicistic_regression = LogisticRegression()
    
    return Pipeline([
        ("vectorizer", tfidf),
        ("classifier", logicistic_regression)
    ])

def setup() -> None:
    add_stations_to_vocab()
    add_to_vocabulary(get_dates())
    add_series_entity_ruler()
    add_station_entity_ruler()
    add_matcher_patterns()
    train_intent_classifier()
    train_constraint_classifier()
    train_faq_classifier()

def add_stations_to_vocab() -> None:
    """
    Add station names to the spaCy vocabulary for spell checking.
    :return: None
    """
    stations_list = [station.lower() for station in get_all_station_names()]
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

    stations = [station.upper() for station in get_all_station_names()]
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
    global preposition_matcher, return_matcher

    preposition_matcher = Matcher(nlp.vocab)
    return_matcher = Matcher(nlp.vocab)

    preposition_matcher.add("PREPOSITIONS", get_extraction_patterns(), greedy="LONGEST")
    return_matcher.add("RETURN", get_return_patterns(), greedy="LONGEST")

def train_intent_classifier() -> None:
    global intent_classifier
    training_sentences, intent_labels = get_intentions_training_data()
    intent_classifier.fit(training_sentences, intent_labels)

def train_constraint_classifier() -> None:
    global constraint_classifier
    training_sentences, constraint_labels = get_constraint_training_data()
    constraint_classifier.fit(training_sentences, constraint_labels)

def train_faq_classifier() -> None:
    global faq_classifier
    training_sentences, faq_labels = get_faq_training_data()
    faq_classifier.fit(training_sentences, faq_labels)

#endregion

#region Text Preprocessing Functions ------

def predict_classifier(text: str, classifier: Pipeline) -> tuple:
    """
    Predict the intent or constraint of the input text using the specified classifier.
    :param text: The input text to classify.
    :param classifier: The classifier to use for prediction.
    :return: A tuple containing the predicted label and its probability.
    """
    prediction = classifier.predict([text.lower()])
    probability = classifier.predict_proba([text])
    return str(prediction[0]), probability

def get_time_constraints(text: str, split_index: tuple) -> str:
    """
    Extract the time from the text using regex.
    :param text: The input text to search for time.
    :return: The extracted time or None if not found.
    """

    text = preprocess_text(text, nlp, True, True)
    variation, index = split_index
    split_text = [text[:index], text[index + len(variation):]] if variation else [text]
    constraints = ['departing', 'departing']

    # Loop through the split text and extract time constraints
    for i in range(len(split_text)):
        segment = split_text[i]
        constraint, confidence = predict_classifier(segment, constraint_classifier)
        constraints[i] = constraint if constraint else constraints[i]
    
    return constraints

def extract_date_and_time(text: str) -> dict:
    """
    Extract date and time from the text using spaCy's NER.
    :param text: The input text to search for date and time.
    :return: A dictionary containing date and time.
    """

    # Get the entities from the text
    doc = nlp(text)

    # Ignore if no entities are found

    journey = {"DATE": [], "TIME": []}

    for ent in doc.ents:
        if ent.label_ in TIME_ENTITIES:
            journey["DATE" if ent.label_ != "TIME" else "TIME"].append(ent.text)

    return journey

def get_journey_times(text: str, split_index: tuple) -> tuple:
    """
    Extract date and time from the text using regex.
    :param text: The input text to search for date and time.
    :param return_variations: List of return ticket variations.
    :return: A tuple containing date and time for first and second journeys.
    """

    variation, index = split_index
    split_text = [text[:index], text[index + len(variation):]] if variation else [text]

    journeys = []

    # Loop through the split text and extract date and time
    for segment in split_text:
        if journey := extract_date_and_time(segment):
            journeys.append(journey)

    return journeys[0] if journeys else None, journeys[1] if len(journeys) > 1 else None

def find_closest_stations(query: str) -> list:
    """
    Suggest the closest matching station names based on the query.
    :param query: The input query string
    :return: A list of similar station names
    """
    station_names = [station.lower() for station in get_all_station_names()]
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

def get_station_data(text: str) -> tuple:
    """
    Extract train information from the user input using spaCy's matcher.
    :param user_input: The input text from the user.
    :return: A tuple containing the departure and arrival stations and similar stations.
    """

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
        closest_stations = find_closest_stations(ent.text)
        similar_stations.append([ent.text, closest_stations])

    return departure, arrival, similar_stations

def extract_single_station(text: str) -> None:
    text = preprocess_text(text, nlp, True, True)
    text = preprocess_text(text, nlp, True, False).upper()
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "STATION":
            return ent.text
    return None

def extract_best_split_index(text: str, variations: list[str]) -> tuple[str, int]:
    best_variation = None
    best_index = None
    min_diff = float('inf')

    for variation in variations:
        # Use regex to find all case-insensitive matches of the variation
        for match in re.finditer(re.escape(variation), text, flags=re.IGNORECASE):
            index = match.start()

            # Split text at this instance
            left = text[:index]
            right = text[index + len(variation):]

            # Count time entities
            left_time_count = len([ent for ent in nlp(left).ents if ent.label_ in TIME_ENTITIES])
            right_time_count = len([ent for ent in nlp(right).ents if ent.label_ in TIME_ENTITIES])

            diff = abs(left_time_count - right_time_count)

            # Choose the split with the smallest time entity count difference
            if diff < min_diff:
                best_variation = variation
                best_index = index
                min_diff = diff

    if best_variation is not None:
        return best_variation, best_index

    return None, None

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
    return extract_best_split_index(text, variations)

#endregion

# Load spaCy's English model
nlp = spacy.load("en_core_web_sm")

intent_classifier = create_pipeline()
constraint_classifier = create_pipeline()
faq_classifier = create_pipeline()

preposition_matcher = None
return_matcher = None

TIME_ENTITIES = ["TIME", "DATE", "ORDINAL", "SERIES", "MONTH"]
departure_terms = get_prepositions("departure")
arrival_terms = get_prepositions("arrival")

setup()

if __name__ == "__main__":
    print("Pisces: Hello There, I am Pisces, your travel assistant. How can I help you today?")
    print("--" * 30)

    while True:
        user_input = input("You: ")
        intent, confidence = predict_classifier(user_input, intent_classifier)
        faq_intent, faq_confidence = predict_classifier(user_input, faq_classifier)
        split_index = get_return_ticket(user_input)
        departure, arrival, similar_stations = get_station_data(user_input)
        outbound, inbound = get_journey_times(user_input, split_index)
        time_constraints = get_time_constraints(user_input, split_index)
        outbound_date, inbound_date = parse_journey_times(outbound, inbound)
        print(f"Return Phrases: {split_index}")
        print(f"Departure: {departure}")
        print(f"Arrival: {arrival}")
        print(f"Similar Stations: {similar_stations}")
        print(f"Outbound: {outbound}")
        print(f"Inbound: {inbound}")
        print(f"Time Constraints: {time_constraints}")
        print(f"Inbound Date: {inbound_date}")
        print(f"Outbound Date: {outbound_date}")
        print(f"Intent: {intent}")
        print(f"Confidence: {confidence.max()}")
        if intent == "station_faq":
            print(f"FAQ Intent: {faq_intent}")
            print(f"FAQ Confidence: {faq_confidence.max()}")
        print("--" * 30)



