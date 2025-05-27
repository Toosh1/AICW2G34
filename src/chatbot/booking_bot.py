import tkinter as tk
from datetime import datetime
from llama_cpp import Llama
from dotenv import load_dotenv
from queue import Queue

import os, threading, nlp, journey_planner, knowledge_base, sys

# Merge the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.input_handler import *
from utils.train_ticket_handler import *

load_dotenv()
llm = Llama(model_path=os.getenv("LLAMA_PATH"), verbose=False)

# Global variables
messages = [""]

# --- Chat Functionality ---

def append_message(role, message):
    messages.append({"role": role, "content": message})

def add_message(text, is_user):
    time_sent = datetime.now().strftime('%H:%M')
    msg_container = tk.Frame(chat_canvas_frame, bg="#F0F0F0")
    msg_container.pack(fill='x', pady=2, padx=10, anchor='e' if is_user else 'w')

    msg_bg = "#a0d8ef" if is_user else "#e0e0e0"
    justify = "right" if is_user else "left"

    msg = tk.Label(
        msg_container,
        text=text,
        padx=10,
        pady=7,
        bg=msg_bg,
        fg="black",
        wraplength=340,
        justify=justify,
        anchor='w',
        font=("Arial", 11)
    )
    msg.pack(side='right' if is_user else 'left', anchor='e' if is_user else 'w')

    timestamp = tk.Label(
        msg_container,
        text=time_sent,
        bg="#F0F0F0",
        fg="#818181",
        font=("Arial", 8),
        padx=5
    )
    timestamp.pack(anchor='e' if is_user else 'w')

    chat_frame.update_idletasks()
    chat_frame.yview_moveto(1.0)

llm_queue = Queue()
llm_processing = False

def llm_generate_question_async():
    typing_label = tk.Label(chat_canvas_frame, text="Pisces is typing...", fg="gray", font=("Arial", 10, "italic"), bg="#F0F0F0")
    typing_label.pack(anchor='w', padx=10, pady=2)
    chat_frame.update_idletasks()

    def generate():
        chat_question = llm.create_chat_completion(messages)
        llm_response = chat_question["choices"][0]["message"]["content"]
        append_message("assistant", llm_response)
        typing_label.destroy()
        add_message(llm_response, is_user=False)

    threading.Thread(target=generate).start()

# --- Prompt Builders ---

def hello_prompt_builder():
    return {
        "role": "system",
        "content": "You are a railway assistant helping a user book a ticket. Just greet the user."
    }

def add_focused_followup(keys):
    if not keys:
        return
    prompt = (
        "Just ask the user for the following missing information:\n" +
        "\n".join(f"- {key}" for key in keys) +
        "\nDo not discuss anything else."
    )
    messages.append({"role": "assistant", "content": prompt})
    llm_generate_question_async()

def incorrect_station_prompt_builder(close_stations):
    suggestion = ", ".join(close_stations[1])
    return {
        "role": "system",
        "content": (
            "You are a railway assistant helping a user.However the user entered a station that doesn't exist.\n" +
            f"(IMPORTANT ) The station '{close_stations[0]}' was not recognized. Try: {suggestion}."
        )
    }

def reply_prompt_builder(reply):
    return {
        "role": "system",
        "content": (
            "You are a railway assistant helping a user. You have checked and below is the answer to the question the user asked.\n" +
            "Only provide the user with the following information." +
            "\n" + reply
        )
    }

def route_prompt_builder(reply):
    return {
        "role": "system",
        "content": (
            "You are a railway assistant helping a user. You have checked and below is the answer to the question the user asked.\n" +
            "Only provide the user with the following information. Explain the entire route following, provide the entire route." +
            "\n" + reply
        )
    }

# --- NLP Integration ---

def collect_info(user_input):
    global current_requirements, info
    requirements = current_requirements
    if "station" in requirements:
            station = nlp.extract_single_station(user_input)
            if station:
                info["station"] = station
                requirements.remove("station")

    if "departure_station" in current_requirements and "arrival_station" in current_requirements:
        departure, arrival, similar_stations = nlp.get_station_data(user_input)
        if departure:
            info["departure_station"] = departure
            requirements.remove("departure_station")
            print("Departure found: ", departure)
        if arrival:
            info["arrival_station"] = arrival
            requirements.remove("arrival_station")
            print("Arrival found: ", arrival)
        # if similar_stations:
        #     messages[0] = incorrect_station_prompt_builder(similar_stations[0])
        #     llm_generate_question_async()

    elif "departure_station" in requirements:
            station = nlp.extract_single_station(user_input)
            if station:
                info["departure_station"] = station
                requirements.remove("departure_station")

    elif "arrival_station" in requirements:
            station = nlp.extract_single_station(user_input)
            if station:
                info["arrival_station"] = station
                requirements.remove("arrival_station")
        #add similar stations logic
        
    if "departure_time" in current_requirements:
        journey = nlp.extract_date_and_time(user_input)
        if journey.get("DATE") != [] or journey.get("TIME") != []:
            requirements.remove("departure_time")
            info["departure_time"] = journey

    current_requirements = requirements

