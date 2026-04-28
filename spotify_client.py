from dotenv import load_dotenv
import os
import base64
import json
from requests import post, get
import requests
import urllib.parse
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

scopes = "playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private"
auth_url = "https://accounts.spotify.com/authorize"

params = {
    "client_id": client_id,
    "response_type": "code",
    "redirect_uri": redirect_uri,
    "scope": scopes,
}


def get_user_token(code):
    auth_string = client_id + ":" + client_secret
    auth_base64 = str(base64.b64encode(auth_string.encode("utf-8")), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }
    result = post(url, headers=headers, data=data)
    return json.loads(result.content)["access_token"]


def genre_similarity_to_playlist(song_genre_confidence, playlist_genre_confidence):
    genres = list(playlist_genre_confidence.keys())
    song_vec = np.array([song_genre_confidence.get(g, 0) for g in genres]).reshape(1, -1)
    playlist_vec = np.array([playlist_genre_confidence.get(g, 0) for g in genres]).reshape(1, -1)
    return float(cosine_similarity(song_vec, playlist_vec)[0][0])


class SpotifyClient:
    """Wraps all Spotify Web API calls. Add new endpoints as methods here."""

    BASE_URL = "https://api.spotify.com/v1"

    def __init__(self, token):
        self.token = token
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _get(self, url):
        response = get(url, headers=self._headers)
        response.raise_for_status()
        return response.json()

    def _post(self, url, payload):
        response = requests.post(url, headers=self._headers, json=payload)
        response.raise_for_status()
        return response.json()

    def get_username(self):
        return self._get(f"{self.BASE_URL}/me")["display_name"]

    def get_playlists(self):
        return self._get(f"{self.BASE_URL}/me/playlists")["items"]

    def get_playlist_title(self, playlist_id):
        return self._get(f"{self.BASE_URL}/playlists/{playlist_id}")["name"]

    def get_songs_in_playlist(self, playlist_id):
        all_songs = []
        limit = 100
        offset = 0
        while True:
            url = f"{self.BASE_URL}/playlists/{playlist_id}/tracks?limit={limit}&offset={offset}"
            data = self._get(url)
            items = data.get("items", [])
            all_songs.extend(items)
            if len(items) < limit:
                break
            offset += limit
        return all_songs

    def add_songs_to_playlist(self, playlist_id, song_ids):
        url = f"{self.BASE_URL}/playlists/{playlist_id}/items"
        uris = [f"spotify:track:{song_id}" for song_id in song_ids]
        self._post(url, {"uris": uris})
