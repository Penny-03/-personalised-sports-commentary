from kokoro import KPipeline
import sounddevice as sd
import soundfile as sf
import time, io, numpy as np

pipeline = KPipeline(lang_code="en-us")

VOICES = {
    "beginner": "af_heart",   # warm, friendly
    "fan":      "am_fenrir",  # energetic male
    "analyst":  "af_nova",    # calm, professional
}

def speak(text: str, persona: str = "fan"):
    voice = VOICES.get(persona, "af_heart")
    start = time.time()
    generator = pipeline(text, voice=voice, speed=1.1)
    audio_chunks = []
    for _, _, audio in generator:
        audio_chunks.append(audio)
    audio = np.concatenate(audio_chunks)
    latency = time.time() - start
    print(f"TTS latency: {latency:.2f}s for {len(text)} chars")
    sd.play(audio, samplerate=24000)
    
if __name__ == "__main__":
    speak("Lautaro Martinez scores and Inter lead the derby!", "fan")
    speak("Inter hold a one goal advantage with twenty minutes remaining.", "analyst")
    speak("Inter have scored — that means they are winning right now!", "beginner")
