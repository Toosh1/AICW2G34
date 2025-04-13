import sys, os, pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.chatbot.nlp import *


@pytest.mark.parametrize("text,expected_label", [
    ("I want to arrive by 10pm", ["ARRIVING"]),
    ("I'll leave after 7am", ["DEPARTING"]),
    ("Departing at 5pm or later", ["DEPARTING"]),
    ("Reach London by 8:30", ["ARRIVING"]),
])
def test_extract_after_before(text: str, expected_label: str) -> None:
    result = extract_after_before(text)
    assert any(label in result for label in expected_label)


@pytest.mark.parametrize("text,expected_date,expected_time", [
    ("I'll travel on the 15th of May at 10am", ["the 15th", "may"], ["10:00 AM"]),
    ("Book for tomorrow at 3:30pm", ["tomorrow"], ["3:30 PM"]),
    ("On the 2nd at 8 in the morning", ["the 2nd"], ["8 in the morning"]),
])
def test_extract_date_time(text: str, expected_date: str, expected_time: str) -> None:
    journeys, _ = extract_date_time(text)
    assert journeys["DATE"] == expected_date
    assert journeys["TIME"] == expected_time


@pytest.mark.parametrize("text,expected_dep_arr", [
    ("I want to travel from Cambridge to Maidstone East", ["cambridge", "maidstone east"]),
    ("Departing from London Bridge to Brighton", ["london bridge", "brighton"]),
    ("Travel from Manchester to Liverpool", [None, None]),
    ("I need to get from Oxford to Birmingham", ["oxford", None]),
    ("I want to depart Norwich towards Maidstone East", ["norwich", "maidstone east"]),
    ("I want to get out of Norwich and leave for Maidstone East", ["norwich", "maidstone east"]),
])
def test_extract_train_info_basic(text, expected_dep_arr):
    dep, arr, _ = extract_train_info(text)
    dep = dep.lower() if dep else None
    arr = arr.lower() if arr else None
    expected_dep_arr = [val.lower() if val else None for val in expected_dep_arr]
    assert dep == expected_dep_arr[0]
    assert arr == expected_dep_arr[1]


@pytest.mark.parametrize("query,expected_stations", [
    ("london", ['battersea park london', 'blackfriars london', 'camden road london']),
    ("cambridge", ['cambridge', 'cambridge heath', 'cambridge north']),
])
def test_find_closest_stations(query, expected_stations):
    results = find_closest_stations(query)
    assert any(expected_station in results for expected_station in expected_stations)



if __name__ == "__main__":
    pytest.main()
