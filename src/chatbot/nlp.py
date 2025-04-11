'''
Pisces: A Train Travel Assistant

To Do
- Get return journey
    - Get travel date
    - Get return date
- Get number of passengers
    - Get number of adults
    - Get number of children
- Get number of railcards
    - Get type of railcard
'''

import re
import spacy
import dateparser
from spacy.matcher import Matcher
from spellchecker import SpellChecker
from rapidfuzz import process
from database import *
from datetime import datetime

# Load spaCy's English model
nlp = spacy.load("en_core_web_sm")
spell = SpellChecker()
matcher = None


def setup():
    add_stations_to_vocab()
    add_series_entity_ruler()
    add_station_entity_ruler()
    add_matcher_patterns()

    # Load the custom knowledge base
    spell.word_frequency.load_words(station_codes.keys())


def add_stations_to_vocab():
    '''
    Add station names to the spaCy vocabulary for spell checking.
    :return: None
    '''
    stations_list = station_codes.keys()
    station_words = {token for station in stations_list for token in station.split()}
    spell.word_frequency.load_words(station_words)


def add_station_entity_ruler():
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


def add_series_entity_ruler():
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


def add_matcher_patterns():
    '''
    Add custom patterns to the spaCy matcher for train routes.
    This includes departure and arrival patterns.
    The patterns are defined in the knowledge base.
    :return: None
    '''
    global matcher
    matcher = Matcher(nlp.vocab)
    matcher.add("PREPOSITIONS", get_extraction_patterns(), greedy="LONGEST")


def preprocess_text(text: str, spell_check: bool =True):
    '''
    Preprocess the input text by normalizing it to lower case and removing special characters.
    :param text: The input text to preprocess.
    :return: The preprocessed text.
    '''
    # Normalize input text to lower case and remove special characters
    cleaned_text = re.sub(r"[^a-z0-9\s]", "", text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
    
    tokens = cleaned_text.split()
    
    # Loop through tokens and correct spelling
    if spell_check:
        # Correct spelling of tokens
        tokens = [correct_spelling(token) for token in tokens]
    
    # Apply lemmatization
    corrected_tokens = [token.lemma_ for token in nlp(" ".join(tokens))]
        
    text = " ".join(corrected_tokens).upper()
    
    return text


def add_leading_zero(match: re.Match) -> str:
    '''
    Add leading zero to the hour in the time string.
    :param match: The regex match object.
    :return: The time string with leading zero.
    '''
    return f'{int(match.group(1)):02}:00{match.group(2)}'
    

def format_time(time_str: str) -> str:
    '''
    Format the time string to a standard format.
    :param time_str: The input time string.
    :return: The formatted time string.
    '''
    
    # Regex pattern to find times like '1am', '1pm', etc and convert them to '01:00am', '01:00pm'
    pattern = r'(?<=\b)(\d{1})(am|pm)\b'
    time_str = re.sub(pattern, add_leading_zero, time_str)
    
    # Regex to remove any space between the time and the 'AM/PM'
    time_str = re.sub(r'(\d{2}:\d{2})(am|pm)', r'\1 \2', time_str, flags=re.IGNORECASE)

    return time_str


def preprocess_time(text: str) -> str:
    '''
    Preproces the input text for time, remove extra spaces and correct am/pm format.
    :param text: The input text to preprocess.
    :return: The preprocessed text.
    '''
    cleaned_text = text.capitalize()
    
    cleaned_text = format_time(cleaned_text)
    
    return cleaned_text


def extract_passengers(text: str) -> list:
    text = preprocess_text(text)
    adults = None
    children = None
    return []


def parse_time(journey: dict[str, str]) -> str:
    parsed_date = datetime.now()
    
    for key in journey.keys():
        for value in journey[key]:
            settings = {"PREFER_DATES_FROM": "future", "RELATIVE_BASE": parsed_date, "TIMEZONE": "GMT", "DATE_ORDER": "DMY"}
            result = dateparser.parse(value, settings=settings)
            if not result:
                continue
            parsed_date = result
    return parsed_date


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
    
    print(text)
    
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

    time = parse_time(journeys)
    print(f"Parsed time: {time}")
    
    return journeys


def correct_spelling(word) -> str:
    '''
    Correct the spelling of a word using the spell checker.
    :param word: The word to correct.
    :return: The corrected word.
    '''
    corrected_word = spell.correction(word)
    return corrected_word if corrected_word else word


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
    
    text = preprocess_text(text)
    doc = nlp(text)
    # Apply the matcher to the document
    matches = matcher(doc)
    
    departure = None
    arrival = None
    
    prepositions = get_prepositions()
    
    departure_terms = prepositions.get("departure_prepositions", [])
    arrival_terms = prepositions.get("arrival_prepositions", [])
    
    for _, start, end in matches:
        span = doc[start:end]
        departure = extract_station(departure, span.text.lower(), departure_terms)
        arrival = extract_station(arrival, span.text.lower(), arrival_terms)
        
    similar_stations = [find_closest_stations(ent.text) for ent in doc.ents if ent.label_ == "PLACE"]
    
    return departure, arrival, similar_stations    


def main():
    '''
    Main function to run the chatbot.
    It initializes the chatbot and handles user input.
    :return: None
    '''
    print("Pisces: Hello There, I am Pisces, your travel assistant. How can I help you today?")
    print("--" * 30)
    
    while True:
        user_input = input("You: ")
        departure, arrival, similar_stations = extract_train_info(user_input)
        journeys = extract_date_time(user_input)
        print(f"Journeys: {journeys}")
        print("--" * 30)


if __name__ == "__main__":
    setup()
    main()
