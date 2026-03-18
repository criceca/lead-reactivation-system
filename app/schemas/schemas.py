"""
Schemas Pydantic para validación de datos
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator
from enum import Enum


# ============ Enums ============

class LeadStatus(str, Enum):
 """Estados válidos para leads"""
 COLD = "cold"
 WARM = "warm"
 HOT = "hot"
 REACTIVATED = "reactivated"
 LOST = "lost"


class ConversationStatus(str, Enum):
 """Estados válidos para conversaciones"""
 ACTIVE = "active"
 COMPLETED = "completed"
 ESCALATED = "escalated"
 PAUSED = "paused"


class RequirementPriority(str, Enum):
 """Prioridades válidas para requerimientos"""
 LOW = "low"
 MEDIUM = "medium"
 HIGH = "high"
 CRITICAL = "critical"


class RequirementStatus(str, Enum):
 """Estados válidos para requerimientos"""
 CAPTURED = "captured"
 CONFIRMED = "confirmed"
 IN_PROGRESS = "in_progress"
 COMPLETED = "completed"


class EscalationStatus(str, Enum):
 """Estados válidos para escalaciones"""
 PENDING = "pending"
 ASSIGNED = "assigned"
 IN_PROGRESS = "in_progress"
 RESOLVED = "resolved"


class Channel(str, Enum):
 """Canales de comunicación válidos"""
 TELEGRAM = "telegram"
 EMAIL = "email"
 API = "api"
 WHATSAPP = "whatsapp"


class MessageRole(str, Enum):
 """Roles válidos para mensajes"""
 AGENT = "agent"
 LEAD = "lead"
 SYSTEM = "system"


# ============ Lead Schemas ============

class LeadBase(BaseModel):
 """Schema base para Lead"""
 name: str = Field(..., min_length=1, max_length=255)
 email: EmailStr
 phone: Optional[str] = Field(None, max_length=20)
 company: Optional[str] = Field(None, max_length=255)
 status: LeadStatus = LeadStatus.COLD
 value: float = Field(default=0, ge=0)
 notes: Optional[str] = None
 preferred_channel: Channel = Channel.TELEGRAM


class LeadCreate(LeadBase):
 """Schema para crear Lead"""
 pass


class LeadUpdate(BaseModel):
 """Schema para actualizar Lead"""
 name: Optional[str] = Field(None, min_length=1, max_length=255)
 email: Optional[EmailStr] = None
 phone: Optional[str] = Field(None, max_length=20)
 company: Optional[str] = Field(None, max_length=255)
 status: Optional[LeadStatus] = None
 value: Optional[float] = Field(None, ge=0)
 notes: Optional[str] = None
 preferred_channel: Optional[Channel] = None
 last_contact: Optional[datetime] = None


class Lead(LeadBase):
 """Schema completo de Lead"""
 id: int
 last_contact: Optional[datetime] = None
 created_at: datetime
 updated_at: datetime

 class Config:
 from_attributes = True


# ============ Conversation Schemas ============

class ConversationBase(BaseModel):
 """Schema base para Conversation"""
 lead_id: int
 channel: Channel = Channel.API
 status: ConversationStatus = ConversationStatus.ACTIVE


class ConversationCreate(ConversationBase):
 """Schema para crear Conversation"""
 telegram_user_id: Optional[int] = None
 telegram_chat_id: Optional[int] = None


class ConversationUpdate(BaseModel):
 """Schema para actualizar Conversation"""
 status: Optional[ConversationStatus] = None
 s3_key: Optional[str] = None


class Conversation(ConversationBase):
 """Schema completo de Conversation"""
 id: int
 agent_id: str
 telegram_user_id: Optional[int] = None
 telegram_chat_id: Optional[int] = None
 s3_key: Optional[str] = None
 created_at: datetime
 updated_at: datetime

 class Config:
 from_attributes = True


# ============ Message Schemas ============

class MessageBase(BaseModel):
 """Schema base para Message"""
 conversation_id: int
 role: MessageRole
 content: str = Field(..., min_length=1)


class MessageCreate(MessageBase):
 """Schema para crear Message"""
 pass


class Message(MessageBase):
 """Schema completo de Message"""
 id: int
 created_at: datetime

 class Config:
 from_attributes = True


# ============ Requirement Schemas ============

class RequirementBase(BaseModel):
 """Schema base para Requirement"""
 conversation_id: int
 lead_id: int
 title: str = Field(..., min_length=1, max_length=255)
 description: Optional[str] = None
 priority: RequirementPriority = RequirementPriority.MEDIUM
 status: RequirementStatus = RequirementStatus.CAPTURED


class RequirementCreate(RequirementBase):
 """Schema para crear Requirement"""
 pass


class RequirementUpdate(BaseModel):
 """Schema para actualizar Requirement"""
 title: Optional[str] = Field(None, min_length=1, max_length=255)
 description: Optional[str] = None
 priority: Optional[RequirementPriority] = None
 status: Optional[RequirementStatus] = None
 s3_key: Optional[str] = None


class Requirement(RequirementBase):
 """Schema completo de Requirement"""
 id: int
 s3_key: Optional[str] = None
 created_at: datetime
 updated_at: datetime

 class Config:
 from_attributes = True


# ============ Escalation Schemas ============

class EscalationBase(BaseModel):
 """Schema base para Escalation"""
 conversation_id: int
 lead_id: int
 reason: str = Field(..., min_length=1)
 status: EscalationStatus = EscalationStatus.PENDING


class EscalationCreate(EscalationBase):
 """Schema para crear Escalation"""
 pass


class EscalationUpdate(BaseModel):
 """Schema para actualizar Escalation"""
 status: Optional[EscalationStatus] = None
 assigned_to: Optional[str] = None
 notes: Optional[str] = None
 s3_key: Optional[str] = None


class Escalation(EscalationBase):
 """Schema completo de Escalation"""
 id: int
 assigned_to: Optional[str] = None
 notes: Optional[str] = None
 s3_key: Optional[str] = None
 created_at: datetime
 updated_at: datetime

 class Config:
 from_attributes = True


# ============ Agent Schemas ============

class AgentResponse(BaseModel):
 """Schema para respuesta del agente"""
 message: str
 requirements_identified: List[str] = []
 should_escalate: bool = False
 sentiment: str = "neutral"
 confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class ConversationMessage(BaseModel):
 """Schema para mensaje en conversación"""
 conversation_id: int
 message: str = Field(..., min_length=1)


class ReactivationRequest(BaseModel):
 """Schema para solicitud de reactivación"""
 lead_id: int
 initial_message: Optional[str] = None


# ============ Dashboard Schemas ============

class DashboardStats(BaseModel):
 """Schema para estadísticas del dashboard"""
 total_leads: int
 cold_leads: int
 warm_leads: int
 hot_leads: int
 reactivated_leads: int
 active_conversations: int
 pending_escalations: int
 total_requirements: int


# ============ Response Schemas ============

class ConversationResponse(BaseModel):
 """Schema para respuesta de conversación"""
 id: int
 lead_id: int
 agent_id: str
 channel: Channel
 status: ConversationStatus
 telegram_user_id: Optional[int] = None
 telegram_chat_id: Optional[int] = None
 s3_key: Optional[str] = None
 created_at: datetime
 updated_at: datetime
 messages: List[Message] = []

 class Config:
 from_attributes = True


class RequirementResponse(BaseModel):
 """Schema para respuesta de requerimiento"""
 id: int
 conversation_id: int
 lead_id: int
 title: str
 description: Optional[str] = None
 priority: RequirementPriority
 status: RequirementStatus
 s3_key: Optional[str] = None
 created_at: datetime
 updated_at: datetime

 class Config:
 from_attributes = True


class EscalationResponse(BaseModel):
 """Schema para respuesta de escalación"""
 id: int
 conversation_id: int
 lead_id: int
 reason: str
 status: EscalationStatus
 assigned_to: Optional[str] = None
 notes: Optional[str] = None
 s3_key: Optional[str] = None
 created_at: datetime
 updated_at: datetime

 class Config:
 from_attributes = True


class AgentInfoResponse(BaseModel):
 """Schema para información del agente"""
 name: str
 version: str
 model: str
 tools: List[str] = []
 capabilities: List[str] = []


class DashboardStatsResponse(BaseModel):
 """Schema para respuesta de estadísticas del dashboard"""
 cold_leads: int
 warm_leads: int
 hot_leads: int
 reactivated_leads: int
 pending_escalations: int
 total_leads: int
