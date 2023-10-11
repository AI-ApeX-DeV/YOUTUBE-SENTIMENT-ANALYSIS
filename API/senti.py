import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os

HUGGINGFACE_API = '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'
print("Sentiment Analysis Tool")

text = input('Enter a comment: ')
text=text+'ppl'

def senti(text):
    obj = SentimentIntensityAnalyzer()
    senti_dict = obj.polarity_scores(text)
    print(senti_dict)
    
    return senti_dict

import requests

API_URL = "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base"

headers = {"Authorization": "Bearer " + HUGGINGFACE_API}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

def senti_class(text):
    output = query({"inputs": str(text)})
    labels = [item['label'] for item in output[0]]
    scores = [item['score'] for item in output[0]]

    print("Sentiment Labels and Scores")
    for label, score in zip(labels, scores):
        print(f"{label}: {score}")

if text:
    senti(text)
    senti_class(text)
