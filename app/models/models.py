"""
Modelos SQLAlchemy para la base de datos
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class Lead(Base):
    """Modelo para leads del CRM"""

    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    company = Column(String(255))
    status = Column(String(50), default="cold", index=True)  # cold, warm, hot, reactivated
    value = Column(Float, default=0)
    notes = Column(Text)
    last_contact = Column(DateTime)
    
    # Campo de canal preferido
    preferred_channel = Column(String(50), default="telegram")  # telegram, email, api
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    conversations = relationship("Conversation", back_populates="lead")
    requirements = relationship("Requirement", back_populates="lead")
    escalations = relationship("Escalation", back_populates="lead")

    def __repr__(self):
        return f"<Lead(id={self.id}, name={self.name}, email={self.email}, status={self.status})>"


class Conversation(Base):
    """Modelo para conversaciones con leads"""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False, index=True)
    agent_id = Column(String(255), default="lead-reactivation-agent")
    channel = Column(String(50), default="api", index=True)  # telegram, email, api
    status = Column(String(50), default="active", index=True)  # active, completed, escalated
    s3_key = Column(String(500))  # Clave de S3 para almacenar conversación
    
    # Campos de Telegram
    telegram_user_id = Column(Integer, index=True)  # ID del usuario en Telegram
    telegram_chat_id = Column(Integer, index=True)  # ID del chat en Telegram
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    lead = relationship("Lead", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")
    requirements = relationship("Requirement", back_populates="conversation")
    escalation = relationship("Escalation", back_populates="conversation", uselist=False)

    def __repr__(self):
        return f"<Conversation(id={self.id}, lead_id={self.lead_id}, status={self.status})>"


class Message(Base):
    """Modelo para mensajes individuales en conversaciones"""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # agent, lead, system
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, role={self.role})>"


class Requirement(Base):
    """Modelo para requerimientos capturados durante conversaciones"""

    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    priority = Column(String(50), default="medium")  # low, medium, high, critical
    status = Column(String(50), default="captured")  # captured, confirmed, completed
    s3_key = Column(String(500))  # Clave de S3 para documentación
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    conversation = relationship("Conversation", back_populates="requirements")
    lead = relationship("Lead", back_populates="requirements")

    def __repr__(self):
        return f"<Requirement(id={self.id}, title={self.title}, priority={self.priority})>"


class Escalation(Base):
    """Modelo para casos escalados a negociadores humanos"""

    __tablename__ = "escalations"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False, index=True)
    reason = Column(Text, nullable=False)
    status = Column(String(50), default="pending", index=True)  # pending, assigned, resolved
    assigned_to = Column(String(255))  # Email o ID del negociador
    notes = Column(Text)
    s3_key = Column(String(500))  # Clave de S3 para documentación de escalación
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    conversation = relationship("Conversation", back_populates="escalation")
    lead = relationship("Lead", back_populates="escalations")

    def __repr__(self):
        return f"<Escalation(id={self.id}, lead_id={self.lead_id}, status={self.status})>"


class AuditLog(Base):
    """Modelo para logs de auditoría"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(255), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(Integer)
    details = Column(Text)
    s3_key = Column(String(500))  # Clave de S3 para logs completos
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, entity_type={self.entity_type})>"


class User(Base):
    """Modelo para usuarios del sistema"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(50), default="user")  # user, negotiator, admin
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
