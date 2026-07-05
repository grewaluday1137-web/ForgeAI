from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from src.websocket.manager import manager

router = APIRouter(prefix="/ws", tags=["websocket"])

@router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    # In a real app, validate token from query params or headers here
    # e.g., token = websocket.query_params.get("token")
    await manager.connect(websocket)
    try:
        while True:
            # We don't necessarily need to receive messages from clients right now,
            # but we need to keep the connection alive.
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
