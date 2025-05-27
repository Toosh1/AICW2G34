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

llm = Llama(model_path=os.getenv("LLAMA_PATH"), verbose=False)
messages = [""]

# Info memory
info = {
    "departure_station": None,
    "arrival_station": None,
    "departure_time": None,
}

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
            "You are a railway assistant who is helping a user who is trying to book a train ticket. Please be kind and polite but stick to the instruction below.\n"
            "(HIGH IMPORTANCE) Only ask the user for the following singular piece of information`:\n"
            + goal
        )
    }
    return message

def incorrect_station_prompt_builder(close_stations):
    suggestions = ", ".join(close_stations[1])  
    message = {
        "role": "system",
        "content": (
            "You are a railway assistant who is helping a user who is trying to book a train ticket. Please be kind and polite but stick to the instruction below.\n"
            "(HIGH IMPORTANCE) The user has entered a station (" + close_stations[0] + ") that does not exist. Please ask for a correction with the following suggestions: "
            + suggestions
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
    chat_question = llm.create_chat_completion(messages, max_tokens=256)
    llm_question = chat_question["choices"][0]["message"]["content"]
    append_message("assistant", chat_question)
    print(f"\033[93mPisces: {llm_question}\033[0m")

def fill_station_info(user_input):
    

def main():
    #Firstly ask the user for all basic information , departure station, arrival station and departure time
    messages[0] = generic_prompt_builder(info.keys())
    llm_generate_question()
    user_input = ask_user()
    fill_station_info(user_input)


    

if __name__ == "__main__":
    main()
