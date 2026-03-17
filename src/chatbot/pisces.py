from datetime import datetime
from llama_cpp import Llama
from dotenv import load_dotenv
import prediction_model
import os, nlp, journey_planner, knowledge_base, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.input_handler import *
from utils.train_ticket_handler import *
from prompts import *

load_dotenv()
llm = Llama(model_path=os.getenv("LLAMA_PATH"), verbose=False)


current_requirements = []
request = ""
info = {}
current_stage = "waiting"

# --- Prompt Builders ---


def hello_prompt_builder():
    return {
        "role": "system",
        "content": "You are a railway assistant helping a user book a ticket. Just greet the user."
    }
messages = [hello_prompt_builder()]



# --- LLM ---

def llm_generate():
    print("GENERATED")
    chat_question = llm.create_chat_completion(messages)
    llm_response = chat_question["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": llm_response})
    return llm_response

# --- NLP / Info Collection ---

question_requirements = {
    "train_delays":      ["departure_time"],
    "departure_time":    ["departure_station"],
    "platform_details":  ["station"],
    "address_details":   ["station"],
    "train_operator":    ["station"],
    "ticket_off_hours":  ["station"],
    "ticket_machine":    ["station"],
    "seated_area":       ["station"],
    "waiting_area":      ["station"],
    "toilets":           ["station"],
    "baby_changing":     ["station"],
    "wifi":              ["station"],
    "ramp_access":       ["station"],
    "ticket_gates":      ["station"],
    "route_details":     ["departure_station", "arrival_station"],
    "booking_tickets":   ["departure_station", "arrival_station", "departure_time"],
}


def collect_info(user_input):
    global current_requirements, info

    if "station" in current_requirements:
        station = nlp.extract_single_station(user_input)
        if station:
            info["station"] = station
            current_requirements.remove("station")

    if "departure_station" in current_requirements and "arrival_station" in current_requirements:
        departure, arrival, similar_stations = nlp.get_station_data(user_input)
        if departure:
            info["departure_station"] = departure
            current_requirements.remove("departure_station")
        if arrival:
            info["arrival_station"] = arrival
            current_requirements.remove("arrival_station")

    elif "departure_station" in current_requirements:
        station = nlp.extract_single_station(user_input)
        if station:
            info["departure_station"] = station
            current_requirements.remove("departure_station")

    elif "arrival_station" in current_requirements:
        station = nlp.extract_single_station(user_input)
        if station:
            info["arrival_station"] = station
            current_requirements.remove("arrival_station")

    if "departure_time" in current_requirements:
        journey = nlp.extract_date_and_time(user_input)
        if journey.get("DATE") != [] or journey.get("TIME") != []:
            current_requirements.remove("departure_time")
            info["departure_time"] = journey

def complete_request():
    global info, request, current_stage

    if request[0] == "booking_tickets":
        messages.append(add_ticket_followup())
        departing_code = knowledge_base.get_station_code_from_name(info["departure_station"])
        arriving_code  = knowledge_base.get_station_code_from_name(info["arrival_station"])
        outbound, _    = parse_journey_times(info["departure_time"], None)
        year, month, day, hour, minute = convert_datetime_to_tuple(str(outbound))
        url = get_single_ticket_url(departing_code, arriving_code, "departing", f"{day}{month}{year}", hour, minute)
        return url

    elif request[0] in question_requirements and "station" in question_requirements[request[0]]:
        columns = nlp.intent_to_function.get(request[0])
        messages[0] = reply_prompt_builder(nlp.get_station_details_by_columns(info["station"], columns))

    elif request[0] == "route_details":
        route = journey_planner.get_optimal_path(info["departure_station"], info["arrival_station"])
        messages[0] = route_prompt_builder(journey_planner.format_route(route))

    elif request[0] == "train_delays":
        outbound_date, _ = parse_journey_times(info["departure_time"], None)
        _, _, _, hour, minute = convert_datetime_to_tuple(str(outbound_date))
        delay = prediction_model.predict_delay_for_time(hour + ":" + minute)
        messages[0] = reply_delay_builder(f"{delay:.2f}")


    current_stage = "waiting"
    info = {}
    request = ""

# --- Main Entry Point ---

def send_message(user_input):
    global current_stage, current_requirements, info, request
    response = []
    user_input = user_input.strip()
    if not user_input:
        return "Please enter a message."

    messages.append({"role": "user", "content": user_input})



    if current_stage == "waiting":
        intent = nlp.predict_classifier(user_input, nlp.intent_classifier)
        if intent[0] == "station_faq":
            intent = nlp.predict_classifier(user_input, nlp.faq_classifier)
        current_stage = "data_collection"
        current_requirements = list(question_requirements.get(intent[0], []))
        request = intent
        collect_info(user_input)

    elif current_stage == "data_collection":
        collect_info(user_input)

    if current_requirements:
        messages.append(add_focused_followup(current_requirements))
    else:
        response.append(complete_request())

    print("________________________")
    for msg in messages:
        print(f"[{msg['role'].capitalize()}]: {msg['content']}\n")
    print("________________________")

    response.append(llm_generate())
    return response