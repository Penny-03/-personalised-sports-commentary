from groq import Groq
import json

client = Groq(api_key="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")

PERSONAS = {
    "beginner": "You explain football simply. Short sentences. Define any term a newcomer wouldn't know. Warm and encouraging tone.",
    "fan": "You are a passionate, emotional fan commentator. React to the action with excitement or frustration. Use colloquial football language.",
    "analyst": "You are a tactical analyst. Focus on formations, pressing triggers, positional play, and strategic patterns. Precise and calm.",
}

def generate_commentary(game_state: dict, persona: str) -> str:
    persona_desc = PERSONAS.get(persona, PERSONAS["fan"])
    prompt = f"""
{persona_desc}

Current match situation:
{json.dumps(game_state, indent=2)}

Generate exactly ONE sentence of live commentary for this moment.
Do not start with 'I' or refer to yourself.
"""
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=80,
        temperature=0.85,
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    state = {
        "home_team": "Inter", "away_team": "Milan",
        "home_score": 1, "away_score": 0,
        "minute": 67, "action": "Corner kick being taken",
        "last_event_player": "Lautaro Martinez",
        "last_event_type": "Goal"
    }
    for persona in PERSONAS:
        print(f"\n[{persona}]")
        print(generate_commentary(state, persona))
