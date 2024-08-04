from pydantic_settings import BaseSettings
import argparse

class Settings(BaseSettings):
    APP_NAME: str = "Lasko Agent"
    DEBUG: bool = False
    BACKEND_WEBSOCKET_URL: str = "ws://localhost:8765"

    class Config:
        env_file = ".env"

def parse_args():
    parser = argparse.ArgumentParser(description="Lasko Agent")
    return parser.parse_args()

args = parse_args()
settings = Settings()