def complete_request():
    global info, request, current_stage
    print("Message Completed")
    print(f"Request: {request[0]}")
    
    if request[0] == "booking_tickets":
        departing_code = knowledge_base.get_station_code_from_name(info["departure_station"])
        arriving_code = knowledge_base.get_station_code_from_name(info["arrival_station"])
        outbound, _ = parse_journey_times(info["departure_time"], None)
        year, month, day, hour, minute = convert_datetime_to_tuple(str(outbound))
        
        url = get_single_ticket_url(
            departing_code, arriving_code, "departing", f"{day}{month}{year}", hour, minute
        )
        
        print("Departing code: ", departing_code)
        print("Arriving code: ", arriving_code)
        print("Outbound journey: ", outbound)
        print("Booking URL: ", url)
        
    elif request[0] in ["platform_details","address_details","train_operator","ticket_off_hours","ticket_machine","seated_area","waiting_area","toilets","baby_changing","wifi","ramp_access","ticket_gates"]:
        columns = nlp.intent_to_function.get(request[0])
        print(nlp.get_station_details_by_columns(info["station"],columns))
        messages[0] = reply_prompt_builder(nlp.get_station_details_by_columns(info["station"],columns))
        print(messages[0])
        llm_generate_question_async()

    elif request[0] == "route_details":
        route = journey_planner.get_optimal_path(info["departure_station"],info["arrival_station"])
        string_path = journey_planner.format_route(route)
        messages[0] = route_prompt_builder(string_path)
        print(messages[0])
        llm_generate_question_async()
    
    elif request[0] == "train_delays":
        pass
        ##get times from thing and get from prediction model

    elif request[0] == "departure_time":
        pass
        ##add the live departure time thingy

    messages.clear()
    current_stage = "waiting"
    info = {}
    request = ""

question_requirements = {

    "train_delays" : ["departure_time"],
    "departure_time" : ["departure_station"],



    "platform_details" : ["station"],
    "address_details" : ["station"],
    "train_operator" : ["station"],
    "ticket_off_hours" : ["station"],
    "ticket_machine" : ["station"],
    "seated_area" : ["station"],
    "waiting_area" : ["station"],
    "toilets" : ["station"],
    "baby_changing" : ["station"],
    "wifi" : ["station"],
    "ramp_access" : ["station"],
    "ticket_gates" : ["station"],
    "route_details" : ["departure_station", "arrival_station"],
    "booking_tickets" : ["departure_station", "arrival_station", "departure_time"],

}

current_requirements = []
request = ""
info = {}

current_stage = "waiting"  # Initial stage
#waiting
#data_collection

# --- Chat Controller ---
def send_message():
    global current_stage, current_requirements, info, request
    user_input = entry_box.get().strip()
    if user_input == "":
        return
    add_message(user_input, is_user=True)
    entry_box.delete(0, tk.END)
    append_message("user", user_input)
    
    if current_stage == "waiting":
        intent = nlp.predict_classifier(user_input,nlp.intent_classifier)
        if intent[0] == "station_faq":
            intent = nlp.predict_classifier(user_input, nlp.faq_classifier)
        current_stage = "data_collection"
        current_requirements = question_requirements.get(intent[0], [])
        request = intent
        collect_info(user_input)
        if current_requirements != []:
            add_focused_followup(current_requirements)
        else:
            complete_request()

    elif current_stage == "data_collection":
        collect_info(user_input)
        if current_requirements != []:
            add_focused_followup(current_requirements)
        else:
            complete_request()

    print(info)
    print(current_requirements)

# --- GUI Main ---
def gui_main():
    global root, chat_frame, chat_canvas_frame, entry_box

    root = tk.Tk()
    root.title("Pisces: Train Chatbot")
    root.geometry("420x580")
    root.configure(bg="#F0F0F0")

    # Chat display
    container = tk.Frame(root, bg="#F0F0F0")
    container.pack(fill=tk.BOTH, expand=True)

    chat_frame = tk.Canvas(container, bg="#F0F0F0", highlightthickness=0)
    chat_scrollbar = tk.Scrollbar(container, command=chat_frame.yview)
    chat_frame.configure(yscrollcommand=chat_scrollbar.set)

    chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    chat_canvas_frame = tk.Frame(chat_frame, bg="#F0F0F0")
    chat_frame.create_window((0, 0), window=chat_canvas_frame, anchor='nw')

    def on_configure(event):
        chat_frame.configure(scrollregion=chat_frame.bbox("all"))
        chat_frame.yview_moveto(1.0)

    chat_canvas_frame.bind("<Configure>", on_configure)

    # Bottom input
    bottom_frame = tk.Frame(root, bg="white", padx=10, pady=10)
    bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)

    entry_box = tk.Entry(bottom_frame, font=("Arial", 12))
    entry_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
    entry_box.bind("<Return>", lambda event: send_message())

    send_button = tk.Button(bottom_frame, text="Send", command=send_message, font=("Arial", 10))
    send_button.pack(side=tk.RIGHT)

    # Start conversation
    messages[0] = hello_prompt_builder()
    llm_generate_question_async()

    root.mainloop()

if __name__ == "__main__":
    gui_main()
