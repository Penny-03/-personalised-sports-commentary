# personalised-sports-commentary
## required installations

- pip install kokoro soundfile sounddevice
- also requires: pip install torch --index-url https://download.pytorch.org/whl/cpu
- pip install groq
- pip install requests
- pip install google-generativeai
- pip install mss Pillow

## API KEYS
- Groq: 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
- Api Football: 80e09bb4d95617666c18d7690fade8b5 , v3.football.api-sports.io
- Gemini: AIzaSyCaAUuRK86k7LPm8m80EtT0K_2BLIxZ-nA

- curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent" \
  -H 'Content-Type: application/json' \
  -H 'X-goog-api-key: AIzaSyCaAUuRK86k7LPm8m80EtT0K_2BLIxZ-nA' \
  -X POST \
  -d '{
    "contents": [
      {
        "parts": [
          {
            "text": "Explain how AI works in a few words"
          }
        ]
      }
    ]
  }'
