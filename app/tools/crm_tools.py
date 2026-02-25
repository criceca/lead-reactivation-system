"""
Tools de LangChain para interactuar con el CRM y realizar acciones
"""

import json
import logging
from datetime import datetime
from typing import Any

from langchain.tools import tool
from sqlalchemy.orm import Session

from app.database import crud
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@tool
def query_crm(lead_id: int, db: Session) -> str:
    """
    Consulta la base de datos CRM para obtener información del lead.
    
    Args:
        lead_id: ID del lead a consultar
        db: Sesión de base de datos
    
    Returns:
        Información del lead en formato JSON
    """
    try:
        lead = crud.get_lead(db, lead_id)
        if not lead:
            return json.dumps({"error": f"Lead {lead_id} not found"})

        # Obtener conversaciones previas
        conversations = crud.get_conversations_by_lead(db, lead_id)
        conversation_count = len(conversations) if conversations else 0

        # Obtener requerimientos previos
        requirements = crud.get_requirements_by_lead(db, lead_id)
        requirements_list = [
            {"id": r.id, "title": r.title, "priority": r.priority, "status": r.status}
            for r in requirements
        ] if requirements else []

        lead_data = {
            "id": lead.id,
            "name": lead.name,
            "email": lead.email,
            "phone": lead.phone,
            "company": lead.company,
            "status": lead.status,
            "value": lead.value,
            "notes": lead.notes,
            "last_contact": lead.last_contact.isoformat() if lead.last_contact else None,
            "conversation_count": conversation_count,
            "previous_requirements": requirements_list,
        }

        logger.info(f"CRM query for lead {lead_id} completed")
        return json.dumps({"success": True, "data": lead_data})

    except Exception as e:
        logger.error(f"Error querying CRM for lead {lead_id}: {e}")
        return json.dumps({"error": str(e)})


@tool
def send_contact_email(lead_id: int, subject: str, message: str, db: Session) -> str:
    """
    Envía un email de contacto inicial al lead.
    
    Args:
        lead_id: ID del lead
        subject: Asunto del email
        message: Contenido del email
        db: Sesión de base de datos
    
    Returns:
        Confirmación de envío
    """
    try:
        lead = crud.get_lead(db, lead_id)
        if not lead:
            return json.dumps({"error": f"Lead {lead_id} not found"})

        # Aquí se integraría el servicio de email real
        logger.info(f"Email sent to {lead.email}: {subject}")

        # Actualizar last_contact
        crud.update_lead(db, lead_id, last_contact=datetime.utcnow())

        return json.dumps({
            "success": True,
            "message": f"Email sent to {lead.email}",
            "email": lead.email,
        })

    except Exception as e:
        logger.error(f"Error sending email to lead {lead_id}: {e}")
        return json.dumps({"error": str(e)})


@tool
def capture_requirement(
    conversation_id: int,
    lead_id: int,
    title: str,
    description: str,
    priority: str = "medium",
    db: Session = None,
) -> str:
    """
    Captura un requerimiento mencionado durante la conversación.
    
    Args:
        conversation_id: ID de la conversación
        lead_id: ID del lead
        title: Título del requerimiento
        description: Descripción detallada
        priority: Prioridad (low, medium, high, critical)
        db: Sesión de base de datos
    
    Returns:
        Confirmación de captura
    """
    try:
        if not db:
            return json.dumps({"error": "Database session not available"})

        requirement = crud.create_requirement(
            db=db,
            conversation_id=conversation_id,
            lead_id=lead_id,
            title=title,
            description=description,
            priority=priority,
        )

        logger.info(f"Requirement captured: {requirement.id} - {title}")

        return json.dumps({
            "success": True,
            "message": f"Requirement captured: {title}",
            "requirement_id": requirement.id,
        })

    except Exception as e:
        logger.error(f"Error capturing requirement: {e}")
        return json.dumps({"error": str(e)})


@tool
def escalate_case(
    conversation_id: int,
    lead_id: int,
    reason: str,
    db: Session = None,
) -> str:
    """
    Escala un caso a un negociador humano.
    
    Args:
        conversation_id: ID de la conversación
        lead_id: ID del lead
        reason: Razón de la escalación
        db: Sesión de base de datos
    
    Returns:
        Confirmación de escalación
    """
    try:
        if not db:
            return json.dumps({"error": "Database session not available"})

        escalation = crud.create_escalation(
            db=db,
            conversation_id=conversation_id,
            lead_id=lead_id,
            reason=reason,
            status="pending",
        )

        # Actualizar estado de conversación
        crud.update_conversation(db, conversation_id, status="escalated")

        # Notificar al equipo (aquí se integraría el servicio de notificaciones)
        logger.info(f"Case escalated: {escalation.id} - Lead {lead_id}")

        return json.dumps({
            "success": True,
            "message": "Case escalated to human negotiator",
            "escalation_id": escalation.id,
        })

    except Exception as e:
        logger.error(f"Error escalating case: {e}")
        return json.dumps({"error": str(e)})


@tool
def analyze_lead_history(lead_id: int, db: Session = None) -> str:
    """
    Analiza el historial completo del lead para generar insights.
    
    Args:
        lead_id: ID del lead
        db: Sesión de base de datos
    
    Returns:
        Análisis del historial
    """
    try:
        if not db:
            return json.dumps({"error": "Database session not available"})

        lead = crud.get_lead(db, lead_id)
        if not lead:
            return json.dumps({"error": f"Lead {lead_id} not found"})

        conversations = crud.get_conversations_by_lead(db, lead_id)
        requirements = crud.get_requirements_by_lead(db, lead_id)

        analysis = {
            "lead_name": lead.name,
            "total_conversations": len(conversations) if conversations else 0,
            "total_requirements": len(requirements) if requirements else 0,
            "current_status": lead.status,
            "estimated_value": lead.value,
            "last_contact": lead.last_contact.isoformat() if lead.last_contact else "Never",
            "notes": lead.notes,
        }

        logger.info(f"Lead history analyzed: {lead_id}")

        return json.dumps({"success": True, "analysis": analysis})

    except Exception as e:
        logger.error(f"Error analyzing lead history: {e}")
        return json.dumps({"error": str(e)})


@tool
def update_lead_status(lead_id: int, new_status: str, db: Session = None) -> str:
    """
    Actualiza el estado del lead en el CRM.
    
    Args:
        lead_id: ID del lead
        new_status: Nuevo estado (cold, warm, hot, reactivated)
        db: Sesión de base de datos
    
    Returns:
        Confirmación de actualización
    """
    try:
        if not db:
            return json.dumps({"error": "Database session not available"})

        lead = crud.update_lead(db, lead_id, status=new_status)
        if not lead:
            return json.dumps({"error": f"Lead {lead_id} not found"})

        logger.info(f"Lead status updated: {lead_id} -> {new_status}")

        return json.dumps({
            "success": True,
            "message": f"Lead status updated to {new_status}",
            "lead_id": lead_id,
        })

    except Exception as e:
        logger.error(f"Error updating lead status: {e}")
        return json.dumps({"error": str(e)})


# Diccionario de tools disponibles
AVAILABLE_TOOLS = {
    "query_crm": query_crm,
    "send_contact_email": send_contact_email,
    "capture_requirement": capture_requirement,
    "escalate_case": escalate_case,
    "analyze_lead_history": analyze_lead_history,
    "update_lead_status": update_lead_status,
}
