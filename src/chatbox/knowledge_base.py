import os
from llama_cpp import Llama 
from dotenv import load_dotenv
load_dotenv()

llm = Llama(model_path= os.getenv("LLAMA_PATH"),verbose=False)
response = llm("What is the capital of France?", max_tokens=50)

print("Bot:", response["choices"][0]["text"].strip())