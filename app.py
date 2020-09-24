import flask
from flask import Flask , render_template
import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
import tkinter
from tkinter import *
from keras.models import load_model
model = load_model('chatbot_model.h5')
import json
import random


app = Flask(__name__)

intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0]*len(words)
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    p = bow(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break
    return result

def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents)
    return res

def send():
    msg = main.EntryBox.get("1.0", 'end-1c').strip()
    main.EntryBox.delete("0.0", END)

    if msg != '':
        main.ChatLog.config(state=NORMAL)
        main.ChatLog.insert(END, "You : " + msg + '\n\n')
        main.ChatLog.config(foreground="#442265", font=("Comic Sans MS", 12))

        res = chatbot_response(msg)
        main.ChatLog.insert(END, "YoYo PIZZA : " + res + '\n\n')

        main.ChatLog.config(state=DISABLED)
        main.ChatLog.yview(END)
def main():
    base = Tk()
    base.title("YoYo PIZZA")
    base.geometry("400x500")
    base.resizable(width=FALSE, height=FALSE)

    main.ChatLog = Text(base, bd=0, bg="white", height="8", width="50", font="Arial", )
    main.ChatLog.config(state=DISABLED)
    scrollbar = Scrollbar(base, command=main.ChatLog.yview, cursor="heart")
    main.ChatLog['yscrollcommand'] = scrollbar.set
    SendButton = Button(base, font=("Comic Sans MS", 12, 'bold'), text="Send", width="12", height=5,
                        bd=0, bg="#709fb0", activebackground="#3c9d9b", fg='#ffffff',
                        command=send)
    main.EntryBox = Text(base, bd=0, bg="white", width="29", height="5", font="Arial")
    scrollbar.place(x=376, y=6, height=386)
    main.ChatLog.place(x=6, y=6, height=386, width=370)
    main.EntryBox.place(x=128, y=401, height=90, width=265)
    SendButton.place(x=6, y=401, height=90)

    base.mainloop()

@app.route('/')
def index():
    return render_template("main.html")

@app.route('/openchatbot', methods=['POST'])
def predict():
    main()

if __name__ == '__main__':
    app.run( threaded=True, port=5000)

