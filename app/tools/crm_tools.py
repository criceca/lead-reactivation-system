"""
Tools mejorados de LangChain con inyección de dependencias
"""

import json
import logging
from datetime import datetime
from typing import List

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import crud

logger = logging.getLogger(__name__)


# ============ Input Schemas para Tools ============

class QueryCRMInput(BaseModel):
 """Input para query_crm"""
 lead_id: int = Field(..., description="ID del lead a consultar")


class AnalyzeLeadHistoryInput(BaseModel):
 """Input para analyze_lead_history"""
 lead_id: int = Field(..., description="ID del lead a analizar")


class CaptureRequirementInput(BaseModel):
 """Input para capture_requirement"""
 conversation_id: int = Field(..., description="ID de la conversación")
 lead_id: int = Field(..., description="ID del lead")
 title: str = Field(..., description="Título breve del requerimiento")
 description: str = Field(..., description="Descripción detallada del requerimiento")
 priority: str = Field(default="medium", description="Prioridad: low, medium, high, critical")


class EscalateCaseInput(BaseModel):
 """Input para escalate_case"""
 conversation_id: int = Field(..., description="ID de la conversación")
 lead_id: int = Field(..., description="ID del lead")
 reason: str = Field(..., description="Razón detallada de la escalación")


class UpdateLeadStatusInput(BaseModel):
 """Input para update_lead_status"""
 lead_id: int = Field(..., description="ID del lead")
 new_status: str = Field(..., description="Nuevo estado: cold, warm, hot, reactivated")


# ============ Tool Functions ============

def create_query_crm_tool(db: Session):
 """Crear tool query_crm con sesión de DB inyectada"""
 
 def query_crm(lead_id: int) -> str:
 """
 Consulta la base de datos CRM para obtener información completa del lead.
 Usa esta herramienta al inicio de la conversación para entender el contexto del lead.
 """
 try:
 lead = crud.get_lead(db, lead_id)
 if not lead:
 return json.dumps({"error": f"Lead {lead_id} no encontrado"})

 # Obtener conversaciones previas
 conversations = crud.get_conversations_by_lead(db, lead_id)
 conversation_count = len(conversations) if conversations else 0

 # Obtener requerimientos previos
 requirements = crud.get_requirements_by_lead(db, lead_id)
 requirements_list = [
 {
 "id": r.id,
 "title": r.title,
 "priority": r.priority,
 "status": r.status,
 "created_at": r.created_at.isoformat()
 }
 for r in requirements
 ] if requirements else []

 # Obtener escalaciones previas
 escalations = crud.get_escalations_by_lead(db, lead_id)
 escalation_count = len(escalations) if escalations else 0

 lead_data = {
 "id": lead.id,
 "name": lead.name,
 "email": lead.email,
 "phone": lead.phone,
 "company": lead.company,
 "status": lead.status,
 "value": lead.value,
 "notes": lead.notes,
 "preferred_channel": lead.preferred_channel,
 "last_contact": lead.last_contact.isoformat() if lead.last_contact else None,
 "created_at": lead.created_at.isoformat(),
 "conversation_count": conversation_count,
 "escalation_count": escalation_count,
 "previous_requirements": requirements_list,
 }

 logger.info(f" CRM query for lead {lead_id} completed")
 return json.dumps({"success": True, "data": lead_data}, indent=2)

 except Exception as e:
 logger.error(f" Error querying CRM for lead {lead_id}: {e}")
 return json.dumps({"error": str(e)})
 
 return StructuredTool.from_function(
 func=query_crm,
 name="query_crm",
 description="Consulta información completa del lead en el CRM. Usa esto al inicio para obtener contexto.",
 args_schema=QueryCRMInput,
 )


def create_analyze_lead_history_tool(db: Session):
 """Crear tool analyze_lead_history con sesión de DB inyectada"""
 
 def analyze_lead_history(lead_id: int) -> str:
 """
 Analiza el historial completo del lead incluyendo conversaciones y requerimientos.
 Usa esta herramienta para entender el contexto histórico antes de hacer propuestas.
 """
 try:
 lead = crud.get_lead(db, lead_id)
 if not lead:
 return json.dumps({"error": f"Lead {lead_id} no encontrado"})

 # Obtener conversaciones con mensajes
 conversations = crud.get_conversations_by_lead(db, lead_id)
 conversation_summaries = []
 
 for conv in conversations:
 messages = crud.get_messages_by_conversation(db, conv.id)
 message_count = len(messages) if messages else 0
 
 conversation_summaries.append({
 "id": conv.id,
 "status": conv.status,
 "channel": conv.channel,
 "message_count": message_count,
 "created_at": conv.created_at.isoformat(),
 })

 # Obtener requerimientos
 requirements = crud.get_requirements_by_lead(db, lead_id)
 requirement_summaries = [
 {
 "title": r.title,
 "description": r.description,
 "priority": r.priority,
 "status": r.status,
 }
 for r in requirements
 ] if requirements else []

 # Obtener escalaciones
 escalations = crud.get_escalations_by_lead(db, lead_id)
 escalation_summaries = [
 {
 "reason": e.reason,
 "status": e.status,
 "created_at": e.created_at.isoformat(),
 }
 for e in escalations
 ] if escalations else []

 analysis = {
 "lead_name": lead.name,
 "company": lead.company,
 "current_status": lead.status,
 "estimated_value": lead.value,
 "last_contact": lead.last_contact.isoformat() if lead.last_contact else "Nunca",
 "notes": lead.notes,
 "total_conversations": len(conversation_summaries),
 "conversations": conversation_summaries,
 "total_requirements": len(requirement_summaries),
 "requirements": requirement_summaries,
 "total_escalations": len(escalation_summaries),
 "escalations": escalation_summaries,
 }

 logger.info(f" Lead history analyzed: {lead_id}")
 return json.dumps({"success": True, "analysis": analysis}, indent=2)

 except Exception as e:
 logger.error(f" Error analyzing lead history: {e}")
 return json.dumps({"error": str(e)})
 
 return StructuredTool.from_function(
 func=analyze_lead_history,
 name="analyze_lead_history",
 description="Analiza el historial completo del lead con conversaciones y requerimientos previos.",
 args_schema=AnalyzeLeadHistoryInput,
 )


