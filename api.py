from flask import Flask, request, render_template, redirect, url_for, session
import urllib.parse
from playlist import auth_url, get_user_token, params, get_playlists_from_user, get_songs_in_playlist
from groq_api import analyze_songs
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# index route
# these routes are for my own server, NOT the spotify api urls
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
    
    # dict of songs and other information
    songs = get_songs_in_playlist(token, playlist_id)

    # json response of playlist genre breakdown
    # pared_json variable in groq_api
    analysis = analyze_songs(songs)

    return render_template("songs.html", songs=songs, token=token, analysis=analysis)
    

if __name__ == "__main__":
    app.run(debug=True)
