import asyncio
from app.core.config import settings
from app.core.websockets.client import WebSocketClient

async def main():
    print("Starting Lasko Agent...")
    websocket_client = WebSocketClient(settings.BACKEND_WEBSOCKET_URL)

    try:
        await websocket_client.connect()

        # Start the main loop to handle requests and responses
        await websocket_client.run()
        
    except Exception as e:
        print(f"Error in main loop: {e}")
    finally:
        await websocket_client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())