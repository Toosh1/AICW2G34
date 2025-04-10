'''
Pisces: A Train Travel Assistant

To Do
- Check if station exists, if it does not, suggest the closest matches e.g.
    - Maidstone -> [Maidstone East, Maidstone West, Maidstone Barracks]
'''

import re
import spacy
from spacy.matcher import Matcher
from spellchecker import SpellChecker
from knowledge_base import station_codes, get_departure_arrival_patterns, get_prepositions

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
    stations_list = station_codes.keys()
    station_words = {token for station in stations_list for token in station.split()}
    spell.word_frequency.load_words(station_words)


def add_station_entity_ruler():
    '''
    Add a custom entity ruler to the spaCy pipeline for station names.
    :return: None
    '''
    ruler = nlp.add_pipe("entity_ruler", config={"overwrite_ents": True}, name="station_ruler", last=True)
    patterns = [{"label": "GPE", "pattern": station} for station in station_codes.keys()]
    ruler.add_patterns(patterns)


def add_matcher_patterns():
    '''
    Add custom patterns to the spaCy matcher for train routes.
    This includes departure and arrival patterns.
    The patterns are defined in the knowledge base.
    :return: None
    '''
    global matcher
    matcher = Matcher(nlp.vocab)
    matcher.add("TrainRoute", get_departure_arrival_patterns())
    
    # # Add custom patterns from responses
    # for intent, data in responses.items():
    #     # Convert each pattern into a Doc object using nlp.make_doc
    #     patterns = [nlp.make_doc(pattern) for pattern in data["patterns"]]
    #     matcher.add(intent, patterns)


def extract_train_info(user_input):
    '''
    Extract train information from the user input using spaCy's matcher.
    :param user_input: The input text from the user.
    :return: None
    '''
    # Process the input text with spaCy
    doc = nlp(user_input)
    
    # Apply the matcher to the document
    matches = matcher(doc)
    
    departure = None
    arrival = None
    
    prepositions = get_prepositions()
    
    departure_terms = prepositions.get("departure_prepositions", [])
    arrival_terms = prepositions.get("arrival_prepositions", [])
    
    for _, start, end in matches:
        span = doc[start:end]
        
        # Handle departure terms
        if departure is None:
            for term in departure_terms:
                if term not in span.text.lower():
                    continue
                departure = span.text.replace(term, "").strip()
                break
        
        # Handle arrival terms
        if arrival is None:
            for term in arrival_terms:
                if term not in span.text.lower():
                    continue
                arrival = span.text.replace(term, "").strip()
                break
    
    print(f"Departure: {departure}")
    print(f"Arrival: {arrival}")
    
    # I want to go from Maidstone East to Norwich

def preprocess_text(text):
    '''
    Preprocess the input text by normalizing it to lower case and removing special characters.
    :param text: The input text to preprocess.
    :return: The preprocessed text.'''
    
    # Normalize input text to lower case and remove special characters
    cleaned_text = text.lower()
    cleaned_text = re.sub(r"[^a-z0-9\s]", "", cleaned_text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
    
    tokens = cleaned_text.split()
    
        
    # Loop through tokens and correct spelling
    corrected_tokens = [spell.correction(token) for token in tokens]

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
        user_input = preprocess_text(user_input)
        extract_train_info(user_input)


if __name__ == "__main__":
    setup()
    main()
