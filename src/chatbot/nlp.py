'''
Pisces: A Train Travel Assistant

To Do
- Get is return?
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
from database import station_codes, get_extraction_patterns, get_prepositions

# Load spaCy's English model
nlp = spacy.load("en_core_web_sm")
spell = SpellChecker()
matcher = None


def setup():
    add_stations_to_vocab()
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
    ruler = nlp.add_pipe("entity_ruler", config={"overwrite_ents": True}, name="station_ruler", before="ner")
    
    stations = list(station_codes.keys())
    # Remove any overlapping names
    places = {station.split(" ")[0] for station in stations} - set(stations)

    station_patterns = [{"label": "STATION", "pattern": station} for station in stations]
    place_patterns = [{"label": "PLACE", "pattern": place} for place in places]
    
    ruler.add_patterns(station_patterns)
    ruler.add_patterns(place_patterns)        


def add_matcher_patterns():
    '''
    Add custom patterns to the spaCy matcher for train routes.
    This includes departure and arrival patterns.
    The patterns are defined in the knowledge base.
    :return: None
    '''
    global matcher
    matcher = Matcher(nlp.vocab)
    matcher.add("TrainRoute", get_extraction_patterns(), greedy="LONGEST")


def extract_date_time(text: str) -> str:
    '''
    Extract date and time from the text using regex.
    :param text: The input text to search for date and time.
    :return: The extracted date and time or None if not found.
    '''
    
    text = preprocess_text(text, False)
    text_result = dateparser.parse(text)
    return text_result


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
    station_names = list(station_codes.keys())
    similar_stations = process.extract(query, station_names, limit=3)
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


def preprocess_text(text, spell_check=True):
    '''
    Preprocess the input text by normalizing it to lower case and removing special characters.
    :param text: The input text to preprocess.
    :return: The preprocessed text.
    '''
    
    # Normalize input text to lower case and remove special characters
    cleaned_text = text.lower()
    cleaned_text = re.sub(r"[^a-z0-9\s]", "", cleaned_text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
    
    tokens = cleaned_text.split()
    
    # Loop through tokens and correct spelling
    if spell_check:
        # Correct spelling of tokens
        tokens = [correct_spelling(token) for token in tokens]
    
    # Apply lemmatization
    corrected_tokens = [token.lemma_ for token in nlp(" ".join(tokens))]
        
    text = " ".join(corrected_tokens)
    
    return text


def main():
    '''
    Main function to run the chatbot.
    It initializes the chatbot and handles user input.
    :return: None
    '''
    print("Pisces: Hello There, I am Pisces, your travel assistant. How can I help you today?")
    
    while True:
        user_input = input("You: ")
        print("--" * 30)
        departure, arrival, similar_stations = extract_train_info(user_input)
        extract_date_time(user_input)


if __name__ == "__main__":
    setup()
    main()
