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

2. Generate a high-level theme that accurately captures the unique vibe of the playlist. Consider multiple factors, including:

Mood or emotion (e.g., melancholic, euphoric, aggressive)

Genre or subgenre (e.g., UK garage, dream pop, phonk, funk carioca)

Listening context (e.g., late-night drive, gym session, studying)

Era or time period (e.g., early 2000s, 90s nostalgia)

Storyline or narrative arc, if applicable

Signature sound characteristics (e.g., distorted bass, ambient pads, chopped vocals)

Be specific and culturally informed. Use concise, vivid language that paints a mental picture of the setting and sound. Avoid generic or overused descriptions like “chill vibes” or “R&B fusion” unless they are truly fitting. Identify underground or global music influences when relevant. The theme should feel authentic and contextually meaningful to the songs in the playlist.

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

Ensure consistency in formatting. ONLY return the JSON object, no other text or explanations. For the genre confidence, order with the most prominent genre on the top, to the least prominent genres on the bottom.

List of songs: "{PROMPT}"
""",
"V2": """Prompt: Analyze the following list of songs and return:

1. Identify a high-level theme or mood of the playlist, based on the song titles and artists (e.g., "party", "melancholy", "road trip", "romantic", "hype", "chill", etc.).

2. For each individual song:
    - Provide the title
    - Provide the artist
    - Provide a confidence score (0.0 to 1.0) indicating how well the song fits this specific theme: "{THEME}"

The response should be in JSON format with the following structure:
{
  "theme": "chill late-night vibes",
  "songs": [
    {
      "title": "Song Title 1",
      "artist": "Artist Name 1",
      "theme_fit_confidence": 0.95
    },
    {
      "title": "Song Title 2",
      "artist": "Artist Name 2",
      "theme_fit_confidence": 0.45
    }
    // more songs here
  ]
}

Do not include genre confidence or any explanations. ONLY return the JSON object, no other text or explanations

List of songs: "{PROMPT}"
"""
}
