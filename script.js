const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const traceTrack = document.getElementById('traceTrack');
const movesValue = document.getElementById('movesValue');
const runtimeValue = document.getElementById('runtimeValue');
const positionValue = document.getElementById('positionValue');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const errorMsg = document.getElementById('errorMsg');

const intervalInput = document.getElementById('interval');
const xMinInput = document.getElementById('xMin');
const xMaxInput = document.getElementById('xMax');
const yMinInput = document.getElementById('yMin');
const yMaxInput = document.getElementById('yMax');

function formatRuntime(totalSeconds) {
  const h = String(Math.floor(totalSeconds / 3600)).padStart(2, '0');
  const m = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, '0');
  const s = String(totalSeconds % 60).padStart(2, '0');
  return `${h}:${m}:${s}`;
}

function showError(message) {
  if (!message) {
    errorMsg.classList.remove('is-visible');
    errorMsg.textContent = '';
    return;
  }
  errorMsg.textContent = message;
  errorMsg.classList.add('is-visible');
}

function applyState(data) {
  const running = data.running;

  statusDot.classList.toggle('is-running', running);
  traceTrack.classList.toggle('is-running', running);
  statusText.textContent = running ? 'active — jiggling mouse' : 'idle — not running';

  startBtn.disabled = running || !data.pyautogui_available;
  stopBtn.disabled = !running;

  movesValue.textContent = data.moves;
  runtimeValue.textContent = formatRuntime(data.elapsed || 0);
  positionValue.textContent = (data.last_x != null && data.last_y != null)
    ? `${data.last_x}, ${data.last_y}`
    : '—';

  [intervalInput, xMinInput, xMaxInput, yMinInput, yMaxInput].forEach(input => {
    input.disabled = running;
  });

  if (data.last_error) {
    showError(data.last_error);
  }
}

async function poll() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    applyState(data);
  } catch (e) {
    // Server unreachable; leave last known state on screen.
  }
}

async function start() {
  showError(null);
  const payload = {
    interval: parseFloat(intervalInput.value),
    x_min: parseInt(xMinInput.value, 10),
    x_max: parseInt(xMaxInput.value, 10),
    y_min: parseInt(yMinInput.value, 10),
    y_max: parseInt(yMaxInput.value, 10),
  };

  const res = await fetch('/api/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!data.ok) {
    showError(data.error || 'Failed to start.');
  }
  poll();
}

async function stop() {
  showError(null);
  await fetch('/api/stop', { method: 'POST' });
  poll();
}

startBtn.addEventListener('click', start);
stopBtn.addEventListener('click', stop);

poll();
setInterval(poll, 1000);
