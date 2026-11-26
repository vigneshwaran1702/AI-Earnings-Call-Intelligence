export function connectPipelineSocket({ onEvent, onStatusChange }) {
  let ws = null;
  let closedByUser = false;
  let reconnectTimer = null;

  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/pipeline`;

  function connect() {
    onStatusChange?.("connecting");
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      onStatusChange?.("live");
    };

    ws.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        onEvent?.(parsed);
      } catch {
        onEvent?.({ type: "message", raw: event.data });
      }
    };

    ws.onclose = () => {
      if (closedByUser) {
        onStatusChange?.("disconnected");
        return;
      }
      onStatusChange?.("reconnecting");
      reconnectTimer = setTimeout(connect, 3000);
    };

    ws.onerror = () => {
      ws?.close();
    };
  }

  connect();

  return () => {
    closedByUser = true;
    if (reconnectTimer) clearTimeout(reconnectTimer);
    ws?.close();
  };
}

