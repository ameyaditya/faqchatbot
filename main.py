from flask import Flask, render_template, request, url_for, redirect
import pandas as pd
import numpy as np
import string
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import json

ps = PorterStemmer()
df = pd.read_excel("queries.xlsx")
df.drop(['Unnamed: 3'], axis=1, inplace = True)
df.head()

tags = list(df['Tags'])
answers = list(df['Answer'])


for i in range(len(tags)):
    tags[i] = tags[i].split(",")
    for j in range(len(tags[i])):
        tags[i][j] = tags[i][j].rstrip().lstrip()
        tag, val = tags[i][j].split()
        val = float(val)
        if tag.startswith('('):
            tag = tag[1:-1]
            tag = tag.split("/")
            for k in range(len(tag)):
                tag[k] = tag[k].rstrip().lstrip()
        tags[i][j] = (tag, val)

def getscore(text, processed_text):
    intersection_sum = 0.0
    intersection = 0
    for i in range(len(processed_text)):
        parti_tag, parti_score = processed_text[i]
        for j in text:
            if type(parti_tag) == list:
                for k in range(len(parti_tag)):
                    parti_tag[k] = ps.stem(parti_tag[k])
                if j in parti_tag:
                    intersection += 1
                    intersection_sum += parti_score
            elif ps.stem(parti_tag) == j:
                intersection += 1
                intersection_sum += parti_score
    return (intersection/(len(text) + len(processed_text) - intersection))

def get_answer(query):
    score = []
    useless_words = {"college", "rnsit"}
    question_tags = {"what", "who", "how", "where", "when", "why", "can"}
    stpwords = set(stopwords.words("english"))
    query = query.translate(str.maketrans("", "", string.punctuation))
    query = query.lower()
    partitioned_text = set(query.split())
    partitioned_text = partitioned_text.difference(stpwords)
    partitioned_text = partitioned_text.difference(question_tags)
    partitioned_text = list(partitioned_text)
    for i in range(len(partitioned_text)):
        partitioned_text[i] = ps.stem(partitioned_text[i])
    for i in tags:
        score.append(getscore(partitioned_text, i))
    if max(score) > 0.2:
        ans_index = np.argmax(score)
    else:
        return("Cannot find answer to this question.")
    return answers[ans_index]

    
app = Flask(__name__, static_url_path='/static')

@app.route("/querymessage", methods=['POST'])
def querymessage():
	data = request.form['text']
	ans = get_answer(data)
	return ans


@app.route('/')
def hello_world():
    return render_template("index.html")
app.run(debug=True)