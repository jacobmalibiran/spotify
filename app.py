from flask import Flask, request, render_template, redirect, url_for, session
import urllib.parse
from spotify_client import auth_url, get_user_token, params, genre_similarity_to_playlist, SpotifyClient
from groq_client import analyze_songs
import state
import os
import json


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")


@app.route("/")
def index():
    session.clear()
    spotify_auth_url = auth_url + "?" + urllib.parse.urlencode(params)
    return render_template("index.html", spotify_auth_url=spotify_auth_url)


@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Error: No code found in callback URL."
    session["token"] = get_user_token(code)
    return redirect(url_for("playlists"))


@app.route("/playlists")
def playlists():
    token = session.get("token")
    if not token:
        return redirect(url_for("index"))

    client = SpotifyClient(token)
    user_playlists = client.get_playlists()
    playlist_dict = {idx + 1: p["id"] for idx, p in enumerate(user_playlists)}

    return render_template(
        "playlists.html",
        username=client.get_username(),
        playlists=user_playlists,
        token=token,
        playlist_dict=playlist_dict,
        main_playlist=state.main_playlist,
        secondary_playlist=state.secondary_playlist,
    )


@app.route("/playlists/<playlist_id>")
def playlist_songs(playlist_id):
    token = request.args.get("token")
    if not token:
        return redirect(url_for("index"))

    client = SpotifyClient(token)
    songs = client.get_songs_in_playlist(playlist_id)
    analysis = analyze_songs(songs, "V1")

    song_genres = {}
    if analysis and analysis.get("songs"):
        song_genres = {s["title"].strip().lower(): s["genre_confidence"] for s in analysis["songs"]}

    return render_template(
        "songs.html",
        songs=songs,
        token=token,
        analysis=analysis,
        playlist_name=client.get_playlist_title(playlist_id),
        playlist_id=playlist_id,
        song_genres=song_genres,
    )


@app.route("/save_main", methods=["POST"])
def save_main():
    playlist_name = request.form.get("playlist_name")
    analysis = request.form.get("analysis")
    playlist_id = request.form.get("playlist_id")
    if analysis and playlist_name:
        state.main_playlist = {
            "name": playlist_name,
            "playlist_id": playlist_id,
            "analysis": json.loads(analysis),
        }
    return redirect(url_for("playlists"))


@app.route("/save_secondary", methods=["POST"])
def save_secondary():
    playlist_name = request.form.get("playlist_name")
    analysis = request.form.get("analysis")
    playlist_id = request.form.get("playlist_id")
    if analysis and playlist_name:
        state.secondary_playlist = {
            "name": playlist_name,
            "playlist_id": playlist_id,
            "analysis": json.loads(analysis),
        }
    return redirect(url_for("playlists"))


@app.route("/compare_playlists")
def compare_playlists():
    token = session.get("token")
    client = SpotifyClient(token)

    songs = client.get_songs_in_playlist(state.secondary_playlist["playlist_id"])
    theme = state.main_playlist["analysis"]["theme"]
    analysis = analyze_songs(songs, "V2", THEME=theme)

    # attach song IDs from the fetched track list
    song_id_map = {match["track"]["name"]: match["track"]["id"] for match in songs}
    for song in state.secondary_playlist["analysis"]["songs"]:
        song["song_id"] = song_id_map.get(song["title"])

    # build a lookup for theme-fit scores returned by V2
    theme_fit_map = {
        (m["title"].strip().lower(), m["artist"].strip().lower()): m["theme_fit_confidence"]
        for m in analysis["songs"]
    }

    for song in state.secondary_playlist["analysis"]["songs"]:
        song["genre_similarity"] = genre_similarity_to_playlist(
            song["genre_confidence"], state.main_playlist["analysis"]["genre_confidence"]
        )
        key = (song["title"].strip().lower(), song["artist"].strip().lower())
        song["theme_similarity"] = theme_fit_map.get(key, 0)
        song["fit_score"] = round(100 * (0.5 * song["genre_similarity"] + 0.5 * song["theme_similarity"]), 2)

    return render_template(
        "compare.html",
        main_playlist=state.main_playlist,
        secondary_playlist=state.secondary_playlist,
        analysis=analysis,
    )


@app.route("/add_songs_to_playlist", methods=["POST"])
def add_songs_to_main_playlist():
    token = session.get("token")
    playlist_id = state.main_playlist["playlist_id"]
    selected_songs = request.form.getlist("selected_songs")
    SpotifyClient(token).add_songs_to_playlist(playlist_id, selected_songs)
    return redirect(url_for("playlists"))


if __name__ == "__main__":
    app.run(debug=True)
