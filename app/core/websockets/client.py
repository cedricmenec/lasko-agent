import asyncio
import websockets
import msgpack
import uuid
from datetime import datetime, timezone
from app.core.config import settings
from app.core.request_handler import RequestHandler

class WebSocketClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.websocket = None
        self.agent_id = str(uuid.uuid4())  # Generate a unique ID for this agent
        self.url = f"{self.base_url}/{self.agent_id}"  # Include agent_id in the URL
        self.reconnect_interval = 5  # seconds
        self.request_handler = RequestHandler()

    async def connect(self):
        while True:
            try:
                self.websocket = await websockets.connect(self.url)
                print(f"Connected to WebSocket server at {self.url}")
                return
            except Exception as e:
                print(f"Failed to connect to WebSocket server: {e}")
                print(f"Retrying in {self.reconnect_interval} seconds...")
                await asyncio.sleep(self.reconnect_interval)

    async def disconnect(self):
        if self.websocket:
            await self.websocket.close()
            print("Disconnected from WebSocket server")

    async def receive_request(self) -> dict:
        if not self.websocket:
            raise Exception("WebSocket is not connected")
        
        while True:
            try:
                if not self.websocket:
                    await self.connect()
                
                message = await self.websocket.recv()
                data = msgpack.unpackb(message)
                
                if data["type"] == "request":
                    return data
                
                raise ValueError(f"Unexpected message type: {data.get('type')}")

            except websockets.exceptions.ConnectionClosed:
                print("WebSocket connection closed. Attempting to reconnect...")
                await self.connect()
            except Exception as e:
                print(f"Error receiving request: {e}")
                await asyncio.sleep(1)

    async def process_request(self, request: dict) -> dict:
        command = request["command"]
        payload = request["payload"]

        handler_response = await self.request_handler.handle_request(command, payload)

        return {
            "type": "response",
            "version": "1.0",
            "id": request["id"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "command": command,
            "processing_time": handler_response["processing_time"],
            "status": handler_response["status"],
            "payload": handler_response["payload"]
        }

    async def send_response(self, response: dict):
        while True:
            try:
                if not self.websocket:
                    await self.connect()
                
                await self.websocket.send(msgpack.packb(response))
                return
            except websockets.exceptions.ConnectionClosed:
                print("WebSocket connection closed. Attempting to reconnect...")
                await self.connect()
            except Exception as e:
                print(f"Error sending response: {e}")
                await asyncio.sleep(1)

    async def run(self):
        while True:
            try:
                request = await self.receive_request()
                response = await self.process_request(request)
                await self.send_response(response)
            except Exception as e:
                print(f"Error in main loop: {e}")
                await asyncio.sleep(1)  # Prevent tight loop in case of persistent errors
