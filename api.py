from flask import Flask, request, render_template, redirect, url_for, session
import urllib.parse
from playlist import auth_url, get_user_token, params, get_playlists_from_user, get_songs_in_playlist, get_playlist_title
from groq_api import analyze_songs
import os
import json

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

main_playlist = None
secondary_playlist = None

# index route
# these routes are for my own server, NOT the spotify api urls
@app.route("/")
def index():
    session.clear()
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
    if session.get("token") is None:
        session["token"] = token
        

    # Just return playlist names and ids for now, or render a template
    # variable = variable is no longer used because of session, but kept just in case
    #return render_template("playlists.html", playlists=playlists, token=token, playlist_dict=playlist_dict)
    return redirect(url_for('playlists'))  # Redirect to playlists route after login


@app.route("/playlists")
def playlists():
    if session.get("token") is None:
        print("no token")
        return redirect(url_for("index"))
    
    token = session.get("token")

    playlists = get_playlists_from_user(token)

    # key is id value is spotify playlist id
    playlist_dict = {idx+1: p["id"] for idx, p in enumerate(playlists)}

    global main_playlist
    print(main_playlist)
    global secondary_playlist

    return render_template("playlists.html", playlists=playlists, token=token, playlist_dict=playlist_dict, main_playlist=main_playlist, secondary_playlist=secondary_playlist)

# route for specific playlist
@app.route("/playlists/<playlist_id>")
def playlist_songs(playlist_id):
    token = request.args.get("token")
    # if theres no token or expired goes back to index to login again
    if not token:
        return redirect(url_for("index"))
    
    #playlist title
    playlist_name = get_playlist_title(token, playlist_id)

    # dict of songs and other information
    songs = get_songs_in_playlist(token, playlist_id)

    # json response of playlist genre breakdown
    # pared_json variable in groq_api
    analysis = analyze_songs(songs)

    return render_template("songs.html", songs=songs, token=token, analysis=analysis, playlist_name=playlist_name, playlist_id=playlist_id)


@app.route("/save_main", methods=["POST"])
def save_main():
    global main_playlist
    playlist_name = request.form.get("playlist_name")
    analysis = request.form.get("analysis")
    playlist_id = request.form.get("playlist_id")
    if analysis and playlist_name:
        main_playlist = {
            "name": playlist_name,
            "playlist_id": playlist_id,
            "analysis": json.loads(analysis)
        }
    return redirect(url_for("playlists"))

@app.route("/save_secondary", methods=["POST"])
def save_secondary():
    global secondary_playlist
    playlist_name = request.form.get("playlist_name")
    analysis = request.form.get("analysis")
    playlist_id = request.form.get("playlist_id")
    if analysis and playlist_name:
        secondary_playlist = {
            "name": playlist_name,
            "playlist_id": playlist_id,
            "analysis": json.loads(analysis)
        }
    return redirect(url_for("playlists"))

@app.route("/compare_playlists")
def compare_playlists():
    global main_playlist, secondary_playlist
    return render_template('compare.html', main_playlist=main_playlist, secondary_playlist=secondary_playlist)

    

if __name__ == "__main__":
    app.run(debug=True)
