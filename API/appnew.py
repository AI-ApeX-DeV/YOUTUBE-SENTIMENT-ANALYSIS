from flask import Flask, render_template, request
import os
from googleapiclient.discovery import build
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests

app = Flask(__name__)

API_KEY = "AIzaSyAfmf9OE52jKRzqnE5fRyH4nrKfljXyaQ8"
HUGGINGFACE_API = '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'
headers = {"Authorization": "Bearer " + HUGGINGFACE_API}
API_URL = "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base"

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

def senti(text):
    obj = SentimentIntensityAnalyzer()
    senti_dict = obj.polarity_scores(text)
    
    # Convert the dictionary to a string with each key-value pair on a new line
    result = "\n".join([f"{key}: {value}" for key, value in senti_dict.items()])
    
    return result

def senti_class(text):
    output = query({"inputs": str(text)})
    labels = [item['label'] for item in output[0]]
    scores = [item['score'] for item in output[0]]

    tx = ""
    for label, score in zip(labels, scores):
        tx = tx + label + " : " + str(score) + "\n"
    return tx


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_prompt = request.form['search_query']

        youtube = build('youtube', 'v3', developerKey=API_KEY)

        search_response = youtube.search().list(
            q=user_prompt,
            type="video",
            part="id",
            maxResults=5
        ).execute()

        video_ids = [item['id']['videoId'] for item in search_response['items']]

        video_data = {}

        weight_views = 0.7
        weight_likes = 0.3

        for video_id in video_ids:
            
            video_response = youtube.videos().list(
                id=video_id,
                part="statistics"
            ).execute()
            
            statistics = video_response['items'][0]['statistics']
            view_count = int(statistics['viewCount'])
            like_count = int(statistics['likeCount'])
            
            # Calculate the weighted score
            score = (weight_views * view_count) + (weight_likes * like_count)
            
        
            comments_response = youtube.commentThreads().list(
                videoId=video_id,
                part="snippet",
                maxResults=20 # Retrieve up to 20 comments
            ).execute()

            # Concatenate all comments for this video into a single variable
            comments = '\n'.join([item['snippet']['topLevelComment']['snippet']['textDisplay'] for item in comments_response['items']])
            
            video_data[video_id] = {
                'score': score,
                'comments': comments
            }

        # Sort videos by score in descending order
        sorted_videos = sorted(video_data.items(), key=lambda x: x[1]['score'], reverse=True)


        print("Top 30 Videos:")
        for i, (video_id, data) in enumerate(sorted_videos[:30], start=1):
            video_info = youtube.videos().list(
                id=video_id,
                part="snippet"
            ).execute()
            title = video_info['items'][0]['snippet']['title']
            
            print(f"{i}. {title} - Score: {data['score']:.2f}")
            
            # Print the concatenated comments for this video
            print('\n')
            print('\n')
            print('SENTIMENT ANALYSIS OF COMMENTS : ')
            text=data['comments']

            try:
                words = text.split()
                selected_words = words[:200]
                words = ' '.join(selected_words)
                x=senti(words)
                y=senti_class(words)
            except: 
                print("ERROR ERROR ERROR")
            print("\n\n TOP 20 COMMENTS MERGED TOGETHER :")  

            sorted_videos=text+x+y
            
            enumerated_videos = list(enumerate(sorted_videos[:30], start=1))

            return render_template('results.html', enumerated_videos=enumerated_videos)


    return render_template('index2.html')

if __name__ == '__main__':
    app.run(debug=True)
