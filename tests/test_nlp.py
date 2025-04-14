import sys, os, pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.chatbot.nlp import *


'''
Testing extracting if user wants to select "arriving before" or "departing after" a certain time.
Failed Test Cases:
    - ("Leaving after 9 in the morning", ["DEPARTING"]),
        - "9 in the morning" is not recognised as TIME entity
    - ("Arrive no later than 11:45am", ["ARRIVING"]),
        - "no later than" is not recognised in the matcher
'''
@pytest.mark.parametrize("text,expected_label", [
    ("I want to arrive by 10pm", ["ARRIVING"]),
    ("Reach London by 8:30", ["ARRIVING"]),
    ("I need to be there before 6pm", ["ARRIVING"]),
    ("I'll depart at 4pm or later", ["DEPARTING"]),
    ("Be there by 2:15pm", ["ARRIVING"]),
    ("Leaving at 7pm sharp", ["DEPARTING"]),
    ("I want to arrive before 5pm and I want to return after 6pm", ["ARRIVING", "DEPARTING"]),
    ("I would like to leave maidstone east to london bridge by 10pm and return on the tuesday at 6am", ["ARRIVING", "DEPARTING"]),
    ("Leaving after 9 in the morning", ["DEPARTING"]),
    ("I want to get there by 7pm and leave after 8pm", ["ARRIVING", "DEPARTING"]),
    ("Be there no later than 3pm and depart at 5pm", ["ARRIVING", "DEPARTING"]),
    ("Arriving at 10am and leaving at 4pm", ["ARRIVING", "DEPARTING"]),
    ("I need to arrive before 1pm and leave after 2pm", ["ARRIVING", "DEPARTING"]),
    ("I'll be arriving by 6pm and departing at 7pm", ["ARRIVING", "DEPARTING"]),
    ("Reach by 9am and leave by 11am", ["ARRIVING", "DEPARTING"]),
    ("I want to arrive at 8am and depart at 10am", ["ARRIVING", "DEPARTING"]),
    ("Arrive at noon and leave at 2pm", ["ARRIVING", "DEPARTING"]),
])
def test_extract_after_before(text: str, expected_label: str) -> None:
    result = extract_time_constraints(text)
    assert any(label in result for label in expected_label)


'''
Testing extracting date and time from the text.
'''
@pytest.mark.parametrize("text,expected_outbound,expected_inbound", [
    ("I'll travel on May 15th at 10am", {"DATE": ["May 15th"], "TIME": ["10:00 AM"]}, None),
    ("I want to go from Maidstone East to Norwich tomorrow and return on Friday at 5pm", {"DATE": ["tomorrow"], "TIME": []}, {"DATE": ["Friday"], "TIME": ["5:00 PM"]}),
    ("Leaving on June 1st at 8:30am and coming back on June 3rd at 6pm", {"DATE": ["June 1st"], "TIME": ["8:30 AM"]}, {"DATE": ["June 3rd"], "TIME": ["6:00 PM"]}),
    ("Departing next Monday at 9am and returning next Wednesday evening", {"DATE": ["next Monday"], "TIME": ["9:00 AM"]}, {"DATE": ["next Wednesday"], "TIME": ["evening"]}),
    ("I'll leave on the 20th at noon and come back on the 22nd at midnight", {"DATE": ["the 20th"], "TIME": ["noon"]}, {"DATE": ["the 22nd"], "TIME": ["midnight"]}),
    ("Traveling on July 4th at 7:15am and returning July 5th at 10pm", {"DATE": ["July 4th"], "TIME": ["7:15 AM"]}, {"DATE": ["July 5th"], "TIME": ["10:00 PM"]}),
    ("Outbound on March 10th at 3pm, inbound on March 12th at 11am", {"DATE": ["March 10th"], "TIME": ["3:00 PM"]}, {"DATE": ["March 12th"], "TIME": ["11:00 AM"]}),
    ("Going tomorrow morning and coming back tomorrow night", {"DATE": [], "TIME": ["tomorrow morning"]}, {"DATE": [], "TIME": ["tomorrow night"]}),
    ("I'll travel on the 1st of August at 5:45pm and return on the 3rd at 8am", {"DATE": ["the 1st of August"], "TIME": ["5:45 PM"]}, {"DATE": ["3rd"], "TIME": ["8:00 AM"]}),
    ("Leaving this Saturday at 2pm and returning next Tuesday at 4pm", {"DATE": ["this Saturday"], "TIME": ["2:00 PM"]}, {"DATE": ["next Tuesday"], "TIME": ["4:00 PM"]}),
    ("Next Tuesday I want to go to maidstone east from norwich and I will to return in 5 weeks", {"DATE": ["Next Tuesday"], "TIME": []}, {"DATE": ["5 weeks"], "TIME": []}),
])
def test_extract_date_time(text: str, expected_outbound: dict, expected_inbound: dict) -> None:
    return_variations = extract_return_ticket(text)
    outbound, inbound = extract_journey_times(text, return_variations)
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
    ("Departing from Sheffield to Leeds", ["sheffield", "leeds"]),
    ("Traveling from Newcastle to Durham", ["newcastle", "durham"]),
    ("I need to go from York to Doncaster", ["york", "doncaster"]),
    ("Leaving from Edinburgh to Glasgow", ["edinburgh", None]),
    ("I want to travel from Bath to Bristol", [None, None]),
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
