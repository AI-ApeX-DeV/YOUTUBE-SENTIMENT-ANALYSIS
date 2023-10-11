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

# Initialize a dictionary to store video view counts
video_views = {}

# Fetch video statistics to get view counts
for video_id in video_ids:
    video_response = youtube.videos().list(
        id=video_id,
        part="statistics"
    ).execute()
    statistics = video_response['items'][0]['statistics']
    view_count = int(statistics['viewCount'])
    video_views[video_id] = view_count

# Sort videos by view count in descending order
sorted_videos = sorted(video_views.items(), key=lambda x: x[1], reverse=True)

# Print the top 30 videos and their view counts
print("Top 30 Videos:")
for i, (video_id, view_count) in enumerate(sorted_videos[:30], start=1):
    video_info = youtube.videos().list(
        id=video_id,
        part="snippet"
    ).execute()
    title = video_info['items'][0]['snippet']['title']
    print(f"{i}. {title} - Views: {view_count}")
