import asyncio
import json
from fastapi import WebSocket
from redis.asyncio import Redis
from src.core.config import settings

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.redis: Redis | None = None
        self.pubsub = None
        self.listen_task: asyncio.Task | None = None

    async def connect_redis(self):
        if not self.redis:
            self.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
            self.pubsub = self.redis.pubsub()
            await self.pubsub.subscribe("forgeai_events")
            self.listen_task = asyncio.create_task(self._listen_to_redis())

    async def _listen_to_redis(self):
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    data = message["data"]
                    # Broadcast to all local connections
                    for connection in self.active_connections:
                        try:
                            await connection.send_text(data)
                        except Exception:
                            # If connection is dead, we'll remove it in disconnect()
                            pass
        except Exception as e:
            print(f"Redis Pub/Sub listener error: {e}")

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # Ensure Redis is connected when the first client joins
        await self.connect_redis()

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_event(self, event: str, payload: dict):
        """
        Publish an event to Redis. All workers listening to 'forgeai_events'
        will receive it and broadcast it to their local WebSocket clients.
        """
        if not self.redis:
            await self.connect_redis()
            
        message = json.dumps({
            "event": event,
            "data": payload
        }, default=str) # default=str handles UUIDs and datetimes
        
        await self.redis.publish("forgeai_events", message)

manager = ConnectionManager()
