import random
import json
import uuid
import conversation
import apiaccess


import torch

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
def new_case_id():                                               #this is for symptom
    """Generates an identifier unique to a new session.

    Returns:
        str: Unique identifier in hexadecimal form.

    Note:
        This is not user id but an identifier that is generated anew with each
        started "visit" to the bot.

    """
    return uuid.uuid4().hex
def run(req):
    """Runs the main application."""
    
    auth_string = '43446992:fc94728c49d650cf38434eed81706d17'
    case_id = new_case_id()

    # Read patient's age and sex; required by /diagnosis endpoint.
    # Alternatively, this could be done after learning patient's complaints
    age, sex = conversation.read_age_sex(req)
    print(f"Ok, {age} year old {sex}.")
    age = {'value':  age, 'unit': 'year'}

    # Query for all observation names and store them. In a real chatbot, this
    # could be done once at initialisation and used for handling all events by
    # one worker. This is an id2name mapping.
    naming = apiaccess.get_observation_names(age, auth_string, case_id, language_model='infermedica-en')

    # Read patient's complaints by using /parse endpoint.
    mentions = conversation.read_complaints(age, sex, auth_string, case_id, language_model='infermedica-en')

    # Keep asking diagnostic questions until stop condition is met (all of this
    # by calling /diagnosis endpoint) and get the diagnostic ranking and triage
    # (the latter from /triage endpoint).
    evidence = apiaccess.mentions_to_evidence(mentions)
    evidence, diagnoses, triage = conversation.conduct_interview(evidence, age,
                                                                 sex, case_id,
                                                                 auth_string,
                                                                 language_model='infermedica-en')

    # Add `name` field to each piece of evidence to get a human-readable
    # summary.
    apiaccess.name_evidence(evidence, naming)

    # Print out all that we've learnt about the case and finish.
    print()
    conversation.summarise_all_evidence(evidence)
    conversation.summarise_diagnoses(diagnoses)
    conversation.summarise_triage(triage)




device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Health buddy"
print("""Hello, Health buddy here. I am your personal health assistant. I will guide you further in your hospital query.
    Before moving forward, If you are feeling unwell or having any sympotms.
    would you like to try our symptom checker. please type "yes" to check diagnose yourself or to know more 
    about hospital type "no"(type 'quit' to exit the chat)""")


def get_response(msg,req):
    if msg == "yes":
        run(req)
        return 'hello'
    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return random.choice(intent['responses'])
    
    return "I do not understand..."


