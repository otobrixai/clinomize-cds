from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/transfusion_cds",
        env="DATABASE_URL"
    )
    
    # JWT
    # SECRET_KEY defaults to dev value - set via environment variable in production
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        env="CORS_ORIGINS",
        json_schema_extra={
            "example": ["http://localhost:3000", "https://yourdomain.com"]
        }
    )
    
    # AI (sandboxed) - ADMIN ONLY, NEVER in clinical UI
    OPENAI_API_KEY: str = ""
    AI_ENABLED: bool = False  # Must be explicitly enabled system-wide
    AI_CLINICAL_ACCESS: bool = False  # Hard-coded: AI never accessible to clinical users
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Warn if using default SECRET_KEY (but allow in development)
        if self.SECRET_KEY == "dev-secret-key-change-in-production":
            import warnings
            warnings.warn(
                "Using default SECRET_KEY. This is insecure for production. "
                "Set SECRET_KEY environment variable in production.",
                UserWarning
            )
    
    class Config:
        env_file = ".env"

settings = Settings()


print(f"CORS_ORIGINS: {settings.CORS_ORIGINS}")
print(f"CORS_ORIGINS type: {type(settings.CORS_ORIGINS)}")