import { useEffect, useRef } from "react";

function useWebSocket(prId, onMessage) {
  const wsRef = useRef(null);

  useEffect(() => {
    if (!prId) return;

    const ws = new WebSocket(`ws://localhost:8000/ws/${prId}`);
    wsRef.current = ws;

    ws.onopen = () => console.log("WebSocket connected:", prId);

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (e) {
        console.error("Failed to parse message:", e);
      }
    };

    ws.onerror = (e) => {
      console.error("WebSocket error:", e);
      onMessage({ error: "Connection error. Is the backend running?" });
    };

    ws.onclose = () => console.log("WebSocket closed");

    return () => {
      ws.close();
    };
  }, [prId]);

  return wsRef;
}

export default useWebSocket;  