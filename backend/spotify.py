from dotenv import load_dotenv
import os
import base64
import json
from requests import post, get

load_dotenv()

# loads sensitive info
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

# gets token to retrieve info from spotify
# take client id and concatenate to client secret, encode to base64. this is what
# we need to send to get token
def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization" : "Basic " + auth_base64,
        "Content-Type" : "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

#authorization header to get info
def get_auth_header(token):
    return {"Authorization" : "Bearer " + token}

#Searches for artist using their name
def search_for_artist(token, artist_name):
    #endpoint
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    #limit for resutls
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    # to get id the next 
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artists found")
        return 0
    else:
        return json_result[0]

#Searches for songs from an artist using artist id
def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result= get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result

#Shows albums from artist using artist id
def get_albums_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["items"]
    return json_result

#Shows songs in an album using album id
def get_songs_by_album(token, album_id):
    url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["items"]
    return json_result


def main():
    token = get_token()

    artist = input("Enter an artist to search: ")
    result = search_for_artist(token, artist)
    artist_id = result["id"]
    print(result["name"])

    albums = get_albums_by_artist(token, artist_id)

    album_dict = {}

    #prints out album names and creates dict with key as the number and value as the album id
    for idx, album in enumerate(albums, start=1):
        print(f"{idx}. {album["name"]}")
        album_dict[idx] = album["id"]

    try:
        choice = int(input("Select an album number to view songs: "))
        album_id = album_dict.get(choice)
        if album_id:
            songs = get_songs_by_album(token, album_id)
            print("Songs in the selected album:")
            for idx, song in enumerate(songs, start=1):
                print(f"{idx}. {song["name"]}")
        else:
            print("Invalid selection")

    except ValueError:
        print("Please enter a valid number.")

main()


#songs = get_songs_by_artist(token, artist_id)
#for idx, song in enumerate(songs):
 #   print(f"{idx + 1}. {song["name"]}")