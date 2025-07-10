PROMPTS = {
    "V1": """Prompt: Analyze the following list of songs and return confidence scores for the presence of the following music genres:

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

The response should be in JSON format with each genre as a key and its confidence score as a decimal between 0 and 1 (inclusive), representing the likelihood that the playlist contains that genre. The sum of all confidence scores does not need to equal 1.

Example Input:
- "Hotline Bling" by Drake  
- "Blinding Lights" by The Weeknd  
- "Stay" by Kid LAROI and Justin Bieber

Example Output:
{
  "Pop": 0.85,
  "Hip-Hop": 0.65,
  "R&B": 0.60,
  "Rock": 0.05,
  "Electronic": 0.30,
  "Country": 0.00,
  "Jazz": 0.00,
  "Classical": 0.00,
  "Indie": 0.10,
  "Metal": 0.00,
  "Folk": 0.00,
  "Reggae": 0.00,
  "Other": 0.02
}

Ensure consistency in formatting and avoid including explanations—only return the JSON object.

List of songs: "{PROMPT}"
""",

}