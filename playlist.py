from flask import Flask, request, render_template, redirect, url_for
from dotenv import load_dotenv
import os
import base64
import json
from requests import post, get
import urllib.parse

load_dotenv()

app = Flask(__name__)


# loads sensitive info, client fields are associated with the app, not specific user account
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
# where to direct after user login
redirect_uri = os.getenv("REDIRECT_URI")


scopes = "playlist-read-private"
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


def get_playlists_from_user(token):
    url = f"https://api.spotify.com/v1/me/playlists"
    json_result = spotify_get(token, url)
    # returns a list of items which contains all the playlists a user has, can loop through to find playlist name and playlist id
    return json_result["items"]

def get_songs_in_playlist(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    json_result = spotify_get(token, url)
    # returns a list of items which contain all the songs, can loop through to find each song and associated information
    return json_result["tracks"]["items"]


# index route
@app.route("/")
def index():
    # Render HTML with auth URL for user to click
    # urllib.parse.urlencode coverts dictionary into properly formatted query string
    spotify_auth_url = auth_url + "?" + urllib.parse.urlencode(params)
    return render_template("index.html", spotify_auth_url=spotify_auth_url)

# route after login
@app.route("/callback")
def callback():
    code = request.args.get("code")
    # Error if no code is found
    if not code:
        return "Error: No code found in callback URL."

    token = get_user_token(code)
    
    playlists = get_playlists_from_user(token)

    # key is id value is spotify playlist id
    playlist_dict = {idx+1: p["id"] for idx, p in enumerate(playlists)}

    # Just return playlist names and ids for now, or render a template
    return render_template("playlists.html", playlists=playlists, token=token, playlist_dict=playlist_dict)

# route for specific playlist
@app.route("/playlists/<playlist_id>")
def playlist_songs(playlist_id):
    token = request.args.get("token")
    # if theres no token or expired goes back to index to login again
    if not token:
        return redirect(url_for("index"))
    
    songs = get_songs_in_playlist(token, playlist_id)
    return render_template("songs.html", songs=songs, token=token)

if __name__ == "__main__":
    app.run(debug=True)


def main():
    # for terminal testings
    print("Go to the following URL:")
    print(auth_url + "?" + urllib.parse.urlencode(params))
    code = input("Enter ?code: " )
    #this token is different from spotify.py token b/c it has code auth from user to get private information
    token = get_user_token(code)
    playlists = get_playlists_from_user(token)

    playlist_dict = {}
    # playlists has all the playlists, looping through this will give playlist, which will have an individual playlist at each index
    for idx, playlist in enumerate(playlists, start=1):
        print(f"{idx}. {playlist["name"]}")
        # maps the indiviudal playlist index to the spotify playlist id which is used to find all tracks inside playlist
        playlist_dict[idx] = playlist["id"]

    try:
        choice = int(input("Select an album number to view songs: "))
        # user chooses an index, in value in dictionary at index is playlist id
        playlist_id = playlist_dict.get(choice)
        if playlist_id:
            # calls function to get list of songs inside a playlist, can loop through to get each indiviudal song and associated information
            songs = get_songs_in_playlist(token, playlist_id)
            print("Songs in the selected album:")
            for idx, song in enumerate(songs, start=1):
                artist_names = ", ".join([artist["name"] for artist in song["track"]["artists"]])
                print(f"{idx}. {song["track"]["name"]} - {artist_names}")
        else:
            print("Invalid selection")

    except ValueError:
        print("Please enter a valid number.")


main()