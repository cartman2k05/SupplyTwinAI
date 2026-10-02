import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore", env_file=".env", env_file_encoding="utf-8")
    
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "supplytwin")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "supplytwin_pass")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "supplytwin_db")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://supplytwin:supplytwin_pass@localhost:5432/supplytwin_db")
    
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "supplytwin_pass")
    
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL_ID: str = os.getenv("GEMINI_MODEL_ID", "gemini-2.5-flash")
    
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super_secret_jwt_key_change_in_production_32bytes")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

    OPEN_METEO_BASE_URL: str = os.getenv("OPEN_METEO_BASE_URL", "https://api.open-meteo.com/v1")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    RISK_THRESHOLD_ALERT: float = float(os.getenv("RISK_THRESHOLD_ALERT", "60.0"))
    SHIPMENT_DELAY_THRESHOLD_HOURS: int = int(os.getenv("SHIPMENT_DELAY_THRESHOLD_HOURS", "24"))

settings = Settings()
