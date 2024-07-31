import asyncio
import websockets
import msgpack
import uuid
from pydantic import BaseModel
from app.core.websockets.commands import Command, CommandType
from app.core.config import settings
from app.models.printer import PrinterListModel
from app.services.printer_service import PrinterService

class WebSocketClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.websocket = None
        self.agent_id = str(uuid.uuid4())  # Generate a unique ID for this agent
        self.url = f"{self.base_url}/{self.agent_id}"  # Include agent_id in the URL
        self.reconnect_interval = 5  # seconds
        self.printer_service = PrinterService()

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

                if data.get("type") == "pong":
                    print("Received pong from server")
                    continue
                
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
        """
        Processes a request received from the WebSocket server and returns a response.
        
        The `process_request` method handles different types of requests received from the WebSocket server. It uses the `printer_service` to get the printer list or the status of a specific printer, and returns the appropriate response.
        
        If the request command is `GET_PRINTER_LIST`, the method returns a dictionary with the list of printers.
        If the request command is `GET_PRINTER_STATUS`, the method returns the status of the printer specified in the request payload.
        If the request command is unknown, the method returns a dictionary with an error message.
        
        Args:
            request (dict): The request received from the WebSocket server.
        
        Returns:
            dict: The response to the request.
        """
        command = request["command"]
        payload = request["payload"]

        if command == CommandType.GET_PRINTER_LIST.value:
            printer_list: PrinterListModel = await self.printer_service.get_printer_list()
            return {
                "type": "response",
                "id": request["id"],
                "command": command,
                "payload": {"printers": printer_list.model_dump()["printers"]}
            }
        elif command == CommandType.GET_PRINTER_STATUS.value:
            printer_id = payload.get("printer_id")
            printer_status =  self.printer_service.get_printer_status(printer_id)
            return {
                "type": "response",
                "id": request["id"],
                "command": command,
                "payload": printer_status
            }
            
        else:
             return {
                "type": "response",
                "id": request["id"],
                "command": command,
                "payload": {"error": f"Unknown command ({command})"}
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

    async def ping(self):
        try:
            if not self.websocket:
                await self.connect()
            
            await self.websocket.send(msgpack.packb({"type": "ping"}))
            print("Ping sent to server")
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed during ping. Attempting to reconnect...")
            await self.connect()
        except Exception as e:
            print(f"Error sending ping: {e}")

    async def start_ping_loop(self):
        if settings.ENABLE_PING:
            while True:
                await self.ping()
                await asyncio.sleep(settings.PING_INTERVAL)
        else:
            print("Ping functionality is disabled")

    async def run(self):
        while True:
            try:
                request = await self.receive_request()
                response = await self.process_request(request)
                await self.send_response(response)
            except Exception as e:
                print(f"Error in main loop: {e}")
                await asyncio.sleep(1)  # Prevent tight loop in case of persistent errors
