from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/feedback_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_API_URL: Optional[str] = None  # Custom base URL for OpenAI API (e.g., for OpenRouter)
    OPENAI_MODEL: str = "gpt-4"
    
    # Application
    APP_NAME: str = "Feedback Loop API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # LLM Configuration
    LLM_MAX_TOKENS: int = 2000
    LLM_TEMPERATURE: float = 0.7
    LLM_TIMEOUT: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
