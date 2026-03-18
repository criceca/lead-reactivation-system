"""
Agente simplificado compatible con LangChain actual
"""

import logging
import json
from typing import List, Dict, Any
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import crud
from app.llm.llm_provider import get_llm_provider
from app.tools.crm_tools import get_crm_tools

logger = logging.getLogger(__name__)
settings = get_settings()

SYSTEM_PROMPT = """Eres un agente de reactivación de leads experto y empático.

Tu objetivo es reactivar leads perdidos mediante conversaciones naturales y profesionales.

Comportamiento:
- Sé empático y comprensivo
- Haz preguntas abiertas para entender necesidades
- Ofrece soluciones relevantes
- Mantén respuestas concisas (máximo 3-4 párrafos)
- Propón escalación cuando sea necesario

Cuándo escalar:
- Requerimientos muy complejos
- Decisiones ejecutivas necesarias
- Valor del deal >$100k
- Lead muestra frustración
- Más de 5 intercambios sin progreso"""


class SimpleLeadReactivationAgent:
 """Agente simplificado para reactivación de leads"""

 def __init__(self, db: Session):
 self.db = db
 llm_provider = get_llm_provider()
 self.llm = llm_provider.get_llm()
 self.llm_provider = llm_provider.get_provider()
 self.tools = get_crm_tools(db)
 
 logger.info(f" Agent initialized with {self.llm_provider}")
 logger.info(f" {len(self.tools)} tools available")

 def load_conversation_memory(self, conversation_id: int) -> List:
 """Cargar historial de conversación"""
 try:
 messages = crud.get_messages_by_conversation(self.db, conversation_id)
 chat_history = []
 
 if messages:
 for msg in messages:
 if msg.role == "agent":
 chat_history.append(AIMessage(content=msg.content))
 elif msg.role == "lead":
 chat_history.append(HumanMessage(content=msg.content))
 
 logger.info(f"Loaded {len(chat_history)} messages for conversation {conversation_id}")
 return chat_history
 except Exception as e:
 logger.error(f"Error loading memory: {e}")
 return []

 def initiate_reactivation(self, lead_id: int, conversation_id: int) -> Dict[str, Any]:
 """Iniciar reactivación de un lead"""
 try:
 lead = crud.get_lead(self.db, lead_id)
 if not lead:
 raise ValueError(f"Lead {lead_id} not found")

 initial_message = f"""Inicia una conversación de reactivación con:
- Nombre: {lead.name}
- Email: {lead.email}
- Empresa: {lead.company or 'No especificada'}
- Estado: {lead.status}
- Notas: {lead.notes or 'Sin notas'}

Saluda de manera personal y pregunta cómo puedes ayudar."""

 # Crear mensajes para el LLM
 messages = [
 SystemMessage(content=SYSTEM_PROMPT),
 HumanMessage(content=initial_message)
 ]
 
 # Invocar LLM
 response = self.llm.invoke(messages)
 response_text = response.content if hasattr(response, 'content') else str(response)

 # Guardar mensaje
 crud.create_message(
 db=self.db,
 conversation_id=conversation_id,
 role="agent",
 content=response_text
 )

 # Actualizar lead
 crud.update_lead(
 self.db,
 lead_id,
 status="warm",
 last_contact=datetime.utcnow()
 )

 logger.info(f" Reactivation initiated for lead {lead_id}")

 return {
 "success": True,
 "message": response_text,
 "conversation_id": conversation_id,
 }

 except Exception as e:
 logger.error(f" Error initiating reactivation: {e}")
 return {
 "success": False,
 "error": str(e),
 "message": "Lo siento, hubo un error al iniciar la conversación."
 }

 def process_message(self, conversation_id: int, lead_message: str) -> Dict[str, Any]:
 """Procesar mensaje del lead"""
 try:
 # Guardar mensaje del lead
 crud.create_message(
 db=self.db,
 conversation_id=conversation_id,
 role="lead",
 content=lead_message
 )

 # Cargar historial
 chat_history = self.load_conversation_memory(conversation_id)

 # Crear mensajes
 messages = [
 SystemMessage(content=SYSTEM_PROMPT),
 *chat_history,
 HumanMessage(content=lead_message)
 ]

 # Invocar LLM
 response = self.llm.invoke(messages)
 response_text = response.content if hasattr(response, 'content') else str(response)

 # Guardar respuesta
 crud.create_message(
 db=self.db,
 conversation_id=conversation_id,
 role="agent",
 content=response_text
 )

 # Análisis simple
 response_lower = response_text.lower()
 escalated = "escalar" in response_lower or "escalación" in response_lower
 requirements_captured = "requerimiento" in response_lower

 logger.info(f" Message processed for conversation {conversation_id}")

 return {
 "success": True,
 "message": response_text,
 "tools_used": [],
 "escalated": escalated,
 "requirements_captured": requirements_captured,
 }

 except Exception as e:
 logger.error(f" Error processing message: {e}")
 return {
 "success": False,
 "error": str(e),
 "message": "Lo siento, hubo un error procesando tu mensaje."
 }

 def get_conversation_summary(self, conversation_id: int) -> Dict[str, Any]:
 """Generar resumen de conversación"""
 try:
 messages = crud.get_messages_by_conversation(self.db, conversation_id)
 
 if not messages:
 return {"summary": "No hay mensajes en esta conversación"}
 
 conversation_text = "\n".join([
 f"{msg.role.upper()}: {msg.content}"
 for msg in messages
 ])
 
 summary_prompt = f"""Analiza esta conversación y proporciona un resumen en JSON:

{conversation_text}

Formato JSON:
{{
 "resumen_general": "Resumen breve",
 "requerimientos_mencionados": ["req1", "req2"],
 "siguiente_paso": "Qué hacer",
 "sentimiento": "positive/neutral/negative",
 "probabilidad_cierre": 50
}}"""

 response = self.llm.invoke([HumanMessage(content=summary_prompt)])
 response_text = response.content if hasattr(response, 'content') else str(response)
 
 try:
 summary = json.loads(response_text)
 except:
 summary = {"summary": response_text}
 
 return summary
 
 except Exception as e:
 logger.error(f"Error generating summary: {e}")
 return {"error": str(e)}

 def get_agent_info(self) -> Dict[str, Any]:
 """Obtener información del agente"""
 return {
 "provider": self.llm_provider,
 "model": settings.llm_model if not settings.use_bedrock else settings.bedrock_model,
 "timeout": settings.agent_timeout,
 "max_turns": settings.max_conversation_turns,
 "tools": [tool.name for tool in self.tools],
 "debug_mode": settings.agent_debug,
 }


def get_agent(db: Session) -> SimpleLeadReactivationAgent:
 """Obtener instancia del agente"""
 return SimpleLeadReactivationAgent(db)
