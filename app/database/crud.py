"""
Funciones CRUD para acceso a la base de datos
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
import logging

from app.models.models import (
    Lead,
    Conversation,
    Message,
    Requirement,
    Escalation,
    AuditLog,
    User,
)

logger = logging.getLogger(__name__)


# ============ LEADS ============


def get_lead(db: Session, lead_id: int) -> Lead:
    """Obtener un lead por ID"""
    return db.query(Lead).filter(Lead.id == lead_id).first()


def get_lead_by_email(db: Session, email: str) -> Lead:
    """Obtener un lead por email"""
    return db.query(Lead).filter(Lead.email == email).first()


def get_leads_by_status(db: Session, status: str, skip: int = 0, limit: int = 100) -> list[Lead]:
    """Obtener leads por estado"""
    return db.query(Lead).filter(Lead.status == status).offset(skip).limit(limit).all()


def get_all_leads(db: Session, skip: int = 0, limit: int = 100) -> list[Lead]:
    """Obtener todos los leads"""
    return db.query(Lead).offset(skip).limit(limit).all()


def create_lead(
    db: Session,
    name: str,
    email: str,
    phone: str = None,
    company: str = None,
    status: str = "cold",
    value: float = 0,
    notes: str = None,
) -> Lead:
    """Crear un nuevo lead"""
    lead = Lead(
        name=name,
        email=email,
        phone=phone,
        company=company,
        status=status,
        value=value,
        notes=notes,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    logger.info(f"Lead created: {lead.id} - {name}")
    return lead


def update_lead(db: Session, lead_id: int, **kwargs) -> Lead:
    """Actualizar un lead"""
    lead = get_lead(db, lead_id)
    if lead:
        for key, value in kwargs.items():
            if hasattr(lead, key):
                setattr(lead, key, value)
        lead.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(lead)
        logger.info(f"Lead updated: {lead_id}")
    return lead


def delete_lead(db: Session, lead_id: int) -> bool:
    """Eliminar un lead"""
    lead = get_lead(db, lead_id)
    if lead:
        db.delete(lead)
        db.commit()
        logger.info(f"Lead deleted: {lead_id}")
        return True
    return False


# ============ CONVERSATIONS ============


def get_conversation(db: Session, conversation_id: int) -> Conversation:
    """Obtener una conversación por ID"""
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()


def get_conversations_by_lead(db: Session, lead_id: int) -> list[Conversation]:
    """Obtener conversaciones de un lead"""
    return (
        db.query(Conversation)
        .filter(Conversation.lead_id == lead_id)
        .order_by(desc(Conversation.created_at))
        .all()
    )


def create_conversation(
    db: Session, lead_id: int, agent_id: str = "lead-reactivation-agent", status: str = "active"
) -> Conversation:
    """Crear una nueva conversación"""
    conversation = Conversation(lead_id=lead_id, agent_id=agent_id, status=status)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    logger.info(f"Conversation created: {conversation.id} for lead {lead_id}")
    return conversation


def update_conversation(db: Session, conversation_id: int, **kwargs) -> Conversation:
    """Actualizar una conversación"""
    conversation = get_conversation(db, conversation_id)
    if conversation:
        for key, value in kwargs.items():
            if hasattr(conversation, key):
                setattr(conversation, key, value)
        conversation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(conversation)
    return conversation


# ============ MESSAGES ============


def get_message(db: Session, message_id: int) -> Message:
    """Obtener un mensaje por ID"""
    return db.query(Message).filter(Message.id == message_id).first()


def get_messages_by_conversation(db: Session, conversation_id: int) -> list[Message]:
    """Obtener mensajes de una conversación"""
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .all()
    )


def create_message(
    db: Session, conversation_id: int, role: str, content: str
) -> Message:
    """Crear un nuevo mensaje"""
    message = Message(conversation_id=conversation_id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    logger.info(f"Message created: {message.id} in conversation {conversation_id}")
    return message


# ============ REQUIREMENTS ============


def get_requirement(db: Session, requirement_id: int) -> Requirement:
    """Obtener un requerimiento por ID"""
    return db.query(Requirement).filter(Requirement.id == requirement_id).first()


def get_requirements_by_conversation(db: Session, conversation_id: int) -> list[Requirement]:
    """Obtener requerimientos de una conversación"""
    return (
        db.query(Requirement)
        .filter(Requirement.conversation_id == conversation_id)
        .order_by(desc(Requirement.priority))
        .all()
    )


def get_requirements_by_lead(db: Session, lead_id: int) -> list[Requirement]:
    """Obtener requerimientos de un lead"""
    return (
        db.query(Requirement)
        .filter(Requirement.lead_id == lead_id)
        .order_by(desc(Requirement.priority))
        .all()
    )


def create_requirement(
    db: Session,
    conversation_id: int,
    lead_id: int,
    title: str,
    description: str = None,
    priority: str = "medium",
) -> Requirement:
    """Crear un nuevo requerimiento"""
    requirement = Requirement(
        conversation_id=conversation_id,
        lead_id=lead_id,
        title=title,
        description=description,
        priority=priority,
    )
    db.add(requirement)
    db.commit()
    db.refresh(requirement)
    logger.info(f"Requirement created: {requirement.id} - {title}")
    return requirement


def update_requirement(db: Session, requirement_id: int, **kwargs) -> Requirement:
    """Actualizar un requerimiento"""
    requirement = get_requirement(db, requirement_id)
    if requirement:
        for key, value in kwargs.items():
            if hasattr(requirement, key):
                setattr(requirement, key, value)
        requirement.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(requirement)
    return requirement


# ============ ESCALATIONS ============


def get_escalation(db: Session, escalation_id: int) -> Escalation:
    """Obtener una escalación por ID"""
    return db.query(Escalation).filter(Escalation.id == escalation_id).first()


def get_escalations_by_status(db: Session, status: str) -> list[Escalation]:
    """Obtener escalaciones por estado"""
    return (
        db.query(Escalation)
        .filter(Escalation.status == status)
        .order_by(desc(Escalation.created_at))
        .all()
    )


def get_escalations_by_lead(db: Session, lead_id: int) -> list[Escalation]:
    """Obtener escalaciones de un lead"""
    return (
        db.query(Escalation)
        .filter(Escalation.lead_id == lead_id)
        .order_by(desc(Escalation.created_at))
        .all()
    )


def create_escalation(
    db: Session,
    conversation_id: int,
    lead_id: int,
    reason: str,
    status: str = "pending",
) -> Escalation:
    """Crear una nueva escalación"""
    escalation = Escalation(
        conversation_id=conversation_id, lead_id=lead_id, reason=reason, status=status
    )
    db.add(escalation)
    db.commit()
    db.refresh(escalation)
    logger.info(f"Escalation created: {escalation.id} for lead {lead_id}")
    return escalation


def update_escalation(db: Session, escalation_id: int, **kwargs) -> Escalation:
    """Actualizar una escalación"""
    escalation = get_escalation(db, escalation_id)
    if escalation:
        for key, value in kwargs.items():
            if hasattr(escalation, key):
                setattr(escalation, key, value)
        escalation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(escalation)
    return escalation


# ============ AUDIT LOGS ============


def create_audit_log(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: int = None,
    details: str = None,
) -> AuditLog:
    """Crear un log de auditoría"""
    audit_log = AuditLog(action=action, entity_type=entity_type, entity_id=entity_id, details=details)
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    logger.info(f"Audit log created: {action} - {entity_type}")
    return audit_log


def get_audit_logs(db: Session, skip: int = 0, limit: int = 100) -> list[AuditLog]:
    """Obtener logs de auditoría"""
    return (
        db.query(AuditLog)
        .order_by(desc(AuditLog.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


# ============ USERS ============


def get_user(db: Session, user_id: int) -> User:
    """Obtener un usuario por ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User:
    """Obtener un usuario por email"""
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, email: str, name: str, role: str = "user") -> User:
    """Crear un nuevo usuario"""
    user = User(email=email, name=name, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"User created: {user.id} - {email}")
    return user
