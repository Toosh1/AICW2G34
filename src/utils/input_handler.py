import dateparser, re
from spellchecker import SpellChecker
from datetime import datetime

spell = SpellChecker()


def add_to_vocabulary(words: list) -> None:
    spell.word_frequency.load_words(words)


def correct_spelling(word: str) -> str:
    '''
    
    Correct the spelling of a word using the spell checker.
    :param word: The word to correct.
    :return: The corrected word.
    '''
    corrected_word = spell.correction(word)
    return corrected_word if corrected_word else word


def modify_tenses(doc: object) -> str:
    modified_tokens = []
    
    for token in doc:
        if token.text == "AT" and token.dep_ == "compound":
            modified_tokens.append("IN")
        else:
            modified_tokens.append(token.text)
    return " ".join(modified_tokens)

def preprocess_text(text: str, spell_check: bool = True) -> str:
    '''
    Preprocess the input text by normalizing it to lower case and removing special characters.
    :param text: The input text to preprocess.
    :return: The preprocessed text.
    '''
    # Normalize input text to lower case and remove special characters
    cleaned_text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

    tokens = cleaned_text.split()
    
    # Loop through tokens and correct spelling
    if spell_check:
        tokens = [correct_spelling(token.lower()) for token in tokens]
    
    text = " ".join(tokens).upper()
    
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
    time_str = re.sub(r'(\d{1,2}:\d{2})(am|pm)', r'\1 \2', time_str, flags=re.IGNORECASE)
    
    # Remove any 0s before the hour e.g 09:00am -> 9:00am
    time_str = re.sub(r'0(\d{1}:\d{2})', r'\1', time_str)
    
    # upper() any instances of "AM" or "PM"
    time_str = re.sub(r'(?<=\s)(am|pm)', lambda x: x.group(0).upper(), time_str, flags=re.IGNORECASE)

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


def parse_time(journey: dict[str, str]) -> str:
    '''
    Parse the time from the journey dictionary.
    :param journey: The dictionary containing the time information.
    :return: The parsed time in the format 'YYYY-MM-DD HH:MM:SS'.
    '''
    parsed_date = datetime.now()
    
    for key in journey.keys():
        for value in journey[key]:
            settings = {"PREFER_DATES_FROM": "future", "RELATIVE_BASE": parsed_date, "TIMEZONE": "GMT", "DATE_ORDER": "DMY"}
            result = dateparser.parse(value, settings=settings)
            if not result:
                continue
            parsed_date = result
    return parsed_date.strftime("%Y-%m-%d %H:%M:%S")