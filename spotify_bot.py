# Ganti dengan credentials kamu dari https://developer.spotify.com/dashboard


import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# ⚠️ GANTI DENGAN CREDENTIALS SPOTIFY KAMU
# Dapatkan di: https://developer.spotify.com/dashboard
# CLIENT_ID = 'your_spotify_client_id_here'
# CLIENT_SECRET = 'your_spotify_client_secret_here'

try:
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    ))
except Exception as e:
    print(f"⚠️ Spotify API Error: {e}")
    sp = None

def get_track_query(spotify_url):
    """Mengambil info track dari Spotify URL dan convert ke search query"""
    if not sp:
        return None
    
    try:
        track_id = spotify_url.split('/')[-1].split('?')[0]
        track = sp.track(track_id)
        query = f"{track['name']} {track['artists'][0]['name']}"
        return query
    except Exception as e:
        print(f"Error getting track: {e}")
        return None

def get_playlist_queries(spotify_url):
    """Mengambil semua tracks dari Spotify playlist"""
    if not sp:
        return []
    
    try:
        playlist_id = spotify_url.split('/')[-1].split('?')[0]
        results = sp.playlist_tracks(playlist_id)
        
        queries = []
        for item in results['items']:
            if item['track']:
                track = item['track']
                query = f"{track['name']} {track['artists'][0]['name']}"
                queries.append(query)
        
        return queries
    except Exception as e:
        print(f"Error getting playlist: {e}")
        return []