"""
Configuración de la aplicación
"""

import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
 """Configuración de la aplicación"""

 # ============ LLM Configuration ============
 # OpenAI
 use_openai: bool = os.getenv("USE_OPENAI", "False").lower() == "true"
 openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
 llm_model: str = os.getenv("LLM_MODEL", "gpt-4")
 llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
 
 # OpenRouter (Prioridad si USE_OPENROUTER=True)
 use_openrouter: bool = os.getenv("USE_OPENROUTER", "False").lower() == "true"
 openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
 openrouter_model: str = os.getenv("OPENROUTER_MODEL", "qwen/qwen-2.5-72b-instruct")
 openrouter_site_url: str = os.getenv("OPENROUTER_SITE_URL", "http://localhost:8000")
 openrouter_app_name: str = os.getenv("OPENROUTER_APP_NAME", "Lead Reactivation System")
 
 # DeepSeek (Prioridad si USE_DEEPSEEK=True)
 use_deepseek: bool = os.getenv("USE_DEEPSEEK", "False").lower() == "true"
 deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
 deepseek_model: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
 
 # AWS Bedrock (Prioridad si USE_BEDROCK=True)
 use_bedrock: bool = os.getenv("USE_BEDROCK", "False").lower() == "true"
 bedrock_model: str = os.getenv("BEDROCK_MODEL", "anthropic.claude-3-sonnet-20240229-v1:0")
 bedrock_region: str = os.getenv("BEDROCK_REGION", "us-east-1")

 # ============ Database Configuration ============
 database_url: str = os.getenv(
 "DATABASE_URL", "sqlite:///./lead_reactivation.db"
 )
 database_echo: bool = os.getenv("DATABASE_ECHO", "False").lower() == "true"

 # ============ Telegram Configuration ============
 telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
 telegram_webhook_url: str = os.getenv("TELEGRAM_WEBHOOK_URL", "")
 telegram_admin_chat_id: str = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "")
 
 # ============ Email Configuration (Opcional) ============
 smtp_host: str = os.getenv("SMTP_HOST", "")
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
 enable_email_notifications: bool = os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "False").lower() == "true"

 # ============ Environment ============
 environment: str = os.getenv("ENVIRONMENT", "development")
 log_level: str = os.getenv("LOG_LEVEL", "INFO")
 
 # ============ Conversation Channel ============
 conversation_channel: str = os.getenv("CONVERSATION_CHANNEL", "telegram") # telegram, email, api

 class Config:
 env_file = ".env"
 case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
 """Obtener configuración (cached)"""
 return Settings()
