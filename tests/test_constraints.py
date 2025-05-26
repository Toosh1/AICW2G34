import sys, os, pytest, spacy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.chatbot.nlp import *

nlp = spacy.load("en_core_web_sm")

'''
Testing extracting if user wants to select "arriving before" or "departing after" a certain time.
'''
@pytest.mark.parametrize("text,expected_label", [
    ("I want to arrive by 10pm", ["arriving", "departing"]),
    ("I need to be there before 6pm", ["arriving", "departing"]),
    ("I'll depart at 4pm or later", ["departing", "departing"]),
    ("Be there by 2:15pm", ["arriving", "departing"]),
    ("Leaving at 7pm sharp", ["departing", "departing"]),
    ("I want to arrive before 5pm and I want to return after 6pm", ["arriving", "departing"]),
    ("I would like to leave maidstone east to london bridge by 10pm and return on the tuesday at 6am", ["departing", "departing"]),
    ("I need to arrive before 1pm and leave after 2pm", ["arriving", "departing"]),
    ("I want to arrive at 8am and depart at 10am", ["arriving", "departing"]),
])
def test_time_constraints(text: str, expected_label: list) -> None:
    text = preprocess_text(text, nlp, True, True)
    return_phrase = get_return_ticket(text)
    result = get_time_constraints(text, return_phrase)
    assert result == expected_label


if __name__ == "__main__":
    pytest.main()