import { useEffect, useRef } from "react";

function useWebSocket(prId, onMessage) {
  const wsRef = useRef(null);

  useEffect(() => {
    if (!prId) return;

    const ws = new WebSocket(`ws://localhost:8000/ws/${prId}`);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    ws.onerror = (e) => console.error("WebSocket error:", e);

    return () => {
      ws.close();
    };
  }, [prId]);

  return wsRef;
}

export default useWebSocket;