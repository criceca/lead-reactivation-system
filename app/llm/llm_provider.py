"""
Proveedor de LLM que soporta OpenAI y AWS Bedrock
Implementación según documentación oficial de LangChain
"""

import json
import logging
from typing import Optional
from app.config import get_settings

logger = logging.getLogger(__name__)


class LLMProvider:
    """Proveedor de LLM flexible que soporta múltiples backends"""
    
    def __init__(self):
        self.settings = get_settings()
        self._init_llm()
    
    def _init_llm(self):
        """Inicializar el LLM según la configuración"""
        if self.settings.use_bedrock:
            self._init_bedrock()
        else:
            self._init_openai()
    
    def _init_openai(self):
        """Inicializar OpenAI"""
        try:
            from langchain_openai import ChatOpenAI
            
            if not self.settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY no configurada")
            
            self.llm = ChatOpenAI(
                model_name=self.settings.llm_model,
                temperature=self.settings.llm_temperature,
                api_key=self.settings.openai_api_key,
                max_tokens=2000,
            )
            self.provider = "openai"
            logger.info(f"✓ LLM inicializado con OpenAI: {self.settings.llm_model}")
        except Exception as e:
            logger.error(f"✗ Error inicializando OpenAI: {e}")
            raise
    
    def _init_bedrock(self):
        """Inicializar AWS Bedrock usando ChatBedrockConverse (RECOMENDADO)"""
        try:
            from langchain_aws import ChatBedrockConverse
            
            # Usar ChatBedrockConverse en lugar de ChatBedrock
            # ChatBedrockConverse usa la API Converse unificada y es más confiable
            self.llm = ChatBedrockConverse(
                model_id=self.settings.bedrock_model,
                region_name=self.settings.bedrock_region,
                temperature=self.settings.llm_temperature,
                max_tokens=2000,
                # Credenciales se obtienen de variables de entorno automáticamente
                # AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN
            )
            self.provider = "bedrock"
            logger.info(f"✓ LLM inicializado con AWS Bedrock: {self.settings.bedrock_model}")
        except ImportError:
            logger.error("✗ langchain-aws no está instalado. Ejecuta: pip install -qU langchain-aws")
            raise
        except Exception as e:
            logger.error(f"✗ Error inicializando AWS Bedrock: {e}")
            logger.error("Verifica que:")
            logger.error("  1. AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY estén configuradas")
            logger.error("  2. El modelo esté habilitado en tu cuenta AWS Bedrock")
            logger.error("  3. La región sea correcta")
            raise
    
    def get_llm(self):
        """Obtener instancia del LLM"""
        return self.llm
    
    def get_provider(self) -> str:
        """Obtener nombre del proveedor"""
        return self.provider
    
    def get_model_info(self) -> dict:
        """Obtener información del modelo"""
        if self.provider == "openai":
            return {
                "provider": "openai",
                "model": self.settings.llm_model,
                "temperature": self.settings.llm_temperature,
            }
        else:
            return {
                "provider": "bedrock",
                "model": self.settings.bedrock_model,
                "region": self.settings.bedrock_region,
                "temperature": self.settings.llm_temperature,
            }


# Instancia global del proveedor
_llm_provider: Optional[LLMProvider] = None


def get_llm_provider() -> LLMProvider:
    """Obtener proveedor de LLM (singleton)"""
    global _llm_provider
    if _llm_provider is None:
        _llm_provider = LLMProvider()
    return _llm_provider


def reinit_llm_provider():
    """Reinicializar el proveedor de LLM (útil para tests)"""
    global _llm_provider
    _llm_provider = None
    return get_llm_provider()
