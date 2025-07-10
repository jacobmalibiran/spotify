import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")

def analyze_songs(songs):
    url = "https://api.groq.com/v1/analyze"  # Replace with actual endpoint
    headers = {
        "Authorization": "Bearer " + API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "songs": songs
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    print(response.json())
    return response.json()
