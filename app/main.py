import asyncio
from app.core.config import settings
from app.core.websockets.client import WebSocketClient
from app.services.print_service import PrintService

async def main():
    print("Starting Lasko Agent...")
    websocket_client = WebSocketClient(settings.BACKEND_WEBSOCKET_URL)
    print_service = PrintService()

    try:
        await websocket_client.connect()
        ping_task = asyncio.create_task(websocket_client.start_ping_loop())
        
        while True:
            try:
                instruction = await websocket_client.receive_instruction()
                response = await print_service.process_instruction(instruction)
                await websocket_client.send_response(response)
            except Exception as e:
                print(f"Error processing instruction: {e}")
                # Optionally, you might want to add a small delay here to avoid tight loop in case of persistent errors
                # await asyncio.sleep(1)
    except Exception as e:
        print(f"Error in main loop: {e}")
    finally:
        if 'ping_task' in locals():
            ping_task.cancel()
        await websocket_client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())