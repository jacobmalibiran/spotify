PROMPTS = {
    "V1": """Prompt: Analyze the following list of songs and return:

1. Confidence scores for the presence of the following music genres:
Pop  
Hip-Hop  
R&B  
Rock  
Electronic  
Country  
Jazz  
Classical  
Indie  
Metal  
Folk  
Reggae  
Other  

2. A high-level theme or mood of the playlist, based on the song titles and artists (e.g., "party", "melancholy", "road trip", "romantic", "hype", "chill", etc.).

The response should be in JSON format with the following structure:
{
  "genre_confidence": {
    "Pop": 0.85,
    "Hip-Hop": 0.65,
    ...
  },
  "theme": "chill late-night vibes"
}

Ensure consistency in formatting. Avoid explanations—only return the JSON object.

List of songs: "{PROMPT}"
"""
}
