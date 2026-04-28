from flask import Flask, request, render_template, redirect, url_for, session
import urllib.parse
from playlist import auth_url, get_user_token, params, get_playlists_from_user, get_songs_in_playlist, get_playlist_title, genre_similarity_to_playlist, get_username, add_songs_to_playlist
from groq_api import analyze_songs
import shared
import os
import json


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")


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

    username = get_username(token)
    playlists = get_playlists_from_user(token)

    # key is id value is spotify playlist id
    playlist_dict = {idx+1: p["id"] for idx, p in enumerate(playlists)}

    return render_template("playlists.html", username=username, playlists=playlists, token=token, playlist_dict=playlist_dict, main_playlist=shared.main_playlist, secondary_playlist=shared.secondary_playlist)

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
    analysis = analyze_songs(songs, "V1")
    print("ANALYSIS VARIABLE: ")
    print(analysis)

    return render_template("songs.html", songs=songs, token=token, analysis=analysis, playlist_name=playlist_name, playlist_id=playlist_id)

# Saves data to global main_playlist variable
@app.route("/save_main", methods=["POST"])
def save_main():
    playlist_name = request.form.get("playlist_name")
    analysis = request.form.get("analysis")
    playlist_id = request.form.get("playlist_id")
    if analysis and playlist_name:
        shared.main_playlist = {
            "name": playlist_name,
            "playlist_id": playlist_id,
            "analysis": json.loads(analysis)
        }
    return redirect(url_for("playlists"))

#Saves data to global secondary_playlist variable
@app.route("/save_secondary", methods=["POST"])
def save_secondary():
    playlist_name = request.form.get("playlist_name")
    analysis = request.form.get("analysis")
    playlist_id = request.form.get("playlist_id")
    song_data = request.form.get("song_data")
    if analysis and playlist_name:
        shared.secondary_playlist = {
            "name": playlist_name,
            "playlist_id": playlist_id,
            "analysis": json.loads(analysis)
        }
    return redirect(url_for("playlists"))

# Compares two playlists, returns a new analysis with theme confidence
@app.route("/compare_playlists")
def compare_playlists():
    songs = get_songs_in_playlist(session.get('token'), shared.secondary_playlist['playlist_id'])
    analysis = analyze_songs(songs, "V2")

    for song in shared.secondary_playlist['analysis']['songs']:
        for match in songs:
            if song['title'] == match['track']['name']:
                song['song_id'] = match['track']['id']


    # goes through all songs in secondary playlist and finds fit score
    # finds genre similarity and theme similarity to calculate fit score, weighted 60% for theme and 40% for genre
    for song in shared.secondary_playlist['analysis']['songs']:
        song['genre_similarity'] = genre_similarity_to_playlist(song['genre_confidence'], shared.main_playlist['analysis']['genre_confidence'])
        for match in analysis['songs']:
                if song['title'].strip().lower() == match['title'].strip().lower() and song['artist'].strip().lower() == match['artist'].strip().lower():
                    song['theme_similarity'] = match['theme_fit_confidence']
                    break
        fit_score = round(0.5 * song['genre_similarity'] + 0.5 * song['theme_similarity'], 2)
        song['fit_score'] = 100 * fit_score
    return render_template('compare.html', main_playlist=shared.main_playlist, secondary_playlist=shared.secondary_playlist, analysis=analysis)

@app.route("/add_songs_to_playlist", methods=["POST"])
def add_songs_to_main_playlist():
    token = session.get('token')
    playlist_id = shared.main_playlist['playlist_id']
    selected_songs = request.form.getlist('selected_songs')
    add_songs_to_playlist(token, playlist_id, selected_songs)
    return redirect(url_for('playlists'))

    

if __name__ == "__main__":
    app.run(debug=True)
