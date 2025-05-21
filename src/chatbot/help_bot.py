'''
This module contains the reasoning engine for the chatbot.
The reasoning engine will be responsible for asking the user for information
and storing it in the info dictionary.
'''
import os
from llama_cpp import Llama 
import json
from llama_cpp import Llama
from dotenv import load_dotenv
import nlp
import services.national_rail.journey_planner as journey_planner 
import knowledge_base as kb
import interface

llm = Llama(model_path=os.getenv("LLAMA_PATH"), verbose=False)
messages = [""]

# Info memory
info = {
    "departure_station": None,
    "arrival_station": None,
    "departure_time": None,
    "departure_date": None,
}

# question_requirements = {
#     "train_delays" : ["departure_station"],
#     "route_details" : ["departure_station", "arrival_station"],
#     "departure_time" : ["departure_station"],
#     "arrival_times" : ["arrival_station"],
#     "platform_details" : ["departure_station"],
#     "address_details" : ["departure_station"],
#     "train_operator" : ["departure_station"],
#     "ticket_off_hours" : ["departure_station"],
#     "ticket_machine" : ["departure_station"],
#     "seated_area" : ["station"],
#     "waiting_area" : ["station"],
#     "toilets" : ["station"],
#     "baby_changing" : ["station"],
#     "wifi" : ["station"],
#     "ramp_access" : ["station"],
#     "ticket_gates" : ["station"],

# }


def help_prompt_builder(station_info: str):
    message = {
        "role": "system",
        "content": (
            "You are a railway assistant who is helping a user, you know this information about a station, if a user asks you about a station, please provide the information below.\n"
            "(HIGH IMPORTANCE) If the information provided does not answer the user's question, please apologize and tell them you do not know.\n"
            + station_info + "\n"
        )
    }
    return message


def generic_prompt_builder():
    message = {
        "role": "system",
        "content": (
            "You are a railway assistant who is helping a user, they will ask you questions",
        )
    }
    return message


def append_message(role,message):
    messages.append({"role": role, "content": message})

def ask_user():
    user_input = input("\nYou: ")
    append_message("user",user_input)
    return user_input

def llm_generate_question():
    chat_question = llm.create_chat_completion(messages)
    llm_question = chat_question["choices"][0]["message"]["content"]
    append_message("assistant", chat_question)
    interface.add_message(llm_question, is_user=False)
    print(f"\033[93mPisces: {llm_question}\033[0m")

    
def main():
    interface.main()
    messages[0] = generic_prompt_builder()
    llm_generate_question()  


if __name__ == "__main__":
    main()