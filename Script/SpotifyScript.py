import requests
import pandas as pd
import time

# Load the dataset with the appropriate encoding
file_path = 'spotify-2023.csv'
spotify_data = pd.read_csv(file_path, encoding='ISO-8859-1')

# Your Spotify API Credentials
client_id = 'your id'
client_secret = 'your secret'

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

# Function to get track ID from Spotify API
def get_track_id(track_name, artist_name, access_token):
    url = "https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "q": f"track:{track_name} artist:{artist_name}",
        "type": "track",
        "limit": 1
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if data['tracks']['items']:
        return data['tracks']['items'][0]['id']
    return None

# Function to get track details
def get_track_details(track_id, access_token):
    if track_id:
        url = f"https://api.spotify.com/v1/tracks/{track_id}"
        response = requests.get(url, headers={'Authorization': f'Bearer {access_token}'})
        if response.status_code == 429:  # Rate limiting
            time.sleep(int(response.headers.get('Retry-After', 1)))
            response = requests.get(url, headers={'Authorization': f'Bearer {access_token}'})
        response.raise_for_status()
        json_data = response.json()
        image_url = json_data['album']['images'][0]['url']
        return image_url
    return None

# Print the column names to debug
print("Columns in CSV:", spotify_data.columns)

# Check if 'track_name' and 'artist_name' columns exist
if 'track_name' not in spotify_data.columns or 'artist_name' not in spotify_data.columns:
    raise KeyError("Columns 'track_name' or 'artist_name' not found in CSV file")

# Get track IDs and image URLs for all tracks in the DataFrame
track_ids = []
image_urls = []

for index, row in spotify_data.iterrows():
    track_id = get_track_id(row['track_name'], row['artist_name'], access_token)
    track_ids.append(track_id)
    image_url = get_track_details(track_id, access_token)
    image_urls.append(image_url)
    print(f"Processed {index + 1}/{len(spotify_data)}: {row['track_name']} - {row['artist_name']}")

# Add the 'image_url' column to the DataFrame
spotify_data['image_url'] = image_urls

# Save the updated DataFrame
spotify_data.to_csv('updated_file.csv', index=False)
