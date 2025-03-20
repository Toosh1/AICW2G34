import spacy
import pandas as pd
from spacy.matcher import PhraseMatcher
import spellchecker


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

def extract_stations(sentence):
    sentence_corrected = ""
    for word in sentence.split():
        sentence_corrected += correct_spelling(word) + " "
    doc = nlp(sentence_corrected)

    from_station, to_station = None, None
    matches = matcher(doc)
    detected_stations = {doc[start:end].text.lower() for _, start, end in matches}

    tokens = [token.text.lower() for token in doc]
    detected_stations = {correct_spelling(station) for station in detected_stations}

    if "from" in tokens:
        idx = tokens.index("from") + 1
        for station in detected_stations:
            if station.lower().startswith(doc[idx].text.lower()):
                from_station = station

    if "to" in tokens:
        idx = tokens.index("to") + 1
        for station in detected_stations:
            if station.lower().startswith(doc[idx].text.lower()):
                to_station = station

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
        from_station, to_station = extract_stations(sentence)
        print(f"From: {from_station}, To: {to_station}")
        print(f"From: {get_coded_stations(from_station)}, To: {get_coded_stations(to_station)}")