import asyncio
from app.core.config import settings
from app.core.websockets.client import WebSocketClient

async def main():
    print("Starting Lasko Agent...")
    websocket_client = WebSocketClient(settings.BACKEND_WEBSOCKET_URL)

    ping_task = None 

    try:
        await websocket_client.connect()

        if settings.ENABLE_PING:
            ping_task = asyncio.create_task(websocket_client.start_ping_loop())

        # Start the main loop to handle requests and responses
        await websocket_client.run()
        
    except Exception as e:
        print(f"Error in main loop: {e}")
    finally:
        if settings.ENABLE_PING and ping_task:
            ping_task.cancel()
        await websocket_client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())