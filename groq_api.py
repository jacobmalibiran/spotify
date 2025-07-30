import requests
from dotenv import load_dotenv
import os
import json
from prompts import PROMPTS
import shared
import re
import orjson

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
    # V1 is to analysi genre confidence for the entire playlist and for each individual song
    if version == "V1":
        full_prompt = PROMPTS[version].replace("{PROMPT}", song_string)
    # V2 is to analyze the theme confidence for each individual song in the secondary playlist
    elif version == "V2":
        full_prompt = PROMPTS[version].replace("{THEME}", shared.main_playlist['analysis']['theme']).replace("{PROMPT}", song_string)

    payload = {
        "model": "llama3-70b-8192",  # Or llama3, etc.
        "messages": [
            {"role": "user", "content": full_prompt},
            {"role": "system", "content": "You are a helpful assistant. Return your response strictly as valid JSON only. Do not include any explanations or prose."}
        ],
        # temperature handles consistency and randomness, lower temp is consistent and less random - precise
        # higher temp is less consistent and more random - good for creative wriitng or brainstorming
        "temperature": 0.1
    }

    


    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    #print("RESPONSE: ")
    #print(response)

    try:
        response_data = response.json()
        model_output = response_data["choices"][0]["message"]["content"]

        print("MODEL OUTPUT:\n", model_output)
        parsed_json = orjson.loads(model_output)
        print("PARSED JSON:\n", parsed_json)
        return parsed_json
    except (KeyError, json.JSONDecodeError) as e:
        print("Error parsing model output:", e)
        print("Raw response:", response.text)
        return None