import asyncio, time, dataclasses

from config import PERSONA, TEAM_NAME, CAPTURE_INTERVAL, STATS_INTERVAL
from state import GameState, merge
from modules.capture import capture_frame
from modules.vision import analyse_frame
from modules.stats import get_live_fixture_id, get_match_stats
from modules.commentary import generate_commentary
from modules.tts import speak

state = GameState()
fixture_id = None

async def vision_loop():
    while True:
        try:
            frame = await asyncio.to_thread(capture_frame)
            vision_data = await asyncio.to_thread(analyse_frame, frame)
            merge(state, vision_data, {})
            print('[vision] action:', state.action)
        except Exception as e:
            print('[vision] error:', e)
        await asyncio.sleep(CAPTURE_INTERVAL)

async def stats_loop():
    global fixture_id
    while True:
        try:
            if not fixture_id:
                fixture_id = await asyncio.to_thread(get_live_fixture_id, TEAM_NAME)
                print('[stats] fixture found:', fixture_id)
            if fixture_id:
                stats_data = await asyncio.to_thread(get_match_stats, fixture_id)
                merge(state, {}, stats_data)
                print('[stats] score:', state.home_score, '-', state.away_score, 'min', state.match_minute)
        except Exception as e:
            print('[stats] error:', e)
        await asyncio.sleep(STATS_INTERVAL)

async def commentary_loop():
    await asyncio.sleep(35)
    while True:
        t0 = time.perf_counter()
        try:
            if state.action or state.home_score is not None:
                state_dict = dataclasses.asdict(state)
                text = await asyncio.to_thread(generate_commentary, state_dict, PERSONA)
                if text != state.last_commentary:
                    print('[commentary]', text)
                    state.last_commentary = text
                    t1 = time.perf_counter()
                    await asyncio.to_thread(speak, text, PERSONA)
                    t2 = time.perf_counter()
                    print('[timing] groq=', round(t1-t0,2), 'tts=', round(t2-t1,2))
        except Exception as e:
            print('[commentary] error:', e)
        await asyncio.sleep(20)

async def main():
    print('Pipeline starting... waiting for first data.')
    await asyncio.gather(
        vision_loop(),
        stats_loop(),
        commentary_loop(),
    )

if __name__ == '__main__':
    asyncio.run(main())
