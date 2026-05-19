import google.generativeai as genai
import json, re

genai.configure(api_key="AIzaSyCaAUuRK86k7LPm8m80EtT0K_2BLIxZ-nA")
model = genai.GenerativeModel("gemini-1.5-flash")

VISION_PROMPT = """
You are analysing a sports broadcast frame.
Return ONLY valid JSON with these fields:
{
  "sport": "football",
  "home_team": "...",
  "away_team": "...",
  "home_score": 0,
  "away_score": 0,
  "match_minute": 0,
  "action": "brief description of what is happening"
}
If you cannot read a field, use null.
"""

def analyse_frame(frame_b64: str) -> dict:
    response = model.generate_content([
        VISION_PROMPT,
        {"mime_type": "image/jpeg", "data": frame_b64}
    ])
    raw = response.text
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        return json.loads(match.group())
    return {}

if __name__ == "__main__":
    from capture import capture_frame
    frame = capture_frame()
    state = analyse_frame(frame)
    print(json.dumps(state, indent=2))
