import spacy
import pandas as pd
from spacy.matcher import PhraseMatcher
from difflib import get_close_matches
import spellchecker
from datetime import datetime
from spacy.lang.en.stop_words import STOP_WORDS




def setup():
    global nlp, spell, matcher, cleaned_stations, stations_df
    nlp = spacy.load("en_core_web_sm")
    spell = spellchecker.SpellChecker()
    stations_df = pd.read_csv("src/data/csv/stations.csv")
    second_column = stations_df.iloc[:, 1]
    cleaned_stations = []

    for name in second_column:
        name = name.replace(" Rail Station", "").strip()
        name = name.replace("-", " ")
        name = name.replace("(", "").replace(")", "")
        name = name.lower()
        cleaned_stations.append(name)


    spell.word_frequency.load_words(cleaned_stations)
    matcher = PhraseMatcher(nlp.vocab)
    patterns = [nlp.make_doc(station) for station in cleaned_stations]
    matcher.add("STATION", patterns)

def correct_spelling(word):
    corrected_word = spell.correction(word)
    return corrected_word if corrected_word else word



def extract_time(sentence):
    doc = nlp(sentence)
    for ent in doc.ents:
        if ent.label_ == "TIME":
            try:
                return ent.text
            except ValueError:
                pass

    return None

def extract_single_station(sentence):
    sentence_corrected = " ".join(correct_spelling(word) for word in sentence.split())
    doc = nlp(sentence_corrected)

    matches = matcher(doc)
    detected_stations = {doc[start:end].text.lower() for _, start, end in matches}

    if detected_stations:
        return " ".join(detected_stations)

    return None


def find_stations(sentence):
    sentence_corrected = " ".join(correct_spelling(word) for word in sentence.split())
    doc = nlp(sentence_corrected)
    matches = matcher(doc)
    detected_stations = [doc[start:end].text.lower() for _, start, end in matches]
    detected_stations = sorted(detected_stations, key=len, reverse=True)

    from_station = None
    to_station = None
    close_stations =None
    
    sentence_lower = sentence_corrected.lower()
    for station in detected_stations[:]:
        if f"from {station}" in sentence_lower:
            from_station = station
            detected_stations.remove(station)
            sentence_lower = sentence_lower.replace(f"from {station}", "")
        elif f"to {station}" in sentence_lower:
            to_station = station
            detected_stations.remove(station)
            sentence_lower = sentence_lower.replace(f"to {station}", "")


    if (to_station is None) and (len(detected_stations) > 1):
        to_station = detected_stations[0]
        sentence_lower = sentence_lower.replace(to_station, "")

    elif (from_station is None) and (len(detected_stations) > 1):
        from_station = detected_stations[0]
        sentence_lower = sentence_lower.replace(from_station, "")

    
    if from_station is None or to_station is None:
        close_stations = find_closest_station(sentence_lower)

    return from_station, to_station, close_stations

def find_closest_station(sentence):
    sentence_corrected = " ".join(correct_spelling(word) for word in sentence.split())
    doc = nlp(sentence_corrected)

    filtered_words = [word for word in sentence_corrected.lower().split() if word not in STOP_WORDS]
    
    partial_matches = []
    for word in filtered_words:
        similair = [station for station in cleaned_stations if word in station]
        if similair != []:
            partial_matches = [word,similair[:5]]
    return partial_matches


def get_coded_stations(station):
    try:
        index = cleaned_stations.index(station)
        return stations_df.iloc[index, 3]
    except ValueError:
        return None




if __name__ == "__main__":
    setup()
    while True:
        sentence = input("Enter a sentence: ")
        print(find_stations(sentence))
