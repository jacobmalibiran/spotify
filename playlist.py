from flask import Flask, request, render_template, redirect, url_for
from dotenv import load_dotenv
import os
import base64
import json
from requests import post, get
import urllib.parse
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import requests

load_dotenv()


# loads sensitive info, client fields are associated with the app, not specific user account
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
# where to direct after user login
redirect_uri = os.getenv("REDIRECT_URI")


scopes = "playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private"
# where users will login to get their user info
auth_url = "https://accounts.spotify.com/authorize"

# GET function, gets code; this is used to insert into the url
params = {
    "client_id": client_id,
    "response_type": "code",
    "redirect_uri": redirect_uri,
    "scope": scopes,
}

#gets data from url
def spotify_get(token, url):
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    result.raise_for_status()  # optional, raises error for bad response
    return json.loads(result.content)


# gets token to retrieve info from spotify
# take client id and concatenate to client secret, encode to base64. this is what
# we need to send to get token

def get_user_token(code):
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization" : "Basic " + auth_base64,
        "Content-Type" : "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }

    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token # contains access_token and refresh_token


#authorization header to get info
def get_auth_header(token):
    return {"Authorization" : "Bearer " + token}

# returns spotify user's username
def get_username(token):
    url = f"https://api.spotify.com/v1/me/"
    json_result = spotify_get(token, url)
    return json_result["display_name"]

# gets all playlists from user
def get_playlists_from_user(token):
    url = f"https://api.spotify.com/v1/me/playlists"
    json_result = spotify_get(token, url)
    # returns a list of items which contains all the playlists a user has, can loop through to find playlist name and playlist id
    return json_result["items"]

# returns a list of all the songs in a playlist
def get_songs_in_playlist(token, playlist_id):
    all_songs = []
    limit = 100
    offset = 0

    while True:
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit={limit}&offset={offset}"
        json_result = spotify_get(token, url)
        items = json_result.get("items", [])
        all_songs.extend(items)
        if len(items) < limit:  # No more tracks to fetch
            break
        offset += limit
    return all_songs

# returns the title of a playlist
def get_playlist_title(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    json_result = spotify_get(token, url)
    return json_result["name"]

# calculates the similarity score for song genre to main playlist genre
def genre_similarity_to_playlist(song_genre_confidence, playlist_genre_confidence):
    genres = list(playlist_genre_confidence.keys())
    song_vec = np.array([song_genre_confidence.get(g, 0) for g in genres]).reshape(1, -1)
    playlist_vec = np.array([playlist_genre_confidence.get(g, 0) for g in genres]).reshape(1, -1)
    return float(cosine_similarity(song_vec, playlist_vec)[0][0])

def add_songs_to_playlist(token, playlist_id, selected_songs):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    headers= {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
     
    uris = [f"spotify:track:{song_id}" for song_id in selected_songs]

    payload = {
        "uris": uris
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )
    if response.status_code != 201:
        print("Failed to add songs:", response.json())
    else:
        return "Success!"







