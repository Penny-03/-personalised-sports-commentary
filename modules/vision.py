import google.generativeai as genai
import json, re

import base64 #to test

genai.configure(api_key="AIzaSyBlfKT1KQXbY-JpVZQJ59y6lARCb_eqMwM")
model = genai.GenerativeModel("gemini-3.5-flash")

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

# uncomment this to test it with an image 
'''def capture_frame():
    with open("test.png", "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")'''

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
    from capture import capture_frame # comment this line to test
    frame = capture_frame()
    state = analyse_frame(frame)
    print(json.dumps(state, indent=2))
