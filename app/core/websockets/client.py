import asyncio
import websockets
import msgpack
from app.core.websockets.instructions import Instruction, InstructionType

class WebSocketClient:
    def __init__(self, url: str):
        self.url = url
        self.websocket = None

    async def connect(self):
        self.websocket = await websockets.connect(self.url)
        print(f"Connected to WebSocket server at {self.url}")

    async def disconnect(self):
        if self.websocket:
            await self.websocket.close()
            print("Disconnected from WebSocket server")

    async def receive_instruction(self) -> Instruction:
        if not self.websocket:
            raise Exception("WebSocket is not connected")
        
        while True:
            message = await self.websocket.recv()
            data = msgpack.unpackb(message)
            if data.get("type") == "pong":
                print("Received pong from server")
                continue
            return Instruction(InstructionType(data["type"]), data["payload"])

    async def send_response(self, response: dict):
        if not self.websocket:
            raise Exception("WebSocket is not connected")
        
        await self.websocket.send(msgpack.packb(response))

    async def ping(self):
        if not self.websocket:
            raise Exception("WebSocket is not connected")
        
        await self.websocket.send(msgpack.packb({"type": "ping"}))
        print("Ping sent to server")

    async def start_ping_loop(self):
        while True:
            await self.ping()
            await asyncio.sleep(60)  # Ping every 60 seconds