import sys, os, pytest, spacy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.input_handler import *

nlp = spacy.load("en_core_web_sm")

@pytest.mark.parametrize("input_word, expected", [
    ("recieve", "receive"),
    ("teh", "the"),
])
def test_correct_spelling(input_word, expected) -> None:
    assert correct_spelling(input_word) == expected


@pytest.mark.parametrize("input_text, expected", [
    ("I recieve teh message", "i receive the message"),
    ("I am arriving at 9pm", "i be arrive at 9:00 am")
])
def test_preprocess_text_with_spell_check(input_text, expected) -> None:
    assert preprocess_text(input_text, nlp, True, True) == expected

@pytest.mark.parametrize("input_time, expected", [
    ("5pm", "5:00 PM"),
    ("5:30am", "5:30 AM"),
    ("17:45", "17:45"),
    ("9:00am", "9:00 AM"),
    ("9:00 pm", "9:00 PM"),
    ("09:00 am", "9:00 AM")
])
def test_format_time(input_time, expected) -> None:
    assert format_time(input_time) == expected


if __name__ == "__main__":
    pytest.main()