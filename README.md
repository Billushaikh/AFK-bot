# AFK Bot (Flask + Web UI)

A local Flask app that keeps your system active by moving the mouse at random intervals using `pyautogui`.

You control it from a browser UI (`index.html`) that talks to a small JSON API (`/api/*`).

## Features

- Start/stop AFK loop from browser
- Configure interval and X/Y movement range
- Live status polling (running state, move count, runtime, last position)
- Error feedback in UI
- Safe fallback path handling for templates/static files

## Project Files

Current layout in this workspace:

```
.
├── app.py
├── index.html
├── script.js
├── style.css
└── README.md
```

`app.py` is configured to support both:

- standard Flask layout (`templates/`, `static/`), and
- your current flat layout (files in project root)

## Requirements

- Python 3.9+
- Packages:
  - `flask`
  - `pyautogui`

Install:

```powershell
pip install flask pyautogui
```

## Run

From the project folder:

```powershell
python .\app.py
```

Open:

- `http://127.0.0.1:5000`

## API Endpoints

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/` | Serve the control panel |
| `GET` | `/api/status` | Get bot status and telemetry |
| `POST` | `/api/start` | Start loop with settings |
| `POST` | `/api/stop` | Stop loop |

### `POST /api/start` JSON body

```json
{
  "interval": 2.0,
  "x_min": 600,
  "x_max": 700,
  "y_min": 200,
  "y_max": 600
}
```

Validation rules:

- `interval > 0`
- `x_min < x_max`
- `y_min < y_max`

## Troubleshooting

### `TemplateNotFound: index.html`

This usually happens when Flask expects a `templates/` folder. Your `app.py` now auto-detects paths and works with root-level `index.html` too.

### `pyautogui is not installed on the server`

Install dependency and restart:

```powershell
pip install pyautogui
python .\app.py
```

### Mouse movement does not happen

- Ensure app is running on your local machine (same machine as cursor)
- Check UI for `last_error`
- Move mouse to top-left corner only if you want to trigger PyAutoGUI failsafe behavior

## Notes

- This tool is intended for local personal use.
- Keep values reasonable to avoid sudden cursor jumps.
