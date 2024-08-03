from pydantic_settings import BaseSettings
import argparse

class Settings(BaseSettings):
    APP_NAME: str = "Lasko Agent"
    DEBUG: bool = False
    BACKEND_WEBSOCKET_URL: str = "ws://localhost:8765"

    """
    Enables or disables the sending of periodic ping messages to the backend websocket server.
    When enabled, the agent will send a ping message to the server every `PING_INTERVAL` seconds to keep the connection alive.
    """
    ENABLE_PING: bool = False
    PING_INTERVAL: int = 60  

    class Config:
        env_file = ".env"

def parse_args():
    parser = argparse.ArgumentParser(description="Lasko Agent")
    parser.add_argument("--enable-ping", action="store_true", help="Enable ping functionality")
    return parser.parse_args()

args = parse_args()
settings = Settings()

if args.enable_ping:
    settings.ENABLE_PING = True
else:
    settings.ENABLE_PING = False