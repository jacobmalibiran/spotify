PROMPTS = {
    "V1": """Prompt: Analyze the following list of songs and return:

1. Confidence scores for the presence of the following music genres in the entire playlist:
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

3. For each individual song, provide confidence scores for the same music genres listed above.

The response should be in JSON format with the following structure:
{
  "genre_confidence": {
    "Pop": 0.85,
    "Hip-Hop": 0.65,
    ...
  },
  "theme": "chill late-night vibes",
  "songs": [
    {
      "title": "Song Title 1",
      "artist": "Artist Name 1",
      "genre_confidence": {
        "Pop": 0.90,
        "Hip-Hop": 0.10,
        ...
      }
    },
    {
      "title": "Song Title 2",
      "artist": "Artist Name 2",
      "genre_confidence": {
        "Pop": 0.20,
        "Hip-Hop": 0.70,
        ...
      }
    }
    // more songs here
  ]
}

Ensure consistency in formatting. Avoid explanations—only return the JSON object. In the return object, Do not return anything else besides the JSON object.

List of songs: "{PROMPT}"
"""
}
