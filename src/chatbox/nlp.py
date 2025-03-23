import spacy
import pandas as pd
from spacy.matcher import PhraseMatcher
import spellchecker
from datetime import datetime

def setup():
    global nlp, spell, matcher, cleaned_stations, stations_df
    nlp = spacy.load("en_core_web_sm")
    spell = spellchecker.SpellChecker()

    stations_df = pd.read_csv("src/data/stations.csv")
    second_column = stations_df.iloc[:, 1]
    cleaned_stations = [name.replace(" Rail Station", "").strip().lower() for name in second_column]
    cleaned_stations_2 = [word for name in cleaned_stations for word in name.split()]
    spell.word_frequency.load_words(cleaned_stations_2)

    matcher = PhraseMatcher(nlp.vocab)
    patterns = [nlp.make_doc(station) for station in cleaned_stations]
    matcher.add("STATION", patterns)

def correct_spelling(word):
    corrected_word = spell.correction(word)
    return corrected_word if corrected_word else word


def extract_time(sentence):
    doc = nlp(sentence)
    for ent in doc.ents:
        print(ent.text, ent.label_)
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

    from_station = None
    to_station = None
    sentence_lower = sentence_corrected.lower()
    for station in detected_stations[:]:
        if f"from {station}" in sentence_lower:
            from_station = station
            detected_stations.remove(station)
        elif f"to {station}" in sentence_lower:
            to_station = station
            detected_stations.remove(station)


    if (from_station is None) and (len(detected_stations) > 1):
        from_station = detected_stations[0]

    if (to_station is None) and (len(detected_stations) > 1):
        to_station = detected_stations[0]


    return from_station, to_station


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
        print(extract_time(sentence))