import asyncio, json, time
from config import *
from state import GameState, merge
from modules.capture import capture_frame
from modules.vision import analyse_frame
from modules.stats import get_live_fixture_id, get_match_stats
from modules.commentary import generate_commentary
from modules.tts import speak
import time

state = GameState()
fixture_id = None



async def commentary_loop():
    await asyncio.sleep(35)
    while True:
        t0 = time.perf_counter()
        try:
            import dataclasses
            state_dict = dataclasses.asdict(state)

            t1 = time.perf_counter()
            text = await asyncio.to_thread(
                generate_commentary, state_dict, PERSONA)
            t2 = time.perf_counter()

            if text != state.last_commentary:
                state.last_commentary = text
                await asyncio.to_thread(speak, text, PERSONA)
            t3 = time.perf_counter()

            print(f"[timing] groq={t2-t1:.2f}s  tts={t3-t2:.2f}s  "
                  f"total={t3-t0:.2f}s")
        except Exception as e:
            print(f"[commentary] error: {e}")
        await asyncio.sleep(40)

# ── Loop 1: capture frame + run vision every 30s ─────────────────
async def vision_loop():
    while True:
        try:
            frame = await asyncio.to_thread(capture_frame)
            vision_data = await asyncio.to_thread(analyse_frame, frame)
            merge(state, vision_data, {})
            print(f"[vision] action: {state.action}")
        except Exception as e:
            print(f"[vision] error: {e}")
        await asyncio.sleep(CAPTURE_INTERVAL)

# ── Loop 2: poll stats API every 2 minutes ───────────────────────
async def stats_loop():
    global fixture_id
    while True:
        try:
            if not fixture_id:
                fixture_id = await asyncio.to_thread(
                    get_live_fixture_id, TEAM_NAME)
                print(f"[stats] fixture found: {fixture_id}")
            if fixture_id:
                stats_data = await asyncio.to_thread(
                    get_match_stats, fixture_id)
                merge(state, {}, stats_data)
                print(f"[stats] score: {state.home_score}-{state.away_score} "
                      f"min {state.match_minute}")
        except Exception as e:
            print(f"[stats] error: {e}")
        await asyncio.sleep(STATS_INTERVAL)

# ── Loop 3: generate + speak commentary every 40s ────────────────
async def commentary_loop():
    await asyncio.sleep(35)  # wait for first vision + stats to load
    while True:
        try:
            if state.action or state.home_score is not None:
                import dataclasses
                state_dict = dataclasses.asdict(state)
                text = await asyncio.to_thread(
                    generate_commentary, state_dict, PERSONA)
                # avoid repeating the exact same line
                if text != state.last_commentary:
                    print(f"[commentary] {text}")
                    state.last_commentary = text
                    await asyncio.to_thread(speak, text, PERSONA)
        except Exception as e:
            print(f"[commentary] error: {e}")
        await asyncio.sleep(40)

# ── Entry point ───────────────────────────────────────────────────
async def main():
    print("Pipeline starting... waiting for first data.")
    await asyncio.gather(
        vision_loop(),
        stats_loop(),
        commentary_loop(),
    )

if __name__ == "__main__":
    asyncio.run(main())