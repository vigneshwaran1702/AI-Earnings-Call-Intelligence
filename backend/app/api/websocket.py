"""WebSocket hub for live pipeline events.

Connected clients receive JSON messages whenever a new filing is
detected, a PDF is downloaded, or an AI summary is generated.
"""

import json
import asyncio
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    """Tracks active WebSocket connections and broadcasts events."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, event: dict):
        """Send a JSON event to every connected client."""
        message = json.dumps(event)
        stale: List[WebSocket] = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                stale.append(connection)
        for conn in stale:
            self.active_connections.remove(conn)


manager = ConnectionManager()


@router.websocket("/ws/pipeline")
async def pipeline_feed(websocket: WebSocket):
    """Live feed endpoint – the React dashboard connects here."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive; ignore client messages for now
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def emit_event(event_type: str, data: dict):
    """Helper used by the pipeline to broadcast updates."""
    await manager.broadcast({"type": event_type, **data})

