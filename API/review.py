import os
from googleapiclient.discovery import build

# Set your YouTube API key
API_KEY = "AIzaSyAfmf9OE52jKRzqnE5fRyH4nrKfljXyaQ8"  # Replace with your actual API key

# Initialize the YouTube Data API client
youtube = build('youtube', 'v3', developerKey=API_KEY)

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

# Initialize a dictionary to store video scores and comments
video_data = {}

# Define the weights for views, likes, and comments
weight_views = 0.7
weight_likes = 0.3

# Fetch video statistics and comments to calculate scores
for video_id in video_ids:
    # Fetch video statistics
    video_response = youtube.videos().list(
        id=video_id,
        part="statistics"
    ).execute()
    
    statistics = video_response['items'][0]['statistics']
    view_count = int(statistics['viewCount'])
    like_count = int(statistics['likeCount'])
    
    # Calculate the weighted score
    score = (weight_views * view_count) + (weight_likes * like_count)
    
    # Fetch top 20 comments (user reviews)
    comments_response = youtube.commentThreads().list(
        videoId=video_id,
        part="snippet",
        maxResults=300  # Retrieve up to 20 comments
    ).execute()

    
    
    comments = [item['snippet']['topLevelComment']['snippet']['textDisplay'] for item in comments_response['items']]
    
    video_data[video_id] = {
        'score': score,
        'comments': comments
    }

# Sort videos by score in descending order
sorted_videos = sorted(video_data.items(), key=lambda x: x[1]['score'], reverse=True)

# Print the top 30 videos and their scores along with the top 20 comments
print("Top 30 Videos:")
for i, (video_id, data) in enumerate(sorted_videos[:30], start=1):
    video_info = youtube.videos().list(
        id=video_id,
        part="snippet"
    ).execute()
    title = video_info['items'][0]['snippet']['title']
    
    print(f"{i}. {title} - Score: {data['score']:.2f}")
    
    # Print the top 20 comments for this video
    print("Top 20 Comments:")
    for j, comment in enumerate(data['comments'], start=1):
        print(f"{j}. {comment}")
    print("\n")
