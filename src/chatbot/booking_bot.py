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
import routes 
import knowledge_base as kb

llm = Llama(model_path=os.getenv("LLAMA_PATH"), verbose=False)
messages = [""]

# Info memory
info = {
    "departure_station": None,
    "arrival_station": None,
    "departure_time": None,
    "departure_date": None,
}

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

def generic_prompt_builder(keys):
    message = {
        "role": "system",
        "content": (
            "You are a railway assistant who is helping a user who is trying to book a train ticket. Please be kind and polite but stick to the instruction below.\n"
            "(HIGH IMPORTANCE) Only ask the user for the following nothing extra:\n"
            + "\n".join(f"- {key}" for key in keys if info[key] is None)
        )
    }
    return message

def specific_prompt_builder(goal):
    message = {
        "role": "system",
        "content": (
            "You are a railway assistant who is helping a user who is trying to book a train ticket. Please be kind and keep messages relatively straight forward but stick to the instruction below.\n"
            "(HIGH IMPORTANCE) Only ask the user for the following singular piece of information`:\n"
            + goal
        )
    }
    return message

def incorrect_station_prompt_builder(close_stations):
    suggestion = ", ".join(close_stations[1])
    message = {
        "role": "system",
        "content": (
            f"You are a railway assistant who is helping a user who is trying to book a train ticket, do not give the user any information about the trip keep messages straightforward. Please be kind and polite but stick to the instruction below.\n"
            f"(HIGH IMPORTANCE) The user has entered a station that does not exist: '{close_stations[0]}'. However, these stations do exist: {suggestion}. Ask the user to clarify"
        )
    }
    return message

def two_stations_prompt_builder(close_stations):

    message = {
        "role": "system",
        "content": (
            "You are a railway assistant who is helping a user who is trying to book a train ticket. Please be kind and polite but stick to the instruction below.\n"
            "(HIGH IMPORTANCE) The user has entered incorrect stations " + {close_stations[0]} +", please ask for a correction with the following suggestions: "
            
        )
    }
    return message

def please_try_again():
    message = {
        "role": "system",
        "content": (
            "You are a railway assistant who is helping a user who is trying to book a train ticket. Please be kind and polite but stick to the instruction below.\n"
            "(HIGH IMPORTANCE) The user has entered another station that does not exist. Please ask for a correction."
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
    print(f"\033[93mPisces: {llm_question}\033[0m")

def fill_station_info(user_input):
    departure, arrival, similar_stations = nlp.get_station_data(user_input)
    if not departure and not arrival:
        messages[0] = two_stations_prompt_builder((user_input, similar_stations))
        llm_generate_question()
        corrected_input = ask_user()
        fill_station_info(corrected_input)
        return

    if departure:
        info["departure_station"] = departure
    if arrival:
        info["arrival_station"] = arrival

    if similar_stations != [None]:
        if not info.get("departure_station"):
            while not info.get("departure_station"):
                if similar_stations:
                    messages[0] = incorrect_station_prompt_builder(similar_stations[0])
                    llm_generate_question()
                    corrected_input = ask_user()
                    station = nlp.extract_single_station(corrected_input)
                    if station:
                        info["departure_station"] = station
                        break
                    else:
                        messages[0] = please_try_again()
                        llm_generate_question()
                        corrected_input = ask_user()

        if not info.get("arrival_station"):
            while not info.get("arrival_station"):
                if similar_stations:
                    messages[0] = incorrect_station_prompt_builder(similar_stations[0])
                    llm_generate_question()
                    corrected_input = ask_user()
                    station = nlp.extract_single_station(corrected_input)
                    if station:
                        info["arrival_station"] = station
                        break
                    else:
                        messages[0] = please_try_again()
                        llm_generate_question()
                        corrected_input = ask_user()

def fill_time_info(user_input):
    return_phrase = nlp.get_return_ticket(user_input)
    outbound = nlp.extract_date_and_time(user_input)
    print(outbound)
    outbound_date, outbound_time = outbound["DATE"], outbound["TIME"]
    while not outbound_date or not outbound_time:
        if not outbound_date and not outbound_time:
            messages[0] = specific_prompt_builder("departure date and time")
            llm_generate_question()
            corrected_input = ask_user()
            outbound = nlp.extract_date_and_time(corrected_input)
            print(outbound)
            outbound_date = outbound["DATE"]
            outbound_time = outbound["TIME"]
        if not outbound_date:   
            messages[0] = specific_prompt_builder("departure date")
            llm_generate_question()
            corrected_input = ask_user()
            outbound = nlp.extract_date_and_time(corrected_input)
            print(outbound)
            outbound_date = outbound["DATE"]

        if not outbound_time:
            messages[0] = specific_prompt_builder("departure time")
            llm_generate_question()
            corrected_input = ask_user()
            outbound = nlp.extract_date_and_time(corrected_input)
            print(outbound)
            outbound_time = outbound["TIME"]

    info["departure_date"] = outbound_date
    info["departure_time"] = outbound_time

def ask_for_help():
    route = routes.main(info["departure_station"].upper(), info["arrival_station"].upper())
    crs_dep, crs_arr = kb.get_station_code_from_name(info["departure_station"].capitalize()), kb.get_station_code_from_name(info["arrival_station"].capitalize())
    print(info)
    
    information = kb.get_all_station_details(crs_dep) + kb.get_all_station_details(crs_arr)
    print(information)
    messages[0] = help_prompt_builder(information)
    while True:
        llm_generate_question()
        ask_user()


def main():
    #Firstly ask the user for all basic information , departure station, arrival station and departure time
    messages[0] = generic_prompt_builder(info.keys())
    llm_generate_question()
    user_input = ask_user()
    fill_station_info(user_input)
    fill_time_info(user_input)
    print(info)
    ask_for_help()

if __name__ == "__main__":
    main()
