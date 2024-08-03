import requests
import pandas as pd
import time
import urllib.parse

# Your Spotify API Credentials
client_id = '254950b2a631433ea016f8caf7f0ec64'
client_secret = '1033983d1e474e40bd6301f5b2757e06'

# Function to get Spotify access token
def get_spotify_token(client_id, client_secret):
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    auth_response.raise_for_status()
    auth_data = auth_response.json()
    return auth_data['access_token']

# Get Access Token
access_token = get_spotify_token(client_id, client_secret)

# Function to search for tracks and get their IDs
def search_tracks(track_name, artist_name, access_token):
    track_id = []
    for track_name, artist_name in zip(track_name, artist_name):
        query = f"{track_name} artist:{artist_name}"
        encoded_query = urllib.parse.quote(query)
        url = f"https://api.spotify.com/v1/search?q={encoded_query}&type=track"
        response = requests.get(url, headers={'Authorization': f'Bearer {access_token}'})
        if response.status_code == 429:  # Rate limiting
            time.sleep(int(response.headers.get('Retry-After', 1)))
            response = requests.get(url, headers={'Authorization': f'Bearer {access_token}'})
        response.raise_for_status()
        json_data = response.json()
        try:
            track_id = json_data['tracks']['items'][0]['id']
            track_id.append(track_id)
        except (KeyError, IndexError):
            track_id.append(None)
    return track_id

# Function to get track details
def get_track_details(track_id, access_token):
    track_images = []
    for track_id in track_id:
        if track_id:
            url = f"https://api.spotify.com/v1/tracks/{track_id}"
            response = requests.get(url, headers={'Authorization': f'Bearer {access_token}'})
            if response.status_code == 429:  # Rate limiting
                time.sleep(int(response.headers.get('Retry-After', 1)))
                response = requests.get(url, headers={'Authorization': f'Bearer {access_token}'})
            response.raise_for_status()
            json_data = response.json()
            image_url = json_data['album']['images'][0]['url']
            track_images.append(image_url)
        else:
            track_images.append(None)
    return track_images

# Read your DataFrame (replace 'spotify-2023.csv' with the path to your CSV file)
df_spotify = pd.read_csv('spotify-2023.csv', encoding='ISO-8859-1')

# Print the column names to debug
print("Columns in CSV:", df_spotify.columns)

# Check if 'track_name' and 'artist_name' columns exist
if 'track_name' not in df_spotify.columns or 'artist_name' not in df_spotify.columns:
    raise KeyError("Columns 'track_name' or 'artist_name' not found in CSV file")

# Get track IDs for all tracks in the DataFrame
track_id = search_tracks(df_spotify['track_name'], df_spotify['artist_name'], access_token)

# Get image URLs for all track IDs
image_urls = get_track_details(track_id, access_token)

# Add the 'image_url' column to the DataFrame
df_spotify['image_url'] = image_urls

# Save the updated DataFrame (replace 'updated_file.csv' with your desired output file name)
df_spotify.to_csv('updated_file.csv', index=False)
