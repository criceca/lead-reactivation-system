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
            # Todos los proveedores compatibles con OpenAI API
            self._init_openai_compatible()

    def _init_openai_compatible(self):
        """Inicializar cualquier proveedor compatible con OpenAI API"""
        try:
            from langchain_openai import ChatOpenAI

            # Configuración por proveedor
            providers = {
                "openai": {
                    "api_key": self.settings.openai_api_key,
                    "base_url": None,  # Usa default de OpenAI
                    "model": self.settings.llm_model,
                    "headers": {},
                    "display_name": "OpenAI"
                },
                "openrouter": {
                    "api_key": self.settings.openrouter_api_key,
                    "base_url": "https://openrouter.ai/api/v1",
                    "model": self.settings.openrouter_model,
                    "headers": {
                        "HTTP-Referer": self.settings.openrouter_site_url,
                        "X-Title": self.settings.openrouter_app_name,
                    },
                    "display_name": "OpenRouter"
                },
                "deepseek": {
                    "api_key": self.settings.deepseek_api_key,
                    "base_url": "https://api.deepseek.com/v1",
                    "model": self.settings.deepseek_model,
                    "headers": {},
                    "display_name": "DeepSeek"
                }
            }

            # Detectar proveedor activo (orden de prioridad)
            if self.settings.use_openrouter:
                provider_name = "openrouter"
            elif self.settings.use_deepseek:
                provider_name = "deepseek"
            elif self.settings.use_openai:
                provider_name = "openai"
            else:
                # Si ninguno está activado, error
                raise ValueError(
                    "Ningún proveedor LLM activado. "
                    "Configura USE_OPENAI=True, USE_OPENROUTER=True, USE_DEEPSEEK=True o USE_BEDROCK=True en .env"
                )

            config = providers[provider_name]

            # Validar API key
            if not config["api_key"]:
                raise ValueError(f"{provider_name.upper()}_API_KEY no configurada")

            # Crear LLM con configuración unificada
            llm_params = {
                "model_name": config["model"],
                "temperature": self.settings.llm_temperature,
                "api_key": config["api_key"],
                "max_tokens": 2000,
            }

            # Agregar base_url si no es OpenAI default
            if config["base_url"]:
                llm_params["base_url"] = config["base_url"]

            # Agregar headers personalizados si existen
            if config["headers"]:
                llm_params["default_headers"] = config["headers"]

            self.llm = ChatOpenAI(**llm_params)
            self.provider = provider_name
            logger.info(f" LLM inicializado con {config['display_name']}: {config['model']}")

        except Exception as e:
            logger.error(f" Error inicializando LLM: {e}")
            raise

    def _init_bedrock(self):
        """Inicializar AWS Bedrock usando ChatBedrockConverse (RECOMENDADO)"""
        try:
            from langchain_aws import ChatBedrockConverse

            # Usar ChatBedrockConverse en lugar de ChatBedrock
            self.llm = ChatBedrockConverse(
                model_id=self.settings.bedrock_model,
                region_name=self.settings.bedrock_region,
                temperature=self.settings.llm_temperature,
                max_tokens=2000,
            )
            self.provider = "bedrock"
            logger.info(f" LLM inicializado con AWS Bedrock: {self.settings.bedrock_model}")
        except ImportError:
            logger.error(" langchain-aws no está instalado. Ejecuta: pip install -qU langchain-aws")
            raise
        except Exception as e:
            logger.error(f" Error inicializando AWS Bedrock: {e}")
            logger.error("Verifica credenciales, habilitación del modelo y región.")
            raise

    def get_llm(self):
        """Obtener instancia del LLM"""
        return self.llm

    def get_provider(self) -> str:
        """Obtener nombre del proveedor"""
        return self.provider

    def get_model_info(self) -> dict:
        """Obtener información del modelo"""
        if self.provider == "bedrock":
            return {
                "provider": "bedrock",
                "model": self.settings.bedrock_model,
                "region": self.settings.bedrock_region,
                "temperature": self.settings.llm_temperature,
            }
        elif self.provider == "openrouter":
            return {
                "provider": "openrouter",
                "model": self.settings.openrouter_model,
                "temperature": self.settings.llm_temperature,
            }
        elif self.provider == "deepseek":
            return {
                "provider": "deepseek",
                "model": self.settings.deepseek_model,
                "temperature": self.settings.llm_temperature,
            }
        else:  # openai
            return {
                "provider": "openai",
                "model": self.settings.llm_model,
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