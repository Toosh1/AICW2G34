import sys, os, pytest, spacy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.chatbot.nlp import *

nlp = spacy.load("en_core_web_sm")

'''
Testing extracting if user wants to select "arriving before" or "departing after" a certain time.
'''
@pytest.mark.parametrize("text,expected_label", [
    ("I want to arrive by 10pm", ["ARRIVING", "DEPARTING"]),
    ("I need to be there before 6pm", ["ARRIVING", "DEPARTING"]),
    ("I'll depart at 4pm or later", ["DEPARTING", "DEPARTING"]),
    ("Be there by 2:15pm", ["ARRIVING", "DEPARTING"]),
    ("Leaving at 7pm sharp", ["DEPARTING", "DEPARTING"]),
    ("I want to arrive before 5pm and I want to return after 6pm", ["ARRIVING", "DEPARTING"]),
    ("I would like to leave maidstone east to london bridge by 10pm and return on the tuesday at 6am", ["DEPARTING", "DEPARTING"]),
    ("I want to get there by 7pm and leave after 8pm", ["ARRIVING", "DEPARTING"]),
    ("I need to arrive before 1pm and leave after 2pm", ["ARRIVING", "DEPARTING"]),
    ("Reach by 9am and leave by 11am", ["ARRIVING", "DEPARTING"]),
    ("I want to arrive at 8am and depart at 10am", ["ARRIVING", "DEPARTING"]),
    ("Arrive at noon and leave at 2pm", ["ARRIVING", "DEPARTING"]),
])
def test_time_constraints(text: str, expected_label: list) -> None:
    text = preprocess_text(text, nlp, True, True)
    return_phrase = get_return_ticket(text)
    departure, arrival, _ = get_station_data(text)
    result = get_time_constraints(text, return_phrase, departure, arrival)
    assert result == expected_label


'''
Testing extracting date and time from the text.
'''
@pytest.mark.parametrize("text,expected_outbound,expected_inbound", [
    ("I'll travel on May 15th at 10am", {"DATE": ["may 15th"], "TIME": ["10:00 am"]}, None),
    ("I want to go from Maidstone East to Norwich tomorrow and return on Friday at 5pm", {"DATE": ["tomorrow"], "TIME": []}, {"DATE": ["friday"], "TIME": ["5:00 pm"]}),
    ("Leaving on June 1st at 8:30am and coming back on June 3rd at 6pm", {"DATE": ["june 1st"], "TIME": ["8:30 am"]}, {"DATE": ["june 3rd"], "TIME": ["6:00 pm"]}),
    ("Departing next Monday at 9am and returning next Wednesday evening", {"DATE": ["next monday"], "TIME": ["9:00 am"]}, {"DATE": [], "TIME": ["next wednesday", "evening"]}),
    ("I'll leave on the 20th at noon and come back on the 22nd at midnight", {"DATE": ["the 20th"], "TIME": ["noon"]}, {"DATE": ["the 22nd"], "TIME": ["midnight"]}),
    ("Traveling on July 4th at 7:15am and returning July 5th at 10pm", {"DATE": ["july 4th"], "TIME": ["7:15 am"]}, {"DATE": ["july 5th"], "TIME": ["10:00 pm"]}),
    ("Outbound on March 10th at 3pm, inbound on March 12th at 11am", {"DATE": ["march 10th"], "TIME": ["3:00 pm"]}, {"DATE": ["march 12th"], "TIME": ["11:00 am"]}),
    ("Leaving this Saturday at 2pm and returning next Tuesday at 4pm", {"DATE": ["this saturday"], "TIME": ["2:00 pm"]}, {"DATE": ["next tuesday"], "TIME": ["4:00 pm"]}),
    ("Next Tuesday I want to go to maidstone east from norwich and I will to return in 5 weeks", {"DATE": ["next tuesday"], "TIME": []}, {"DATE": ["5 week"], "TIME": []}),
])
def test_get_date_time(text: str, expected_outbound: dict, expected_inbound: dict) -> None:
    text = preprocess_text(text, nlp, True, True)
    return_phrase = get_return_ticket(text)
    outbound, inbound = get_journey_times(text, return_phrase)
    if expected_outbound is not None:
        assert outbound["DATE"] == expected_outbound["DATE"]
        assert outbound["TIME"] == expected_outbound["TIME"]
    if expected_inbound is not None:
        assert inbound["DATE"] == expected_inbound["DATE"]
        assert inbound["TIME"] == expected_inbound["TIME"]


'''
Testing extracting departing and arriving stations from the text.
Will return none if an exact match is not found.
'''
@pytest.mark.parametrize("text,expected_dep_arr", [
    ("I want to travel from Cambridge to Maidstone East", ["cambridge", "maidstone east"]),
    ("Departing from Oxford to Brighton", ["oxford", "brighton"]),
    ("Travel from Manchester to Liverpool", [None, None]),
    ("I need to get from Oxford to Birmingham", ["oxford", None]),
    ("I want to depart Norwich towards Maidstone East", ["norwich", "maidstone east"]),
    ("I want to get out of Norwich and leave for Maidstone East", ["norwich", "maidstone east"]),
    ("Heading from Cambridge to Peterborough", ["cambridge", "peterborough"]),
    ("Traveling from Newcastle to Durham", ["newcastle", "durham"]),
    ("I need to go from York to Doncaster", ["york", "doncaster"]),
    ("Leaving from Edinburgh to Glasgow", ["edinburgh", None]),
    ("I want to travel from Bath to Bristol", [None, None]),
])
def test_get_station_data_basic(text, expected_dep_arr):
    text = preprocess_text(text, nlp, True, True).upper()
    dep, arr, _ = get_station_data(text)
    assert dep == expected_dep_arr[0]
    assert arr == expected_dep_arr[1]


@pytest.mark.parametrize("query,expected_stations", [
    ("london", ['hampton london', 'lee london', 'london cannon street']),
    ("cambridge", ['cambridge', 'cambridge heath', 'cambridge north']),
])
def test_find_closest_stations(query, expected_stations):
    results = find_closest_stations(query)
    assert any(expected_station in results for expected_station in expected_stations)



if __name__ == "__main__":
    pytest.main()
