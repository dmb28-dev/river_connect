const WS_URL = import.meta.env.VITE_WS_URL || `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}`;

export function createWebSocket(path, onMessage) {
  const token = localStorage.getItem('access_token');
  const url = `${WS_URL}${path}?token=${token}`;
  const ws = new WebSocket(url);

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch {
      /* ignore */
    }
  };

  ws.onerror = () => ws.close();
  return ws;
}

export function vibrateEmergency() {
  if ('vibrate' in navigator) navigator.vibrate([200, 100, 200, 100, 500]);
}
