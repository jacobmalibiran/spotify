import requests
from dotenv import load_dotenv
import os
from prompts import PROMPTS
import orjson

load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("Missing Groq API key. Set API_KEY in the environment.")

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def _build_song_string(songs):
    entries = []
    for idx, song in enumerate(songs, start=1):
        track = song.get("track", {})
        title = track.get("name", "Unknown Title")
        artists = track.get("artists") or []
        artist_names = ", ".join(a.get("name", "Unknown Artist") for a in artists)
        entries.append(f'{idx}. "{title}" by {artist_names}')
    return "\n".join(entries) if entries else "The playlist is empty."


def _build_prompt(version, song_string, **kwargs):
    """Fill in a prompt template by version. Pass extra template variables as kwargs."""
    template = PROMPTS.get(version)
    if template is None:
        raise ValueError(f"Unsupported prompt version: {version}")
    prompt = template.replace("{PROMPT}", song_string)
    for key, value in kwargs.items():
        prompt = prompt.replace(f"{{{key}}}", str(value))
    return prompt


def _call_groq(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant. Return your response strictly as valid JSON only. Do not include any explanations or prose.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
    }
    response = requests.post(GROQ_URL, json=payload, headers=headers)
    if response.status_code >= 400:
        try:
            error_payload = response.json()
            if (
                isinstance(error_payload, dict)
                and error_payload.get("error", {}).get("code") == "model_decommissioned"
            ):
                raise RuntimeError(
                    f"Groq model '{GROQ_MODEL}' is deprecated. "
                    "Set GROQ_MODEL to a currently supported model."
                )
        except ValueError:
            pass
        response.raise_for_status()
    return response


def _parse_groq_response(response):
    message_content = response.json()["choices"][0]["message"]["content"]
    if isinstance(message_content, list):
        model_output = "".join(
            chunk.get("text", "")
            for chunk in message_content
            if isinstance(chunk, dict) and chunk.get("type") == "text"
        ).strip()
    else:
        model_output = str(message_content).strip()

    if not model_output:
        raise ValueError("Groq response contained no text.")

    if model_output.startswith("```"):
        model_output = model_output.strip().strip("`")
        if model_output.lower().startswith("json"):
            model_output = model_output[4:].lstrip()

    return orjson.loads(model_output)


def analyze_songs(songs, version, **kwargs):
    """
    Analyze a list of Spotify track objects with a Groq LLM.

    version: key into PROMPTS (e.g. "V1", "V2")
    kwargs:  extra template variables the prompt version needs (e.g. THEME="late-night drive")
    """
    song_string = _build_song_string(songs)
    prompt = _build_prompt(version, song_string, **kwargs)
    try:
        response = _call_groq(prompt)
        return _parse_groq_response(response)
    except Exception as e:
        print("Error analyzing songs:", e)
        return None
