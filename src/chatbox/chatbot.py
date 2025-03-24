import os
from llama_cpp import Llama 
import json
from llama_cpp import Llama
from dotenv import load_dotenv
import nlp
load_dotenv()

llm = Llama(model_path=os.getenv("LLAMA_PATH"), verbose=False)


def system_prompt_builder(keys):
    message = {
        "role": "system",
        "content": (
            "You are mid conversation with a user who is trying to book a train ticket. Please be kind and polite but stick to the instruction below.\n"
            "Please ask the user for the following information:\n"
            + "\n".join(f"- {key}" for key in keys)
        )
    }
    return message

messages = [""]

# Info memory
info = {
    "departure_station": None,
    "arrival_station": None,
    "departure_time": None,
    "single_ticket": None,
    "railcard": None,
}


# Main chat loop
nlp.setup()
override = None
while True:
    
    # question_goal = ""
    # if override is None: #follow up question may be needed
    #     for key in info:
    #         if info[key] is None:
    #             question_goal = key #what the chatbot is asking for
    #             break
       

    messages[0] = system_prompt_builder(info.keys())


    chat_question = llm.create_chat_completion(messages, max_tokens=256)
    reply = chat_question["choices"][0]["message"]["content"]
    print("Pisces:", reply)

    messages.append({"role": "assistant", "content": chat_question})

    user_input = input("\nYou: ")
    messages.append({"role": "user", "content": user_input})
    extracted_response = nlp.extract_station(user_input)
    if extracted_response is not None:
        # info[question_goal] = extracted_response
        print(extracted_response)

   