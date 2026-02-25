"""
Agente LangChain central para reactivación de leads
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import crud

logger = logging.getLogger(__name__)
settings = get_settings()

# Prompt del sistema para el agente negociador
SYSTEM_PROMPT = """Eres un agente de reactivación de leads experto y empático. Tu objetivo es:

1. **Establecer Conexión**: Saludar al lead de manera personal y profesional
2. **Entender Necesidades**: Hacer preguntas abiertas para entender sus necesidades actuales
3. **Ofrecer Valor**: Presentar soluciones relevantes basadas en su historial
4. **Capturar Requerimientos**: Documentar claramente todos los requerimientos mencionados
5. **Determinar Próximos Pasos**: Definir acciones concretas y fechas de seguimiento
6. **Escalar si Necesario**: Reconocer cuándo se requiere un negociador humano

**Comportamiento Esperado:**
- Sé empático y comprensivo con leads que se fueron
- Reconoce por qué se fueron (precio, timing, alternativas)
- Ofrece nuevas propuestas o mejoras
- Mantén un tono profesional pero amigable
- Sé honesto sobre limitaciones
- Propón escalación cuando sea apropiado

**Cuando Escalar:**
- El lead tiene requerimientos muy complejos
- Se requieren decisiones ejecutivas
- El valor del deal es muy alto (>$100k)
- El lead muestra frustración significativa
- Se necesita expertise técnica específica

Recuerda: Tu objetivo es reactivar la relación y generar oportunidades de negocio."""


class LeadReactivationAgent:
    """Agente central para reactivación de leads"""

    def __init__(self):
        """Inicializar el agente"""
        self.llm = ChatOpenAI(
            model_name=settings.llm_model,
            temperature=settings.llm_temperature,
            openai_api_key=settings.openai_api_key,
            max_tokens=2000,
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=4000,
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt, memory=self.memory)
        logger.info("LeadReactivationAgent initialized")

    def initiate_reactivation(
        self,
        lead_id: int,
        lead_name: str,
        lead_email: str,
        lead_history: str = "",
        db: Session = None,
    ) -> str:
        """
        Iniciar conversación de reactivación con un lead
        
        Args:
            lead_id: ID del lead
            lead_name: Nombre del lead
            lead_email: Email del lead
            lead_history: Historial del lead (opcional)
            db: Sesión de base de datos
        
        Returns:
            Respuesta inicial del agente
        """
        try:
            initial_message = f"""Necesito que inicies una conversación de reactivación con {lead_name} ({lead_email}).

Información del lead:
- Nombre: {lead_name}
- Email: {lead_email}
- Historial: {lead_history if lead_history else 'Lead perdido hace tiempo'}

Por favor:
1. Saluda al lead de manera personal
2. Reconoce que hace tiempo no nos comunicamos
3. Expresa interés genuino en sus necesidades actuales
4. Ofrece ayuda o soluciones

Mantén un tono empático y profesional."""

            response = self.chain.run(input=initial_message)
            logger.info(f"Reactivation initiated for lead {lead_id}")
            return response

        except Exception as e:
            logger.error(f"Error initiating reactivation: {e}")
            raise

    def process_lead_response(
        self,
        lead_message: str,
        conversation_history: List[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Procesar respuesta del lead
        
        Args:
            lead_message: Mensaje del lead
            conversation_history: Historial de conversación
        
        Returns:
            Respuesta del agente con análisis
        """
        try:
            # Construir contexto
            context_message = f"""El lead ha respondido: "{lead_message}"

Por favor:
1. Analiza la respuesta del lead
2. Identifica requerimientos mencionados
3. Determina si es necesario escalar
4. Responde al lead de manera apropiada"""

            response = self.chain.run(input=context_message)

            # Analizar respuesta para extraer información
            analysis = self._analyze_response(response, lead_message)

            return {
                "agent_response": response,
                "requirements_identified": analysis["requirements"],
                "should_escalate": analysis["escalate"],
                "sentiment": analysis["sentiment"],
            }

        except Exception as e:
            logger.error(f"Error processing lead response: {e}")
            raise

    def continue_conversation(
        self,
        user_message: str,
    ) -> str:
        """
        Continuar conversación existente
        
        Args:
            user_message: Mensaje del usuario
        
        Returns:
            Respuesta del agente
        """
        try:
            response = self.chain.run(input=user_message)
            logger.info("Conversation continued")
            return response

        except Exception as e:
            logger.error(f"Error continuing conversation: {e}")
            raise

    def _analyze_response(self, agent_response: str, lead_message: str) -> Dict[str, Any]:
        """
        Analizar respuesta del agente para extraer información
        
        Args:
            agent_response: Respuesta del agente
            lead_message: Mensaje del lead
        
        Returns:
            Análisis de la respuesta
        """
        analysis = {
            "requirements": [],
            "escalate": False,
            "sentiment": "neutral",
        }

        # Buscar patrones de requerimientos
        requirement_keywords = [
            "necesita",
            "requiere",
            "solicita",
            "debe",
            "problema",
            "desafío",
        ]
        
        lower_message = lead_message.lower()
        for keyword in requirement_keywords:
            if keyword in lower_message:
                analysis["requirements"].append(lead_message[:100])
                break

        # Determinar si escalar
        escalation_keywords = [
            "complejo",
            "especial",
            "urgente",
            "importante",
            "decisión ejecutiva",
            "frustrado",
            "enojado",
        ]
        
        lower_response = agent_response.lower()
        for keyword in escalation_keywords:
            if keyword in lower_response:
                analysis["escalate"] = True
                break

        # Análisis de sentimiento simple
        positive_words = ["excelente", "perfecto", "interesado", "sí", "claro"]
        negative_words = ["no", "nunca", "imposible", "problema", "difícil"]

        positive_count = sum(1 for word in positive_words if word in lower_message)
        negative_count = sum(1 for word in negative_words if word in lower_message)

        if positive_count > negative_count:
            analysis["sentiment"] = "positive"
        elif negative_count > positive_count:
            analysis["sentiment"] = "negative"

        return analysis

    def get_agent_info(self) -> Dict[str, Any]:
        """Obtener información del agente"""
        return {
            "model": settings.llm_model,
            "timeout": settings.agent_timeout,
            "max_turns": settings.max_conversation_turns,
            "tools": [
                "query_crm",
                "send_contact_email",
                "capture_requirement",
                "escalate_case",
                "analyze_lead_history",
                "update_lead_status",
            ],
        }


# Instancia global del agente
_agent_instance = None


def get_agent() -> LeadReactivationAgent:
    """Obtener instancia del agente (singleton)"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = LeadReactivationAgent()
    return _agent_instance


def reset_agent():
    """Resetear la instancia del agente"""
    global _agent_instance
    _agent_instance = None
