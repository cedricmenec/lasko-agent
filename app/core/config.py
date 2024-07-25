from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Lasko Agent"
    DEBUG: bool = False
    BACKEND_WEBSOCKET_URL: str = "ws://localhost:8765"
    
    class Config:
        env_file = ".env"

settings = Settings()