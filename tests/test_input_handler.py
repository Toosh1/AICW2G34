import sys, os, pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.input_handler import *


@pytest.mark.parametrize("input_word, expected", [
    ("recieve", "receive"),
    ("teh", "the"),
])
def test_correct_spelling(input_word, expected) -> None:
    assert correct_spelling(input_word) == expected


@pytest.mark.parametrize("input_text, expected", [
    ("hello!!!  world...", "HELLO WORLD"),
])
def test_preprocess_text_with_spell_check(input_text, expected) -> None:
    assert preprocess_text(input_text) == expected


@pytest.mark.parametrize("input_text, expected", [
    ("hello!!!  world...", "HELLO WORLD"),
])
def test_preprocess_text_without_spell_check(input_text, expected) -> None:
    assert preprocess_text(input_text, spell_check=False) == expected


@pytest.mark.parametrize("input_time, expected", [
    ("5pm", "5:00 PM"),
    ("10:30am", "10:30 AM"),
    ("17:45", "17:45")
])
def test_preprocess_time(input_time, expected) -> None:
    assert preprocess_time(input_time) == expected


@pytest.mark.parametrize("journey, expected_substring", [
    ({"departure": ["15th May 2025 at 10:30pm"]}, "2025-05-15 22:30"),
    ({"departure": ["1st Jan 2023 at 12:00am"]}, "2023-01-01 00:00")
])
def test_parse_time(journey, expected_substring) -> None:
    result = parse_time(journey)
    assert expected_substring in result  # allows time variance by seconds


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