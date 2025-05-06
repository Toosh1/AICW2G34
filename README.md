# 🎓 AI ChatBot for Rail Ticket Support

This project is an AI-powered chatbot designed to assist users with rail ticketing queries. It leverages natural language processing, real-time train data, and a locally hosted LLaMA language model to provide intelligent and context-aware support.

## 1. 🦙 Download LLaMA Model

Download the **LLaMA 2 7B Chat GGUF** model from [Hugging Face](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/blob/main/llama-2-7b-chat.Q4_K_M.gguf):

- Save the `.gguf` file locally.
- Copy the **full file path** into your `.env` file as shown below.


## 2. 🛠️ Environment Setup

Copy the example environment configuration.
Edit the `.env` file and update the required paths.


```bash
cp .env.example .env
```

## 3. 📦 Install Dependencies

Install all required Python dependencies:

```bash
pip install -r requirements.txt
```


## 4. 🧠 Download spaCy Model

Download the English NLP model for intent and entity extraction:

```bash
python -m spacy download en_core_web_sm
```


## 5. 🧰 Install C++ Build Tools (Windows Only)

Download and install CMake and [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (~7 GB).

## 6. 📝 Setup PostgreSQL Table and Data

Within `src/services/national_rail`, run `darwin_fetcher.py` and `static_feed_fetcher.py` to download relavant train data
Then run `stations_parser.py` in `src/services` to process the `tocs.xml` that was downloaded.

Setup a PostgreSQL database and add the database password to your dotenv file. Ensure the server is running
The server properties are currently set as this:
```py
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="postgres",
    user="postgres",
    password=os.getenv("POSTGRES_PASSWORD")
)
```
In `knowledge_base.py` temporarily uncomment the `generate_station_codes_table()` and `generate_departure_table()` functions and run the script to fill up the tables.
    - You may re-comment these lines after the tables have been fully loaded.
