"""
Schemas Pydantic para validación de datos
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List


# ============ LEAD SCHEMAS ============


class LeadBase(BaseModel):
    """Schema base para leads"""

    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    company: Optional[str] = Field(None, max_length=255)
    status: str = Field(default="cold", max_length=50)
    value: float = Field(default=0, ge=0)
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    """Schema para crear leads"""

    pass


class LeadUpdate(BaseModel):
    """Schema para actualizar leads"""

    name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    status: Optional[str] = None
    value: Optional[float] = None
    notes: Optional[str] = None


class LeadResponse(LeadBase):
    """Schema para respuestas de leads"""

    id: int
    last_contact: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ CONVERSATION SCHEMAS ============


class ConversationBase(BaseModel):
    """Schema base para conversaciones"""

    lead_id: int
    agent_id: str = "lead-reactivation-agent"
    status: str = "active"


class ConversationCreate(ConversationBase):
    """Schema para crear conversaciones"""

    pass


class ConversationUpdate(BaseModel):
    """Schema para actualizar conversaciones"""

    status: Optional[str] = None
    s3_key: Optional[str] = None


class ConversationResponse(ConversationBase):
    """Schema para respuestas de conversaciones"""

    id: int
    s3_key: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ MESSAGE SCHEMAS ============


class MessageBase(BaseModel):
    """Schema base para mensajes"""

    role: str = Field(..., max_length=50)
    content: str


class MessageCreate(MessageBase):
    """Schema para crear mensajes"""

    pass


class MessageResponse(MessageBase):
    """Schema para respuestas de mensajes"""

    id: int
    conversation_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ REQUIREMENT SCHEMAS ============


class RequirementBase(BaseModel):
    """Schema base para requerimientos"""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: str = Field(default="medium", max_length=50)


class RequirementCreate(RequirementBase):
    """Schema para crear requerimientos"""

    pass


class RequirementUpdate(BaseModel):
    """Schema para actualizar requerimientos"""

    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class RequirementResponse(RequirementBase):
    """Schema para respuestas de requerimientos"""

    id: int
    conversation_id: int
    lead_id: int
    status: str
    s3_key: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ ESCALATION SCHEMAS ============


class EscalationBase(BaseModel):
    """Schema base para escalaciones"""

    reason: str
    status: str = "pending"


class EscalationCreate(EscalationBase):
    """Schema para crear escalaciones"""

    pass


class EscalationUpdate(BaseModel):
    """Schema para actualizar escalaciones"""

    status: Optional[str] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None


class EscalationResponse(EscalationBase):
    """Schema para respuestas de escalaciones"""

    id: int
    conversation_id: int
    lead_id: int
    assigned_to: Optional[str] = None
    notes: Optional[str] = None
    s3_key: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ AGENT SCHEMAS ============


class AgentInfoResponse(BaseModel):
    """Schema para información del agente"""

    model: str
    timeout: int
    max_turns: int
    tools: List[str]


# ============ DASHBOARD SCHEMAS ============


class DashboardStatsResponse(BaseModel):
    """Schema para estadísticas del dashboard"""

    cold_leads: int
    warm_leads: int
    hot_leads: int
    reactivated_leads: int
    pending_escalations: int
    total_leads: int


# ============ CONVERSATION FLOW SCHEMAS ============


class InitiateReactivationRequest(BaseModel):
    """Schema para iniciar reactivación"""

    lead_id: int


class InitiateReactivationResponse(BaseModel):
    """Schema para respuesta de reactivación iniciada"""

    success: bool
    message: str
    conversation_id: int
    agent_response: str


class SendMessageRequest(BaseModel):
    """Schema para enviar mensaje"""

    content: str
    role: str = "lead"


class SendMessageResponse(BaseModel):
    """Schema para respuesta de mensaje enviado"""

    success: bool
    message: str
    agent_response: str
    requirements_identified: List[str]
    escalated: bool


class ProcessLeadResponseRequest(BaseModel):
    """Schema para procesar respuesta del lead"""

    content: str


class ProcessLeadResponseResponse(BaseModel):
    """Schema para respuesta de procesamiento"""

    agent_response: str
    requirements_identified: List[str]
    should_escalate: bool
