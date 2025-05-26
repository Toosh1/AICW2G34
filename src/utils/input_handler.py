import dateparser, re
from spellchecker import SpellChecker
from datetime import datetime
from spacy.lang.en.stop_words import STOP_WORDS
from nltk.corpus import stopwords

spell = SpellChecker()
merged_stopwords = set(STOP_WORDS).union(set(stopwords.words("english")))


def add_to_vocabulary(words: list) -> None:
    """
    Add words to the spell checker vocabulary.
    :param words: The list of words to add.
    """
    spell.word_frequency.load_words(words)


def correct_spelling(word: str) -> str:
    """

    Correct the spelling of a word using the spell checker.
    :param word: The word to correct.
    :return: The corrected word.
    """
    corrected_word = spell.correction(word)
    return corrected_word if corrected_word else word


def correct_sentence(sentence: str) -> str:
    """
    Correct the spelling of a sentence using the spell checker.
    :param sentence: The sentence to correct.
    :return: The corrected sentence.
    """
    words = sentence.split()
    corrected_words = [correct_spelling(word) for word in words]
    return " ".join(corrected_words)


def lemmatize_text(doc: object) -> str:
    """
    Lemmatize the input text using spaCy.
    :param doc: The input text to lemmatize.
    :return: The lemmatized text.
    """
    lemmatized_tokens = [
        token.lemma_ if token.lemma_ != "-PRON-" else token.text for token in doc
    ]
    return " ".join(lemmatized_tokens)


def modify_tenses(doc: object) -> str:
    """
    Modify the tenses of the input text using spaCy.
    :param doc: The input text to modify.
    :return: The modified text.
    """
    modified_tokens = []

    for token in doc:
        if token.text == "AT" and token.dep_ == "compound":
            modified_tokens.append("IN")
        else:
            modified_tokens.append(token.text)
    return " ".join(modified_tokens)


def add_leading_zero(match: re.Match) -> str:
    """
    Add leading zero to the hour in the time string.
    :param match: The regex match object.
    :return: The time string with leading zero.
    """
    return f"{int(match.group(1)):02}:00{match.group(2)}"


def format_time(time_str: str) -> str:
    """
    Format the time string to a standard format.
    :param time_str: The input time string.
    :return: The formatted time string.
    """
    # Regex pattern to find times like '1am', '1pm', etc and convert them to '01:00am', '01:00pm'
    pattern = r"\b(1[0-2]|[1-9])\s*(am|pm)\b"
    time_str = re.sub(pattern, add_leading_zero, time_str)

    # Regex to remove any space between the time and the 'AM/PM'
    time_str = re.sub(r"(\d{1,2}:\d{2})(am|pm)", r"\1 \2", time_str, flags=re.IGNORECASE)
    
    # Remove any 0s before the hour e.g 09:00am -> 9:00am
    time_str = re.sub(r"0(\d{1}:\d{2})", r"\1", time_str)
    
    # Use upper() on any instances of "AM" or "PM"
    time_str = re.sub(r"(?<=\s)(am|pm)", lambda x: x.group(0).upper(), time_str, flags=re.IGNORECASE)
    
    # Remove any trailing zeros in the time string
    time_str = re.sub(r"(?<=\d{2}:\d{2}):00\b", "", time_str)
    
    return time_str


def preprocess_text(text: str, nlp: object, spell_check: bool = True, lemma: bool = False) -> str:
    """
    Preproces the input text for time, remove extra spaces and correct am/pm format.
    :param text: The input text to preprocess.
    :return: The preprocessed text.
    """
    cleaned_text = format_time(text)
    # Remove all symbols except for colon and period and comma
    cleaned_text = re.sub(r"[^a-zA-Z0-9\s:.,]", "", cleaned_text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

    if spell_check:
        cleaned_text = correct_sentence(cleaned_text)

    if lemma:
        doc = nlp(cleaned_text)
        cleaned_text = lemmatize_text(doc)

    return cleaned_text.lower()


def parse_datestring(date_string: str, current_date) -> str:
    settings = {
        "PREFER_DATES_FROM": "future",
        "RELATIVE_BASE": current_date,
        "TIMEZONE": "GMT",
        "DATE_ORDER": "DMY",
    }
    result = dateparser.parse(date_string, settings=settings)
    return result if result else current_date

def parse_journey_dict(journey_dict: dict, current_date) -> tuple:
    for key in journey_dict:
        for value in journey_dict[key]:
            current_date = parse_datestring(value, current_date)
    return current_date

def parse_journey_times(outbound: dict, inbound: dict) -> tuple:
    current_date = datetime.now()
    outbound_date = parse_journey_dict(outbound, current_date)
    
    if not inbound:
        return outbound_date, None

    inbound_date = parse_journey_dict(inbound, outbound_date)
    return outbound_date, inbound_date

def process_station_name(station_name: str, nlp) -> list:
    """
    Process the station name by removing special characters, numbers, and short words.
    :param station_name: The input station name to process.
    :return: The processed station name as a list of terms.
    """
    return [
        re.sub(r"[^a-zA-Z]", "", preprocess_text(token, nlp))
        for token in station_name.split()
        if len(token) > 2 and token.lower() not in merged_stopwords
    ]