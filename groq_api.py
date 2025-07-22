import requests
from dotenv import load_dotenv
import os
import json
from prompts import PROMPTS
import shared

load_dotenv()

API_KEY = os.getenv("API_KEY")

def analyze_songs(songs, version):
    import api
    # endpoint
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": "Bearer " + API_KEY,
        "Content-Type": "application/json"
    }

    # formats the dict as a string with song name and artists
    song_string = "\n".join([
        f"{i+1}. \"{song['track']['name']}\" by {([artist["name"] for artist in song["track"]["artists"]])}"
        for i, song in enumerate(songs)
    ])


    # full prompt with song list to send to ai
    if version == "V1":
        full_prompt = PROMPTS[version].replace("{PROMPT}", song_string)
    elif version == "V2":
        full_prompt = PROMPTS[version].replace("{THEME}", shared.main_playlist['analysis']['theme']).replace("{PROMPT}", song_string)

    payload = {
        "model": "llama3-70b-8192",  # Or llama3, etc.
        "messages": [
            {"role": "user", "content": full_prompt}
        ],
        # temperature handles consistency and randomness, lower temp is consistent and less random - precise
        # higher temp is less consistent and more random - good for creative wriitng or brainstorming
        "temperature": 0.3
    }

    


    response = requests.post(url, json=payload, headers=headers)
    response_data = response.json()
    model_output = response_data["choices"][0]["message"]["content"]
    parsed_json = json.loads(model_output)
    #entire
    #print(parsed_json)
    #theme
    #print(parsed_json["theme"])
    #genres
    #print(parsed_json["genre_confidence"])

    response.raise_for_status()
    return parsed_json
