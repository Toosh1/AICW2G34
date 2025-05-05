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
