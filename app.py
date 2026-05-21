import asyncio, threading, time, dataclasses, json, queue
from flask import Flask, Response, render_template_string, request, jsonify

from config import PERSONA, TEAM_NAME, CAPTURE_INTERVAL, STATS_INTERVAL
from state import GameState, merge
from modules.capture import capture_frame
from modules.vision import analyse_frame
from modules.stats import get_live_fixture_id, get_match_stats
from modules.commentary import generate_commentary
from modules.tts import speak

app = Flask(__name__)

state = GameState()
fixture_id = None
pipeline_running = False
pipeline_thread = None
event_queue = queue.Queue(maxsize=100)
settings = {
      'persona': PERSONA,
      'team_name': TEAM_NAME,
      'capture_interval': CAPTURE_INTERVAL,
      'stats_interval': STATS_INTERVAL,
      'commentary_interval': 20,
      'tts_enabled': True,
}

def push_event(kind, data):
      try:
                event_queue.put_nowait({'kind': kind, 'data': data, 'ts': time.time()})
except queue.Full:
        pass

async def vision_loop():
      while pipeline_running:
                try:
                              frame = await asyncio.to_thread(capture_frame)
                              vision_data = await asyncio.to_thread(analyse_frame, frame)
                              merge(state, vision_data, {})
                              push_event('vision', {
                                  'action': state.action,
                                  'home_team': state.home_team,
                                  'away_team': state.away_team,
                                  'home_score': state.home_score,
                                  'away_score': state.away_score,
                                  'match_minute': state.match_minute,
                              })
except Exception as e:
            push_event('error', {'source': 'vision', 'msg': str(e)})
        await asyncio.sleep(settings['capture_interval'])

async def stats_loop():
      global fixture_id
      while pipeline_running:
                try:
                              if not fixture_id:
                                                fixture_id = await asyncio.to_thread(get_live_fixture_id, settings['team_name'])
                                                push_event('stats', {'fixture_id': fixture_id})
                                            if fixture_id:
                                                              stats_data = await asyncio.to_thread(get_match_stats, fixture_id)
                                                              merge(state, {}, stats_data)
                                                              push_event('stats', {
                                                                  'home_score': state.home_score,
                                                                  'away_score': state.away_score,
                                                                  'match_minute': state.match_minute,
                                                                  'last_event_type': state.last_event_type,
                                                                  'last_event_player': state.last_event_player,
                                                                  'last_event_team': state.last_event_team,
                                                              })
                except Exception as e:
                              push_event('error', {'source': 'stats', 'msg': str(e)})
                          await asyncio.sleep(settings['stats_interval'])

  async def commentary_loop():
        await asyncio.sleep(15)
        while pipeline_running:
                  t0 = time.perf_counter()
                  try:
                                if state.action or state.home_score is not None:
                                                  state_dict = dataclasses.asdict(state)
                                                  text = await asyncio.to_thread(generate_commentary, state_dict, settings['persona'])
                                                  if text != state.last_commentary:
                                                                        state.last_commentary = text
                                                                        t1 = time.perf_counter()
                                                                        push_event('commentary', {'text': text, 'persona': settings['persona'], 'groq_ms': round((t1-t0)*1000)})
                                                                        if settings['tts_enabled']:
                                                                                                  await asyncio.to_thread(speak, text, settings['persona'])
                                                                                              t2 = time.perf_counter()
                                                                        push_event('timing', {'groq_s': round(t1-t0,2), 'tts_s': round(t2-t1,2) if settings['tts_enabled'] else 0})
                  except Exception as e:
                                push_event('error', {'source': 'commentary', 'msg': str(e)})
                            await asyncio.sleep(settings['commentary_interval'])

    def run_pipeline():
          loop = asyncio.new_event_loop()
          asyncio.set_event_loop(loop)
          loop.run_until_complete(asyncio.gather(vision_loop(), stats_loop(), commentary_loop()))

@app.route('/')
def index():
      return render_template_string(HTML)

@app.route('/start', methods=['POST'])
def start():
      global pipeline_running, pipeline_thread, fixture_id, state
      if pipeline_running:
                return jsonify({'ok': False, 'msg': 'already running'})
            state = GameState()
    fixture_id = None
    pipeline_running = True
    pipeline_thread = threading.Thread(target=run_pipeline, daemon=True)
    pipeline_thread.start()
    push_event('system', {'msg': 'Pipeline started'})
    return jsonify({'ok': True})

@app.route('/stop', methods=['POST'])
def stop():
      global pipeline_running
    pipeline_running = False
    push_event('system', {'msg': 'Pipeline stopped'})
    return jsonify({'ok': True})

@app.route('/settings', methods=['POST'])
def update_settings():
      data = request.json
    settings.update(data)
    push_event('system', {'msg': 'Settings updated'})
    return jsonify({'ok': True, 'settings': settings})

@app.route('/state')
def get_state():
      return jsonify(dataclasses.asdict(state))

@app.route('/stream')
def stream():
      def generate():
                while True:
                              try:
                                                event = event_queue.get(timeout=30)
                                                yield 'data: ' + json.dumps(event) + '\n\n'
except queue.Empty:
                yield 'data: {"kind":"ping"}\n\n'
    return Response(generate(), mimetype='text/event-stream', headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})

HTML = open('templates/index.html').read() if __import__('os').path.exists('templates/index.html') else '<h1>Missing templates/index.html</h1>'

if __name__ == '__main__':
      print('Starting Sports Commentary UI at http://localhost:5000')
    app.run(debug=False, threaded=True, port=5000, host='0.0.0.0')
