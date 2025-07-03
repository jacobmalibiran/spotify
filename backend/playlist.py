from dotenv import load_dotenv
import os
import base64
import json
from requests import post, get
import urllib.parse

load_dotenv()

# loads sensitive info
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")


scopes = "playlist-read-private"
auth_url = "https://accounts.spotify.com/authorize"
params = {
    "client_id": client_id,
    "response_type": "code",
    "redirect_uri": redirect_uri,
    "scope": scopes,
}

#gets data  from url and
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


def get_playlists_from_user(token):
    url = f"https://api.spotify.com/v1/me/playlists"
    json_result = spotify_get(token, url)
    return json_result["items"]

def get_songs_in_playlist(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    json_result = spotify_get(token, url)
    return json_result["tracks"]["items"]

def main():
    print("Go to the following URL:")
    print(auth_url + "?" + urllib.parse.urlencode(params))
    code = input("Enter ?code: " )
    #this token is different from spotify.py token b/c it has code auth from user to get private information
    token = get_user_token(code)
    playlists = get_playlists_from_user(token)

    playlist_dict = {}
    for idx, playlist in enumerate(playlists, start=1):
        print(f"{idx}. {playlist["name"]}")
        playlist_dict[idx] = playlist["id"]

    try:
        choice = int(input("Select an album number to view songs: "))
        playlist_id = playlist_dict.get(choice)
        if playlist_id:
            songs = get_songs_in_playlist(token, playlist_id)
            #here
            print("Songs in the selected album:")
            for idx, song in enumerate(songs, start=1):
                artist_names = ", ".join([artist["name"] for artist in song["track"]["artists"]])
                print(f"{idx}. {song["track"]["name"]} - {artist_names}")
        else:
            print("Invalid selection")

    except ValueError:
        print("Please enter a valid number.")


main()