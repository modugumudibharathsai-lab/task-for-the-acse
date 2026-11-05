from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union, Any
import os
import json

DEFAULT_INSECURE_SECRET = "vigbot-super-secret-production-key-change-in-prod-12345"

class Settings(BaseSettings):
    APP_NAME: str = "VIGBOT API"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", DEFAULT_INSECURE_SECRET)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database: Default to persistent SQLite database at database/vigbot.db
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///database/vigbot.db" if os.path.exists(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "database", "vigbot.db"))) else "sqlite:///database/vigbot.db")
    USE_IN_MEMORY_DB: bool = os.getenv("USE_IN_MEMORY_DB", "false").lower() in ("true", "1", "yes")
    
    # LLM Provider Configuration (Primary: Gemini, disabled when ENABLE_GEMINI is false)
    ENABLE_GEMINI: bool = os.getenv("ENABLE_GEMINI", "false").lower() in ("true", "1", "yes")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    
    # LLM Fallback Provider (Groq, disabled when ENABLE_GROQ is false)
    ENABLE_GROQ: bool = os.getenv("ENABLE_GROQ", "false").lower() in ("true", "1", "yes")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
    
    # ML Intent Classifier Configuration (Default: True in Production)
    USE_INTENT_CLASSIFIER: bool = os.getenv("USE_INTENT_CLASSIFIER", "true").lower() in ("true", "1", "yes")
    ALLOW_PIPELINE_TEST_MODEL: bool = os.getenv("ALLOW_PIPELINE_TEST_MODEL", "false").lower() in ("true", "1", "yes")
    INTENT_MODEL_PATH: str = os.getenv("INTENT_MODEL_PATH", "artifacts/intent_model.joblib")
    INTENT_CONFIG_PATH: str = os.getenv("INTENT_CONFIG_PATH", "artifacts/intent_config.json")
    
    # CORS
    FRONTEND_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000"
    ]
    
    @field_validator("FRONTEND_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            v_str = v.strip()
            if not v_str:
                return []
            if v_str.startswith("[") and v_str.endswith("]"):
                try:
                    parsed = json.loads(v_str)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if str(item).strip()]
                except Exception:
                    pass
            return [i.strip() for i in v_str.split(",") if i.strip()]
        if isinstance(v, (list, tuple, set)):
            return [str(i).strip() for i in v if str(i).strip()]
        return [str(v)]

    model_config = SettingsConfigDict(
        env_file=(
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env")),
            ".env"
        ),
        extra="allow"
    )

    def validate_production_security(self):
        if not self.SECRET_KEY or self.SECRET_KEY == DEFAULT_INSECURE_SECRET:
            if self.ENVIRONMENT.lower() == "production":
                raise RuntimeError(
                    "CRITICAL SECURITY FATAL: A strong, unique SECRET_KEY (minimum 32 chars) "
                    "must be configured in environment variables for production deployment."
                )
            else:
                import logging
                logging.getLogger("uvicorn.error").warning(
                    "[SECURITY WARNING] Using default development SECRET_KEY. "
                    "Ensure a cryptographically secure 256-bit SECRET_KEY is set in production."
                )
        elif len(self.SECRET_KEY) < 32:
            if self.ENVIRONMENT.lower() == "production":
                raise RuntimeError(
                    "CRITICAL SECURITY FATAL: SECRET_KEY must be at least 32 characters long in production."
                )

settings = Settings()
settings.validate_production_security()
