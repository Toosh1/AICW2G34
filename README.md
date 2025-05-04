# AI ChatBot for Rail Ticket Support

## Requirements
1. Copy the contents of `.env.example` into a `.env` file
2. Install libraries
    - `pip install dotenv, spacy, nltk, pyspellchecker, zeep, datetime, pytest`
        - Install spacy model: `python -m spacy download en_core_web_sm`
    - cmake and c++ tools needed for below:
        - `pip install llama-cpp-python` 
        https://visualstudio.microsoft.com/visual-cpp-build-tools/ ~ 7gb

3. Download Llama (You might need to download this before llama-cpp-python)
    - "https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/blob/main/llama-2-7b-chat.Q4_K_M.gguf"
    - download and copy path to .env file