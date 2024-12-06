"""Configuration settings for Deep Lynx queries."""
from functools import lru_cache
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Settings for Deep Lynx connection."""
    DEEP_LYNX_URL: str = "http://localhost:8090"
    DEEP_LYNX_CONTAINER_ID: str
    DEEP_LYNX_API_KEY: str
    DEEP_LYNX_API_SECRET: str

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    """Get settings instance."""
    return Settings() 