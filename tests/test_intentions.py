import sys, os, pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.chatbot.nlp import *

@pytest.mark.parametrize("text, expected_output", [
    ("are there train delayed?", ["train_delays"]),
    ("is the train running late to London?", ["train_delays"]),
    ("what is the status of my train?", ["train_delays"]),
    ("when does the train leave?", ["departure_times"]),
    ("what time is the next train to Cambridge?", ["departure_times"]),
    ("when does the train arrive at Oxford?", ["arrival_times"]),
    ("arrival schedule for train to Manchester", ["arrival_times"]),
    ("what is the route from London to Edinburgh?", ["route_details"]),
    ("show me the train route to Glasgow", ["route_details"]),
    ("which platform is the train to Bristol on?", ["station_faq", "platform_details"]),
    ("where is platform 3 at King's Cross?", ["station_faq", "platform_details"]),
    ("what is the address of Paddington station?", ["station_faq", "address_details"]),
    ("where is Liverpool Street located?", ["station_faq", "address_details"]),
    ("who operates the train to York?", ["station_faq", "train_operator"]),
    ("what is the operator for train 1234?", ["station_faq", "train_operator"]),
    ("when does the ticket office open at Victoria?", ["station_faq", "ticket_office_hours"]),
    ("ticket office hours for Birmingham New Street?", ["station_faq", "ticket_office_hours"]),
    ("is there a ticket machine at Euston?", ["station_faq", "ticket_machine"]),
    ("where can I find a ticket vending machine?", ["station_faq", "ticket_machine"]),
    ("where is the seated area at Clapham Junction?", ["station_faq", "seated_area"]),
    ("is there a seating area at Oxford?", ["station_faq", "seated_area"]),
    ("does King's Cross have a waiting room?", ["station_faq", "waiting_room"]),
    ("where is the waiting area at Liverpool Street?", ["station_faq", "waiting_room"]),
    ("where are the toilets at Paddington?", ["station_faq", "toilets"]),
    ("is there a restroom at Victoria?", ["station_faq", "toilets"]),
    ("does Maidstone East have baby changing facilities?", ["station_faq", "baby_changing"]),
    ("where is the baby changing room at Oxford?", ["station_faq", "baby_changing"]),
    ("is there wifi at King's Cross?", ["station_faq", "wifi"]),
    ("where can I find wifi at Birmingham?", ["station_faq", "wifi"]),
    ("is there ramp access at Liverpool Street?", ["station_faq", "ramp_access"]),
    ("where can I find accessible facilities at Oxford?", ["station_faq", "ramp_access"]),
    ("are there ticket gates at Euston?", ["station_faq", "ticket_gates"]),
    ("where can I find ticket barriers at Paddington?", ["station_faq", "ticket_gates"]),
    ("hello", ["greeting"]),
    ("hi there", ["greeting"]),
    ("yes please", ["confirmation"]),
    ("definitely", ["confirmation"]),
    ("no thanks", ["rejection"]),
    ("not really", ["rejection"]),
])
def test_get_intentions(text: str, expected_output: list) -> None:
    intent, _ = predict_classifier(text, intent_classifier)
    faq_intent, _ = predict_classifier(text, faq_classifier)
    
    if intent != expected_output[0]:
        assert False
    elif len(expected_output) > 1 and faq_intent != expected_output[1]:
        assert False
    assert True

if __name__ == "__main__":
    pytest.main()