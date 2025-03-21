import os
from llama_cpp import Llama 
from dotenv import load_dotenv
load_dotenv()

llm = Llama(model_path=os.getenv("LLAMA_PATH"), verbose=False)

while True:
    user_input = input("\nYou: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Exiting chat. Goodbye!")
        break
    response = llm(user_input, max_tokens=50    )
    print("Bot:", response["choices"][0]["text"].strip())