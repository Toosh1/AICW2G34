import os
from llama_cpp import Llama 
import json
from llama_cpp import Llama
from dotenv import load_dotenv
import nlp
load_dotenv()

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


def generic_statement():
    # Ask generic statement with all missing info from memory and try to extract everything from input
    messages[0] = generic_prompt_builder(info.keys())
    chat_question = llm.create_chat_completion(messages, max_tokens=256)
    reply = chat_question["choices"][0]["message"]["content"]
    close_stations = None

    print(f"\033[93mPisces: {reply}\033[0m")
    user_input = input("\nYou: ")

    append_message("assistant", chat_question)
    append_message("user",user_input)

    if info["departure_station"] is None and info["arrival_station"] is None:
        extracted_response = nlp.find_stations(user_input)
        info["departure_station"], info["arrival_station"], close_stations = extracted_response

    if info["departure_time"] is None:
        info["departure_time"] = nlp.extract_time(user_input)

    if close_stations is not None:
        messages[0] = incorrect_station_prompt_builder(close_stations)
        if info["departure_station"] is None:
            singular_target_statement("departure_station")
        elif info["arrival_station"] is None:
            singular_target_statement("arrival_station")


    
            

def singular_target_statement(goal):
    chat_question = llm.create_chat_completion(messages, max_tokens=256)
    reply = chat_question["choices"][0]["message"]["content"]

    print(f"\033[93mPisces: {reply}\033[0m")
    user_input = input("\nYou: ")

    append_message("assistant", chat_question)
    append_message("user",user_input)

    info[goal] = nlp.extract_single_station(user_input)

    if info[goal] is None:
        messages[0] = please_try_again()
        singular_target_statement(goal)




def append_message(role,message):
    messages.append({"role": role, "content": message})




# Main chat loop
nlp.setup()
override = None
while True:
    generic_statement()






    
    

   