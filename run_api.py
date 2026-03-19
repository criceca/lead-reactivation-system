"""
Script para ejecutar la API FastAPI
"""

import uvicorn
import logging
from app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

if __name__ == "__main__":
    logger.info(f"Starting FastAPI server on {settings.api_host}:{settings.api_port}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"LLM Model: {settings.llm_model}")
    
    uvicorn.run(
        "app.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers if settings.environment == "production" else 1,
        reload=settings.api_reload,
        log_level=settings.log_level.lower(),
    )
