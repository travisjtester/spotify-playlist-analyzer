# Import required libraries
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

# Set up Spotify API credentials using environment variables
client_credentials_manager = SpotifyClientCredentials(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET')
)

# Create Spotify object to interact with the API
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

# Define the playlist URL
playlist_link = "https://open.spotify.com/playlist/37i9dQZF1DWYMokBiQj5qF?si=6c0ca7db899c47cd"

# Extract playlist ID from URL
# Split the URL by '/' and take the last part, then split by '?' and take the first part
playlist_url = playlist_link.split("/")[-1].split('?')[0]

# Fetch tracks from the playlist
tracks = sp.playlist_tracks(playlist_url)

# Extract album information
album_list = []
for row in tracks['items']:
    album_id = row['track']['album']['id']
    album_name = row['track']['album']['name']
    album_release_date = row['track']['album']['release_date']
    album_total_tracks = row['track']['album']['total_tracks']
    album_url = row['track']['album']['external_urls']['spotify']
    album_element = {'album_id' :album_id, 'name' :album_name, 'release_date' :album_release_date,
                        'total_tracks' :album_total_tracks, 'url' :album_url}
    album_list.append(album_element)

# Extract artist information
artist_list = []
for item in tracks['items']:
    for artist in item['track']['artists']:
        artist_dict = {
            'artist_id': artist['id'],
            'artist_name': artist['name'],
            'external_url': artist['external_urls']['spotify']
        }
        artist_list.append(artist_dict)

# Extract song information
song_list = []
for row in tracks['items']:
    song_id = row['track']['id']
    song_name = row['track']['name']
    song_duration = row['track']['duration_ms']
    song_url = row['track']['external_urls']['spotify']
    song_popularity = row['track']['popularity']
    song_added= row['added_at']
    album_id = row['track']['album']['id']
    artist_id = row['track']['album']['artists'][0]['id']
    song_element = {'song_id' :song_id, 'song_name' :song_name, 'duration_ms' :song_duration, 'url' :song_url,
                    'popularity' :song_popularity, 'song_added' :song_added, 'album_id' :album_id,
                    'artist_id' :artist_id
                    }
    song_list.append(song_element)

# Create DataFrames
album_df = pd.DataFrame.from_dict(album_list)
artist_df = pd.DataFrame.from_dict(artist_list)
song_df = pd.DataFrame.from_dict(song_list)

# Remove duplicate entries from album_df and artist_df
# This ensures each album and artist is represented only once in their respective DataFrames
album_df = album_df.drop_duplicates(subset=['album_id'])
artist_df = artist_df.drop_duplicates(subset=['artist_id'])

# Convert 'release_date' in album_df and 'song_added' in song_df to datetime format
# This allows for easier date-based operations and analysis
album_df['release_date'] = pd.to_datetime(album_df['release_date'])
song_df['song_added'] = pd.to_datetime(song_df['song_added'])

# Uncomment the following line to display the first few rows of the DataFrame
print(artist_df)

# Note: Tutorial stopped at end of Video 1