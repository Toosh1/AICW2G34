import random, spacy, difflib, requests

from difflib import get_close_matches, SequenceMatcher
from bs4 import BeautifulSoup
from datetime import datetime
from random import choice
from experta import *

import warnings
warnings.filterwarnings('ignore')

from nlp_services import load_sentences, load_intentions,\
            load_labels_sentences, extract_locations, check_similarity

import spacy.cli
nlp = spacy.load('en_core_web_sm')

train_ticket_sentences = load_sentences()
intentions = load_intentions()
labels, sentences = load_labels_sentences(train_ticket_sentences)

def chatbot_response(user_input):
    is_same_intent, _ = check_similarity(user_input, "train_ticket", labels, sentences)
    if not is_same_intent:
        print(f"BOT: {random.choice( intentions['unsure']['responses'])}")
        return False

    locations = extract_locations(user_input)

    if len(locations) == 0:
        print(
            "BOT: I didn't catch any departure or arrival stations. Could you please provide both your departure and arrival stations?")
    elif len(locations) == 1:
        print(
            f"BOT: You mentioned {locations[0]} as your station. Could you please tell me where you're traveling to (arrival station)?")
    else:
        # WIP: At the moment it assumes that the locations mentioned will be departure --> arrival
        departure, arrival = locations[0], locations[1]
        print(f"BOT: Sure! I can help you find a train ticket from {departure} to {arrival}.")

    return True

conversation_end = False

# WIP: At the moment the conversation loops indefinitely
# Needs to check user's input against ALL intents then respond accordingly

if __name__ == "__main__":
    while (conversation_end == False):
        user_input = input("USER: ")
        chatbot_response(user_input)