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
if not API_KEY:
    raise RuntimeError("Missing Groq API key. Set API_KEY in the environment.")

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

def analyze_songs(songs, version):
    import api  # noqa: F401  # ensure Flask app is loaded before making external call

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": "Bearer " + API_KEY,
        "Content-Type": "application/json"
    }

    song_entries = []
    for idx, song in enumerate(songs, start=1):
        track = song.get("track", {})
        title = track.get("name", "Unknown Title")
        artists = track.get("artists") or []
        artist_names = ", ".join(artist.get("name", "Unknown Artist") for artist in artists)
        song_entries.append(f'{idx}. "{title}" by {artist_names}')
    song_string = "\n".join(song_entries) if song_entries else "The playlist is empty."

    if version == "V1":
        full_prompt = PROMPTS[version].replace("{PROMPT}", song_string)
    elif version == "V2":
        theme = shared.main_playlist['analysis']['theme'] if shared.main_playlist else "unknown theme"
        full_prompt = PROMPTS[version].replace("{THEME}", theme).replace("{PROMPT}", song_string)
    else:
        raise ValueError(f"Unsupported prompt version: {version}")

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Return your response strictly as valid JSON only. Do not include any explanations or prose."},
            {"role": "user", "content": full_prompt}
        ],
        "temperature": 0.1
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code >= 400:
        print("Groq API error:", response.status_code)
        try:
            error_payload = response.json()
            print(error_payload)
            if (
                isinstance(error_payload, dict)
                and error_payload.get("error", {}).get("code") == "model_decommissioned"
            ):
                raise RuntimeError(
                    f"Groq model '{GROQ_MODEL}' is deprecated. "
                    "Set GROQ_MODEL to a currently supported model."
                )
        except ValueError:
            print(response.text)
        response.raise_for_status()

    try:
        response_data = response.json()
        message_content = response_data["choices"][0]["message"]["content"]
        if isinstance(message_content, list):
            text_chunks = [
                chunk.get("text", "")
                for chunk in message_content
                if isinstance(chunk, dict) and chunk.get("type") == "text"
            ]
            model_output = "".join(text_chunks).strip()
        else:
            model_output = str(message_content).strip()

        if not model_output:
            raise ValueError("Groq response contained no text.")

        print("MODEL OUTPUT:\n", model_output)
        if model_output.startswith("```"):
            model_output = model_output.strip().strip("`")
            if model_output.lower().startswith("json"):
                model_output = model_output[4:].lstrip()
        parsed_json = orjson.loads(model_output)
        print("PARSED JSON:\n", parsed_json)
        return parsed_json
    except Exception as e:
        print("Error parsing model output:", e)
        print("Raw response:", response.text)
        return None
