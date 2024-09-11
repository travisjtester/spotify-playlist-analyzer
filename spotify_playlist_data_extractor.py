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

# Extract playlist metadata info
def get_playlist_metadata(sp, playlist_id):
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
    return {
        'album_id': album['id'],
        'name': album['name'],
        'release_date': album['release_date'],
        'total_tracks': album['total_tracks'],
        'url': album['external_urls']['spotify']
    }

# Extract artist information
def extract_artist_info(artist):
    return {
        'artist_id': artist['id'],
        'artist_name': artist['name'],
        'external_url': artist['external_urls']['spotify']
    }

# Extract song information from a playlist item
def extract_song_info(item):
    track = item['track']
    return {
        'song_id': track['id'],
        'song_name': track['name'],
        'duration_ms': track['duration_ms'],
        'url': track['external_urls']['spotify'],
        'popularity': track['popularity'],
        'song_added': item['added_at'],
        'album_id': track['album']['id'],
        'artist_id': track['album']['artists'][0]['id'],
    }

# Get all tracks from a playlist, handling pagination
def get_playlist_tracks(sp,playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def main():
    # Define the playlist URL, then Extract/Split playlist ID out of URL
    playlist_link = "https://open.spotify.com/playlist/37i9dQZF1DWYMokBiQj5qF?si=6c0ca7db899c47cd"
    playlist_id = playlist_link.split("/")[-1].split('?')[0]

    # Get playlist metadata
    playlist_metadata = get_playlist_metadata(sp,playlist_id)
    playlist_df = pd.DataFrame([playlist_metadata])

    # Fetch tracks from the playlist
    tracks = get_playlist_tracks(sp, playlist_id)

    # Extract information
    album_list = [extract_album_info(item['track']) for item in tracks]
    artist_list = [extract_artist_info(artist) for item in tracks for artist in item['track']['artists']]
    song_list = [extract_song_info(item) for item in tracks]

    # Create DataFrames
    album_df = pd.DataFrame(album_list).drop_duplicates(subset=['album_id'])
    artist_df = pd.DataFrame.from_dict(artist_list).drop_duplicates(subset=['artist_id'])
    song_df = pd.DataFrame.from_dict(song_list)

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