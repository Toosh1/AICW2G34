import json, spacy

nlp = spacy.load('en_core_web_sm')

# Loads sentences from 'data/sentences'
def load_sentences():
    sentences_path = "data/sentences.txt"

    train_ticket_sentences = ''

    with open(sentences_path) as file:
        for line in file:
            parts = line.split(' | ')
            if parts[0] == 'train_ticket':
                train_ticket_sentences = train_ticket_sentences + ' ' + parts[1].strip()

    return train_ticket_sentences

def load_intentions():
    intentions_path = "data/intentions.json"

    with open(intentions_path) as f:
        intentions = json.load(f)

    return intentions

# Parses sentences into labels and sentences (dependent on 'load_sentences' function)
def load_labels_sentences(loaded_sentences):
    labels = []
    sentences = []

    doc = nlp(loaded_sentences)
    for sentence in doc.sents:
        labels.append("train_ticket")
        sentences.append(sentence.text.lower().strip())

    # for label, sentence in zip(labels, sentences):
    #     print(label + " : " + sentence)

    return labels, sentences

# Separates text into sentences + removes stop_words and punctuation
def lemmatize_and_clean(text):
    doc = nlp(text.lower())
    out = ""
    for token in doc:
        if not token.is_stop and not token.is_punct:
            out = out + token.lemma_ + " "
    return out.strip()

# Extracts locations from user input
def extract_locations(user_input):
    doc = nlp(user_input)
    locations = []

    for ent in doc.ents:
        if ent.label_ == 'GPE':
            locations.append(ent.text)

    return locations

def check_similarity(user_input, label, labels, sentences):
    cleaned_user_input = lemmatize_and_clean(user_input)
    doc_1 = nlp(cleaned_user_input)
    similarities = {}

    for idx, sentence in enumerate(sentences):
        cleaned_sentence = lemmatize_and_clean(sentence)
        doc_2 = nlp(cleaned_sentence)
        similarity = doc_1.similarity(doc_2)
        similarities[idx] = similarity

    max_similarity_idx = max(similarities, key=similarities.get)

    min_similarity = 0.75

    if similarities[max_similarity_idx] > min_similarity and labels[max_similarity_idx] == label:
        return True, max_similarity_idx
    return False, None