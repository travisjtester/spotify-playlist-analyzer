# Import required libraries
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.cache_handler import CacheFileHandler
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set up a custom cache handler
cache_handler = CacheFileHandler(cache_path='.spotify_cache')

# Set up Spotify API credentials using environment variables
client_credentials_manager = SpotifyClientCredentials(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
    cache_handler=cache_handler
)

# Create Spotify object to interact with the API
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

# Define Functions (extract meta data, album info, artist info, song info, etc)

# Extract playlist metadata info
def extract_playlist_metadata(sp, playlist_id):
    playlist = sp.playlist(playlist_id)
    return {
        'name': playlist['name'],
        'description': playlist['description'],
        'followers': playlist['followers']['total'],
        'total_tracks': playlist['tracks']['total'],
        'owner': playlist['owner']['display_name'],
        'public': playlist['public'],
        'collaborative': playlist['collaborative'],
        'snapshot_id': playlist['snapshot_id']
    }

# Extract album info from a track
def extract_album_info(track):
    album = track['album']
    album_id = album['id']

    # Get additional album details
    try:
        album_details = sp.album(album_id)
    except:
        album_details = {}

    return {
        'album_id': album_id,
        'name': album['name'],
        'release_date': album['release_date'],
        'total_tracks': album['total_tracks'],
        'url': album['external_urls']['spotify'],
        'label': album_details.get('label'),
        'popularity': album_details.get('popularity'),
        'album_type': album_details.get('album_type'),
        'images': album_details.get('images')[0]['url'] if album_details.get('images') else None
    }

# Extract artist information
def extract_artist_info(artist):
    artist_id = artist['id']

    # Get additional artists details
    try:
        artist_details = sp.artist(artist_id)
    except:
        artist_details = {}
    return {
        'artist_id': artist_id,
        'artist_name': artist['name'],
        'external_url': artist['external_urls']['spotify'],
        'popularity': artist_details.get('popularity'),
        'followers': artist_details.get('followers', {}).get('total'),
        'genres': artist_details.get('genres', []),
        'images': artist_details.get('images')[0]['url'] if artist_details.get('images') else None
    }

# Extract song information from a playlist item
def extract_song_info(item):
    track = item['track']
    song_id = track['id']

    # Get audio features
    try:
        audio_features = sp.audio_features([song_id])[0]
    except:
        audio_features = {}

    return {
        'song_id': song_id,
        'song_name': track['name'],
        'duration_ms': track['duration_ms'],
        'url': track['external_urls']['spotify'],
        'popularity': track['popularity'],
        'song_added': item['added_at'],
        'album_id': track['album']['id'],
        'artist_id': track['album']['artists'][0]['id'],
        'danceability': audio_features.get('danceability'),
        'energy': audio_features.get('energy'),
        'key': audio_features.get('key'),
        'loudness': audio_features.get('loudness'),
        'mode': audio_features.get('mode'),
        'speechiness': audio_features.get('speechiness'),
        'acousticness': audio_features.get('acousticness'),
        'instrumentalness': audio_features.get('instrumentalness'),
        'liveness': audio_features.get('liveness'),
        'valence': audio_features.get('valence'),
        'tempo': audio_features.get('tempo'),
        'time_signature': audio_features.get('time_signature')
    }

# Get all tracks from a playlist, handling pagination
def get_playlist_tracks(sp,playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

# Main Execution
def main():
    # Define the playlist URL, then Extract/Split playlist ID out of URL
    playlist_link = "https://open.spotify.com/playlist/37i9dQZF1DWYMokBiQj5qF?si=6c0ca7db899c47cd"
    playlist_id = playlist_link.split("/")[-1].split('?')[0]

    # Fetch tracks from the playlist
    tracks = get_playlist_tracks(sp, playlist_id)

    # Extract information
    album_list = [extract_album_info(item['track']) for item in tracks]
    artist_list = [extract_artist_info(artist) for item in tracks for artist in item['track']['artists']]
    song_list = [extract_song_info(item) for item in tracks]
    playlist_metadata = extract_playlist_metadata(sp,playlist_id)

    # Create DataFrames
    album_df = pd.DataFrame(album_list).drop_duplicates(subset=['album_id'])
    artist_df = pd.DataFrame.from_dict(artist_list).drop_duplicates(subset=['artist_id'])
    song_df = pd.DataFrame.from_dict(song_list)
    playlist_df = pd.DataFrame([playlist_metadata])

    # Convert date columns to datetime
    album_df['release_date'] = pd.to_datetime(album_df['release_date'])
    song_df['song_added'] = pd.to_datetime(song_df['song_added'])

    # Print DataFrames (for debugging)
    print(album_df.head())
    print(artist_df.head())
    print(song_df.head())
    print(playlist_df)

    # Here you would call the functions to get playlist metadata and genre info
    # And then the functions to get additional artist and album details

    # Note: Tutorial stopped at end of Video 1; End of Day 3

if __name__ == "__main__":
    main()