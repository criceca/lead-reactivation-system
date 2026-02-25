"""
Configuración de la aplicación
"""

import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración de la aplicación"""

    # ============ LLM Configuration ============
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4")
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))

    # ============ Database Configuration ============
    database_url: str = os.getenv(
        "DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/lead_reactivation"
    )
    database_echo: bool = os.getenv("DATABASE_ECHO", "False").lower() == "true"

    # ============ Email Configuration ============
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from: str = os.getenv("SMTP_FROM", "noreply@leadreactivation.com")
    sales_team_email: str = os.getenv("SALES_TEAM_EMAIL", "")

    # ============ AWS S3 Configuration ============
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    aws_s3_bucket: str = os.getenv("AWS_S3_BUCKET", "")

    # ============ API Configuration ============
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_workers: int = int(os.getenv("API_WORKERS", "4"))
    api_reload: bool = os.getenv("API_RELOAD", "True").lower() == "true"

    # ============ Streamlit Configuration ============
    streamlit_port: int = int(os.getenv("STREAMLIT_PORT", "8501"))

    # ============ Agent Configuration ============
    agent_timeout: int = int(os.getenv("AGENT_TIMEOUT", "300"))
    max_conversation_turns: int = int(os.getenv("MAX_CONVERSATION_TURNS", "20"))
    agent_debug: bool = os.getenv("AGENT_DEBUG", "False").lower() == "true"

    # ============ Environment ============
    environment: str = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Obtener configuración (cached)"""
    return Settings()
