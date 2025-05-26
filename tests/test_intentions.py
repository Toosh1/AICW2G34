import sys, os, pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.chatbot.nlp import *

@pytest.mark.parametrize("text, expected_output", [
    # train_delays intent
    ("are there train delayed?", ["train_delays"]),
    ("is the train running late to London?", ["train_delays"]),
    ("what is the status of my train?", ["train_delays"]),

    # departure_times intent
    ("when does the train leave?", ["departure_times"]),
    ("what time is the next train to Cambridge?", ["departure_times"]),

    # arrival_times intent
    ("when does the train arrive at Oxford?", ["arrival_times"]),
    ("arrival schedule for train to Manchester", ["arrival_times"]),

    # route_details intent
    ("what is the route from London to Edinburgh?", ["route_details"]),
    ("show me the train route to Glasgow", ["route_details"]),

    # platform_details intent (with station_faq)
    ("which platform is the train to Bristol on?", ["station_faq", "platform_details"]),
    ("where is platform 3 at King's Cross?", ["station_faq", "platform_details"]),

    # address_details intent (with station_faq)
    ("what is the address of Paddington station?", ["station_faq", "address_details"]),
    ("where is Liverpool Street located?", ["station_faq", "address_details"]),

    # train_operator intent (with station_faq)
    ("who operates the train to York?", ["station_faq", "train_operator"]),
    ("what is the operator for train 1234?", ["station_faq", "train_operator"]),

    # ticket_office_hours intent (with station_faq)
    ("when does the ticket office open at Victoria?", ["station_faq", "ticket_office_hours"]),
    ("ticket office hours for Birmingham New Street?", ["station_faq", "ticket_office_hours"]),

    # ticket_machine intent (with station_faq)
    ("is there a ticket machine at Euston?", ["station_faq", "ticket_machine"]),
    ("where can I find a ticket vending machine?", ["station_faq", "ticket_machine"]),

    # seated_area intent (with station_faq)
    ("where is the seated area at Clapham Junction?", ["station_faq", "seated_area"]),
    ("is there a seating area at Oxford?", ["station_faq", "seated_area"]),

    # waiting_room intent (with station_faq)
    ("does King's Cross have a waiting room?", ["station_faq", "waiting_room"]),
    ("where is the waiting area at Liverpool Street?", ["station_faq", "waiting_room"]),

    # toilets intent (with station_faq)
    ("where are the toilets at Paddington?", ["station_faq", "toilets"]),
    ("is there a restroom at Victoria?", ["station_faq", "toilets"]),

    # baby_changing intent (with station_faq)
    ("does Maidstone East have baby changing facilities?", ["station_faq", "baby_changing"]),
    ("where is the baby changing room at Oxford?", ["station_faq", "baby_changing"]),

    # wifi intent (with station_faq)
    ("is there wifi at King's Cross?", ["station_faq", "wifi"]),
    ("where can I find wifi at Birmingham?", ["station_faq", "wifi"]),

    # ramp_access intent (with station_faq)
    ("is there ramp access at Liverpool Street?", ["station_faq", "ramp_access"]),
    ("where can I find accessible facilities at Oxford?", ["station_faq", "ramp_access"]),

    # ticket_gates intent (with station_faq)
    ("are there ticket gates at Euston?", ["station_faq", "ticket_gates"]),
    ("where can I find ticket barriers at Paddington?", ["station_faq", "ticket_gates"]),

    # greeting
    ("hello", ["greeting"]),
    ("hi there", ["greeting"]),

    # confirmation
    ("yes please", ["confirmation"]),
    ("definitely", ["confirmation"]),

    # rejection
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