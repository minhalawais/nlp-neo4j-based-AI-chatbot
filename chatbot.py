from glob import glob
import aiml
from autocorrect import Speller
import requests
from flask import request,jsonify
from bs4 import BeautifulSoup
from website import creat_app
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag
from nltk.corpus import wordnet,stopwords
import userData
from collections import Counter
import database
import datetime
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()
app = creat_app()
spell = Speller()
k = aiml.Kernel()
chat = []
wh_family = ['who','whom','what','when','where','which','why','whose','how','could','would','do','does','should','was','were','is','am','are','will','shall']
k.setBotPredicate("name", "Dexx")

k.setBotPredicate("name", "Mini Bot")
k.setBotPredicate("email", "minhalawais1@gmail.com")
k.setBotPredicate("botmaster", "Minhal Awais")
k.setBotPredicate("master", "Minhal Awais")
k.setBotPredicate("country", "Pakistan")
k.setBotPredicate("nationality", "Pakistani")



def read_files():
    path = "MyBot"
    for name in glob(path + "\*"):
        k.learn(name)


def get_ip():
    ip = requests.get('https://api.ipify.org').content.decode('utf8')
    return ip
def getResponse(query):
    while True:
        response = k.respond(query)
        if response:
            return (str(response))
        else:
            return (str(":)"))

def remove_special_characters(string):
    translation_table = str.maketrans('', '', "!@#$%^&*(){}[]<>?.,:;/\|`~")
    cleaned_string = string.translate(translation_table)
    return cleaned_string

def can_be_answered_through_web_scraping(sentence):
    web_scraping_keywords = ['meant','who', 'when', 'where', 'why', 'definition of', 'meaning of','what','should','where','which','does']
    adv = ['your','my','you']
    for keyword in web_scraping_keywords:
        if keyword in sentence.lower():
            for ad in  adv:
                if ad in sentence.lower():
                    return False
            return True
    return False

def can_be_answered_through_wordnet(word_token):
    if 'meaning' in word_token or 'define' in word_token or 'definition' in word_token or 'meant' in word_token:
        last_word = word_token[-1]
        if pos_tag([last_word])[0][1].startswith('N') or pos_tag([last_word])[0][1].startswith('V'):
            return last_word
    return False


def get_sentiment(chat_message):
    chat_list = sent_tokenize(chat_message)
    sent_list = []
    for chat in chat_list:
        if "User: " in chat:
            index = chat.find("Bot")
            chat = chat[0:index-1]
            chat = chat.replace("User: ","")
            sentiment_scores = sid.polarity_scores(chat)
            sentiment_polarity = sentiment_scores['compound']

            if sentiment_polarity >= 0.05:
                sentiment_label = 'Happy'
            elif sentiment_polarity <= -0.05:
                sentiment_label = 'Sad'
            else:
                sentiment_label = 'Neutral'
            sent_list.append(sentiment_label)
    counter = Counter(sent_list)
    most_common_element = max(counter, key=counter.get)
    return most_common_element

def web_scrap(question):
    search_url = f"https://www.google.com/search?q={question}"
    response = requests.get(search_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    first_result = soup.find("div", class_="BNeawe").get_text()
    return first_result

def getfact(words, pos_tags, name):
    relationship_nouns = ["father", "mother", "son", "relative", "relatives", "friend", "friends"]
    noun_tags = ['NN', 'NNS', 'NNP', 'NNPS']

    current_relationship = next((word.lower() for word in words if word.lower() in relationship_nouns), None)
    final_relationship = ""
    entities = []

    if current_relationship:
        if current_relationship in ["father", "mother"]:
            final_relationship = "son_of"
        elif current_relationship in ["friend", "friends"]:
            final_relationship = "are_friends"
        elif current_relationship in ["relative", "relatives"]:
            final_relationship = "are_relatives"
        elif current_relationship == "son":
            final_relationship = "son_of"

        if pos_tags[0][0] == "My" or pos_tags[0][0] == 'I' or words[0] in name:
            entities.append(name)
            relevant_nouns = [word for word, tag in pos_tags if word not in relationship_nouns and tag in noun_tags]
            entities.append(relevant_nouns[1])
        else:
            relevant_nouns = [word for word, tag in pos_tags if word not in relationship_nouns and tag in noun_tags]
            entities = relevant_nouns[:2]
        if final_relationship == "son_of" and "my" not in words and "of" in words and words.index(current_relationship) + 1 < len(words):
            entities[0], entities[1] = entities[1], entities[0]

    if final_relationship and len(entities) > 0:
        if len(entities) == 1:
            entities.extend([name, entities[0]])
        relationship_string = f"{final_relationship}({entities[0]},{entities[1]})"
        entities.extend([final_relationship, relationship_string])

    return entities

@app.route('/send_message', methods=['POST'])
def get_bot_response():
    message = request.json['message']
    response = getResponse(message)
    message = message.lower()
    message = remove_special_characters(message)
    sent_token = sent_tokenize(message)
    word_token = word_tokenize(message)
    name = database.get_name(userData.userEmail)
    gender = database.get_gender(userData.userEmail)
    curr_date = datetime.date.today()
    ip = database.get_ip(userData.userEmail)
    stop_words = set(stopwords.words('english'))
    tagged = pos_tag(word_token)
    k.setPredicate("fullname", name)
    k.setPredicate("name", name)
    k.setPredicate("email", userData.userEmail)
    k.setPredicate("gender", gender)

    if "Yes" in message or "yes" in message:
        if database.findRelation(userData.userEmail) in userData.last_message:
            name1 = database.findRelation(userData.userEmail)
            database.create_relation(name1,userData.userEmail)
    if "No" in message or "no" in message:
        print("Yes")
        if database.findRelation(userData.userEmail) in userData.last_message:

            database.update_norelation(userData.userEmail,database.findRelation(userData.userEmail))

    if getfact(word_token,tagged,name):
        entities = getfact(word_token,tagged,name)
        database.create_social_network(entities[0],entities[1],entities[2])

    if can_be_answered_through_wordnet(word_token):
        last_word = can_be_answered_through_wordnet(word_token)
        synsets = wordnet.synsets(last_word)
        if synsets:
            response = f"{synsets[0].definition()}"
    elif can_be_answered_through_web_scraping(message):
        response = web_scrap(message)
    print(response)
    if "Recursion limit exceeded" in response or "None" in response or "Unknown" in response or "response" in response or "responses" in response or "responding" in response or not response:
        relation = database.findRelation(userData.userEmail)
        if relation:
            if relation in database.get_norelation(userData.userEmail):
                pass
            else:
                response = f"Do you know {relation} ? He lives near you."
                userData.last_message = response
        elif get_sentiment(database.get_episode_chat(userData.userEmail)) != "Neutral":
            sent = get_sentiment(database.get_episode_chat(userData.userEmail))
            response = f"You seems to be {sent} today. How is your day going?"
        print(get_sentiment(database.get_episode_chat(userData.userEmail)))
    comp_chat = "User: "+ message + "\n" + "Bot: " + response + "\n"
    database.update_episode(userData.userEmail,curr_date,comp_chat)
    return jsonify({'response': response, 'message': message})

if __name__ == "__main__":
    read_files()
    app.run(host='0.0.0.0',port=40000, debug=True)
