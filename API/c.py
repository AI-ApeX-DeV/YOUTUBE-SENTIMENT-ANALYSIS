import os
from googleapiclient.discovery import build
from transformers import pipeline
from googleapiclient.errors import HttpError

# Set your YouTube API key
API_KEY = "AIzaSyAfmf9OE52jKRzqnE5fRyH4nrKfljXyaQ8"  # Replace with your actual API key

# Initialize the YouTube Data API client
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Initialize the sentiment analysis pipeline using a pre-trained BERT model
nlp = pipeline("sentiment-analysis")

# Prompt the user for a search query
user_prompt = input("Enter your search query: ")

# Call the search.list method to search for videos
search_response = youtube.search().list(
    q=user_prompt,
    type="video",
    part="id",
    maxResults=30  # You can adjust the number of results as needed
).execute()

# Extract the video IDs from the search results
video_ids = [item['id']['videoId'] for item in search_response['items']]

# Initialize a dictionary to store video scores and sentiment probabilities
video_data = []

# Define the weights for views, likes, and comments
weight_views = 0.7
weight_likes = 0.3

# Maximum sequence length for the BERT model (adjust as needed)
max_sequence_length = 512

# Fetch video statistics to calculate scores and perform sentiment analysis
for video_id in video_ids:
    video_response = youtube.videos().list(
        id=video_id,
        part="statistics,snippet"
    ).execute()
    
    statistics = video_response['items'][0]['statistics']
    view_count = int(statistics['viewCount'])
    like_count = int(statistics['likeCount'])
    title = video_response['items'][0]['snippet']['title']
    
    # Calculate the weighted score
    score = (weight_views * view_count) + (weight_likes * like_count)
    
    try:
        # Get video comments
        comments_response = youtube.commentThreads().list(
            videoId=video_id,
            part="snippet",
            textFormat="plainText",
            maxResults=50  # You can adjust the number of comments to retrieve
        ).execute()

        comments = [item['snippet']['topLevelComment']['snippet']['textDisplay'] for item in comments_response['items']]

        # Initialize a list to store sentiment results for this video's comments
        video_sentiments = []

        # Process comments in smaller segments to avoid exceeding the model's max sequence length
        for comment in comments:
            segments = [comment[i:i+max_sequence_length] for i in range(0, len(comment), max_sequence_length)]

            # Perform sentiment analysis on each comment segment
            for segment in segments:
                sentiment_results = nlp(segment)
                video_sentiments.extend(sentiment_results)

        video_data.append({
            'title': title,
            'score': score,
            'sentiment_results': video_sentiments
        })

    except HttpError as e:
        if e.resp.status == 403 and "commentsDisabled" in str(e):
            print(f"Comments are disabled for the video with ID: {video_id}")
        else:
            print(f"An error occurred while processing video with ID: {video_id}")

# Sort videos by score in descending order
sorted_videos = sorted(video_data, key=lambda x: x['score'], reverse=True)

# Print the top 30 videos, their scores, and sentiment probabilities
print("Top 30 Videos:")
for i, video_info in enumerate(sorted_videos[:30], start=1):
    print(f"{i}. {video_info['title']} - Score: {video_info['score']:.2f}")
    print("Sentiment Probabilities:")
    for sentiment in video_info['sentiment_results']:
        print(f"{sentiment['label']} ({sentiment['score']:.2f})")
    print()
