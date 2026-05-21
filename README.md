# Real-Time personalized Football Commentary System

A real-time AI system that watches a live football broadcast, understands what is happening using both vision and live match data, and generates a personalised audio commentary track on top of the game.

The system combines **screen capture**, **computer vision**, **live sports APIs**, **LLMs**, and **text-to-speech** to create an adaptive commentary experience tailored to different user personas.


## System Overview

The pipeline consists of four main components:

### 1. Screen Capture
The system continuously captures frames from a live broadcast using screen capture tools.

### 2. Vision Understanding
Each frame is analysed using a vision model (Gemini 2.5 Flash) to extract:
- On-pitch action (e.g. counterattack, corner, foul)
- Visual context (e.g. crowded box, goalkeeper under pressure)
- General game situation

### 3. Live Stats Integration
Structured match data is retrieved from the API-Footbal (v3.football.api-sports.io):
- Scoreline
- Match minute
- Teams
- Goal events
- Match status

This provides **ground truth** to complement visual interpretation.


## Game State Fusion

Outputs from vision and API are merged into a single structured object:


```json
{
  "teams": {
    "home": "Inter",
    "away": "Milan"
  },
  "score": "2-1",
  "minute": 67,
  "visual_context": "Corner kick with crowded penalty area",
  "recent_event": "Shot on target saved by goalkeeper"
}
```
## Requirments
Requires Python 3.12 or lower and install the dependencies

```
pip install requirements.txt
```




