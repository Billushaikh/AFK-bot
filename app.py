import random
import threading
import time
from pathlib import Path

from flask import Flask, jsonify, render_template, request

try:
    import pyautogui as pag
    pag.FAILSAFE = True
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

BASE_DIR = Path(__file__).resolve().parent
template_dir = BASE_DIR / "templates"
static_dir = BASE_DIR / "static"

app = Flask(
    __name__,
    template_folder=str(template_dir if template_dir.exists() else BASE_DIR),
    static_folder=str(static_dir if static_dir.exists() else BASE_DIR),
)

state_lock = threading.Lock()
state = {
    "running": False,
    "moves": 0,
    "start_time": None,
    "last_x": None,
    "last_y": None,
    "last_error": None,
}
worker_thread = None
stop_event = threading.Event()


def run_loop(interval, x_min, x_max, y_min, y_max):
    while not stop_event.is_set():
        x = random.randint(x_min, x_max)
        y = random.randint(y_min, y_max)
        try:
            pag.moveTo(x, y, 0.5)
        except Exception as e:
            with state_lock:
                state["running"] = False
                state["last_error"] = str(e)
            return
        with state_lock:
            state["moves"] += 1
            state["last_x"] = x
            state["last_y"] = y
        stop_event.wait(interval)


@app.route("/")
def index():
    return render_template("index.html", pyautogui_available=PYAUTOGUI_AVAILABLE)


@app.route("/api/status")
def status():
    with state_lock:
        elapsed = 0
        if state["running"] and state["start_time"]:
            elapsed = int(time.time() - state["start_time"])
        return jsonify(
            running=state["running"],
            moves=state["moves"],
            elapsed=elapsed,
            last_x=state["last_x"],
            last_y=state["last_y"],
            last_error=state["last_error"],
            pyautogui_available=PYAUTOGUI_AVAILABLE,
        )


@app.route("/api/start", methods=["POST"])
def start():
    global worker_thread

    if not PYAUTOGUI_AVAILABLE:
        return jsonify(ok=False, error="pyautogui is not installed on the server."), 400

    with state_lock:
        if state["running"]:
            return jsonify(ok=False, error="Already running."), 400

    payload = request.get_json(silent=True) or {}
    try:
        interval = float(payload.get("interval", 2.0))
        x_min = int(payload.get("x_min", 600))
        x_max = int(payload.get("x_max", 700))
        y_min = int(payload.get("y_min", 200))
        y_max = int(payload.get("y_max", 600))
        if interval <= 0:
            raise ValueError("Interval must be greater than 0.")
        if x_min >= x_max or y_min >= y_max:
            raise ValueError("Min values must be less than max values.")
    except (TypeError, ValueError) as e:
        return jsonify(ok=False, error=str(e) or "Invalid settings."), 400

    stop_event.clear()
    with state_lock:
        state["running"] = True
        state["moves"] = 0
        state["start_time"] = time.time()
        state["last_error"] = None

    worker_thread = threading.Thread(
        target=run_loop, args=(interval, x_min, x_max, y_min, y_max), daemon=True
    )
    worker_thread.start()
    return jsonify(ok=True)


@app.route("/api/stop", methods=["POST"])
def stop():
    stop_event.set()
    with state_lock:
        state["running"] = False
    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(debug=False, port=5000)