def create_capture_requirement_tool(db: Session):
 """Crear tool capture_requirement con sesión de DB inyectada"""
 
 def capture_requirement(
 conversation_id: int,
 lead_id: int,
 title: str,
 description: str,
 priority: str = "medium",
 ) -> str:
 """
 Captura un requerimiento mencionado por el lead durante la conversación.
 USA ESTA HERRAMIENTA SIEMPRE que el lead mencione una necesidad, problema o solicitud específica.
 """
 try:
 # Validar prioridad
 valid_priorities = ["low", "medium", "high", "critical"]
 if priority not in valid_priorities:
 priority = "medium"

 requirement = crud.create_requirement(
 db=db,
 conversation_id=conversation_id,
 lead_id=lead_id,
 title=title,
 description=description,
 priority=priority,
 )

 logger.info(f" Requirement captured: {requirement.id} - {title}")

 return json.dumps({
 "success": True,
 "message": f"Requerimiento capturado exitosamente: {title}",
 "requirement_id": requirement.id,
 "priority": priority,
 })

 except Exception as e:
 logger.error(f" Error capturing requirement: {e}")
 return json.dumps({"error": str(e)})
 
 return StructuredTool.from_function(
 func=capture_requirement,
 name="capture_requirement",
 description="Captura requerimientos mencionados por el lead. USA SIEMPRE que detectes una necesidad específica.",
 args_schema=CaptureRequirementInput,
 )


def create_escalate_case_tool(db: Session):
 """Crear tool escalate_case con sesión de DB inyectada"""
 
 def escalate_case(
 conversation_id: int,
 lead_id: int,
 reason: str,
 ) -> str:
 """
 Escala el caso a un negociador humano cuando la situación lo requiere.
 USA ESTA HERRAMIENTA cuando:
 - Los requerimientos son muy complejos o técnicos
 - Se necesitan decisiones ejecutivas o descuentos especiales
 - El lead muestra frustración
 - El valor del deal es muy alto (>$100k)
 - Han pasado más de 5 intercambios sin progreso
 """
 try:
 escalation = crud.create_escalation(
 db=db,
 conversation_id=conversation_id,
 lead_id=lead_id,
 reason=reason,
 status="pending",
 )

 # Actualizar estado de conversación
 crud.update_conversation(db, conversation_id, status="escalated")

 # Actualizar estado del lead
 crud.update_lead(db, lead_id, status="hot")

 logger.info(f" Case escalated: {escalation.id} - Lead {lead_id}")

 return json.dumps({
 "success": True,
 "message": "Caso escalado exitosamente a un negociador humano",
 "escalation_id": escalation.id,
 "next_steps": "Un negociador humano se pondrá en contacto pronto",
 })

 except Exception as e:
 logger.error(f" Error escalating case: {e}")
 return json.dumps({"error": str(e)})
 
 return StructuredTool.from_function(
 func=escalate_case,
 name="escalate_case",
 description="Escala el caso a un negociador humano cuando la situación lo requiere.",
 args_schema=EscalateCaseInput,
 )


def create_update_lead_status_tool(db: Session):
 """Crear tool update_lead_status con sesión de DB inyectada"""
 
 def update_lead_status(lead_id: int, new_status: str) -> str:
 """
 Actualiza el estado del lead en el CRM.
 Estados válidos: cold, warm, hot, reactivated
 """
 try:
 # Validar estado
 valid_statuses = ["cold", "warm", "hot", "reactivated", "lost"]
 if new_status not in valid_statuses:
 return json.dumps({
 "error": f"Estado inválido. Debe ser uno de: {', '.join(valid_statuses)}"
 })

 lead = crud.update_lead(db, lead_id, status=new_status)
 if not lead:
 return json.dumps({"error": f"Lead {lead_id} no encontrado"})

 logger.info(f" Lead status updated: {lead_id} -> {new_status}")

 return json.dumps({
 "success": True,
 "message": f"Estado del lead actualizado a {new_status}",
 "lead_id": lead_id,
 "new_status": new_status,
 })

 except Exception as e:
 logger.error(f" Error updating lead status: {e}")
 return json.dumps({"error": str(e)})
 
 return StructuredTool.from_function(
 func=update_lead_status,
 name="update_lead_status",
 description="Actualiza el estado del lead en el CRM (cold, warm, hot, reactivated).",
 args_schema=UpdateLeadStatusInput,
 )


# ============ Factory Function ============

def get_crm_tools(db: Session) -> List[StructuredTool]:
 """
 Obtener todas las herramientas CRM con sesión de DB inyectada
 
 Args:
 db: Sesión de base de datos
 
 Returns:
 Lista de herramientas configuradas
 """
 tools = [
 create_query_crm_tool(db),
 create_analyze_lead_history_tool(db),
 create_capture_requirement_tool(db),
 create_escalate_case_tool(db),
 create_update_lead_status_tool(db),
 ]
 
 logger.info(f" Created {len(tools)} CRM tools with DB session")
 return tools
