"""
API FastAPI principal para el sistema de reactivación de leads
"""

import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database.db import get_db, init_db
from app.schemas.schemas import (
    LeadCreate,
    LeadResponse,
    LeadUpdate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    RequirementCreate,
    RequirementResponse,
    EscalationResponse,
    DashboardStatsResponse,
    AgentInfoResponse,
    InitiateReactivationRequest,
    InitiateReactivationResponse,
    SendMessageRequest,
    SendMessageResponse,
)
from app.database import crud
from app.agent.agent import get_agent

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

# Crear aplicación FastAPI
app = FastAPI(
    title="Lead Reactivation System API",
    description="API para sistema de reactivación de leads con IA",
    version="1.0.0",
)

# Agregar CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ EVENTOS ============


@app.on_event("startup")
async def startup_event():
    """Evento de inicio"""
    logger.info("Starting Lead Reactivation API...")
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre"""
    logger.info("Shutting down Lead Reactivation API...")


# ============ HEALTH CHECK ============


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Lead Reactivation System API",
        "version": "1.0.0",
        "status": "online",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# ============ LEADS ENDPOINTS ============


@app.get("/api/leads", response_model=list[LeadResponse])
async def get_leads(status: str = "cold", skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener leads por estado"""
    return crud.get_leads_by_status(db, status, skip, limit)


@app.get("/api/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: int, db: Session = Depends(get_db)):
    """Obtener un lead específico"""
    lead = crud.get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@app.post("/api/leads", response_model=LeadResponse)
async def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    """Crear un nuevo lead"""
    existing_lead = crud.get_lead_by_email(db, lead.email)
    if existing_lead:
        raise HTTPException(status_code=400, detail="Lead with this email already exists")
    
    new_lead = crud.create_lead(
        db=db,
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        company=lead.company,
        status=lead.status,
        value=lead.value,
        notes=lead.notes,
    )
    
    # Log audit
    crud.create_audit_log(
        db=db,
        action="CREATE_LEAD",
        entity_type="lead",
        entity_id=new_lead.id,
        details=f"Created lead: {lead.name}",
    )
    
    return new_lead


@app.put("/api/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(lead_id: int, lead: LeadUpdate, db: Session = Depends(get_db)):
    """Actualizar un lead"""
    existing_lead = crud.get_lead(db, lead_id)
    if not existing_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    updated_lead = crud.update_lead(db, lead_id, **lead.dict(exclude_unset=True))
    
    # Log audit
    crud.create_audit_log(
        db=db,
        action="UPDATE_LEAD",
        entity_type="lead",
        entity_id=lead_id,
        details=f"Updated lead: {existing_lead.name}",
    )
    
    return updated_lead


# ============ REACTIVATION ENDPOINTS ============


@app.post("/api/leads/{lead_id}/reactivate", response_model=InitiateReactivationResponse)
async def initiate_reactivation(lead_id: int, db: Session = Depends(get_db)):
    """Iniciar proceso de reactivación de un lead"""
    lead = crud.get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Crear conversación
    conversation = crud.create_conversation(db, lead_id)
    
    # Obtener agente
    agent = get_agent()
    
    # Generar respuesta inicial
    try:
        agent_response = agent.initiate_reactivation(
            lead_id=lead_id,
            lead_name=lead.name,
            lead_email=lead.email,
            lead_history=lead.notes or "",
            db=db,
        )
    except Exception as e:
        logger.error(f"Error initiating reactivation: {e}")
        agent_response = f"Error: {str(e)}"
    
    # Guardar mensaje del agente
    crud.create_message(
        db=db,
        conversation_id=conversation.id,
        role="agent",
        content=agent_response,
    )
    
    # Log audit
    crud.create_audit_log(
        db=db,
        action="REACTIVATION_INITIATED",
        entity_type="conversation",
        entity_id=conversation.id,
        details=f"Initiated reactivation for lead: {lead.name}",
    )
    
    return {
        "success": True,
        "message": "Reactivation process initiated",
        "conversation_id": conversation.id,
        "agent_response": agent_response,
    }


# ============ CONVERSATIONS ENDPOINTS ============


@app.get("/api/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Obtener una conversación"""
    conversation = crud.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@app.post("/api/conversations/{conversation_id}/message", response_model=SendMessageResponse)
async def send_message(
    conversation_id: int,
    message: SendMessageRequest,
    db: Session = Depends(get_db),
):
    """Enviar mensaje en una conversación"""
    conversation = crud.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Guardar mensaje del lead
    crud.create_message(
        db=db,
        conversation_id=conversation_id,
        role=message.role,
        content=message.content,
    )
    
    # Obtener agente
    agent = get_agent()
    
    # Procesar respuesta
    try:
        result = agent.process_lead_response(message.content)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        result = {
            "agent_response": f"Error: {str(e)}",
            "requirements_identified": [],
            "should_escalate": False,
            "sentiment": "neutral",
        }
    
    # Guardar respuesta del agente
    crud.create_message(
        db=db,
        conversation_id=conversation_id,
        role="agent",
        content=result["agent_response"],
    )
    
    # Crear requerimientos si se identificaron
    for requirement in result["requirements_identified"]:
        crud.create_requirement(
            db=db,
            conversation_id=conversation_id,
            lead_id=conversation.lead_id,
            title=requirement[:255],
            description=requirement,
            priority="medium",
        )
    
    # Escalar si es necesario
    if result["should_escalate"]:
        crud.create_escalation(
            db=db,
            conversation_id=conversation_id,
            lead_id=conversation.lead_id,
            reason="Complex case requiring human negotiator",
            status="pending",
        )
        crud.update_conversation(db, conversation_id, status="escalated")
    
    # Log audit
    crud.create_audit_log(
        db=db,
        action="MESSAGE_PROCESSED",
        entity_type="message",
        details=f"Processed message in conversation {conversation_id}",
    )
    
    return {
        "success": True,
        "message": "Message processed",
        "agent_response": result["agent_response"],
        "requirements_identified": result["requirements_identified"],
        "escalated": result["should_escalate"],
    }


# ============ REQUIREMENTS ENDPOINTS ============


@app.get("/api/requirements/{conversation_id}", response_model=list[RequirementResponse])
async def get_requirements(conversation_id: int, db: Session = Depends(get_db)):
    """Obtener requerimientos de una conversación"""
    return crud.get_requirements_by_conversation(db, conversation_id)


# ============ ESCALATIONS ENDPOINTS ============


@app.get("/api/escalations", response_model=list[EscalationResponse])
async def get_escalations(status: str = "pending", db: Session = Depends(get_db)):
    """Obtener casos escalados"""
    return crud.get_escalations_by_status(db, status)


# ============ AGENT ENDPOINTS ============


@app.get("/api/agent/info", response_model=AgentInfoResponse)
async def get_agent_info():
    """Obtener información del agente"""
    agent = get_agent()
    info = agent.get_agent_info()
    return info


# ============ DASHBOARD ENDPOINTS ============


@app.get("/api/dashboard/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Obtener estadísticas del dashboard"""
    cold_leads = crud.get_leads_by_status(db, "cold")
    warm_leads = crud.get_leads_by_status(db, "warm")
    hot_leads = crud.get_leads_by_status(db, "hot")
    reactivated_leads = crud.get_leads_by_status(db, "reactivated")
    pending_escalations = crud.get_escalations_by_status(db, "pending")
    
    return {
        "cold_leads": len(cold_leads) if cold_leads else 0,
        "warm_leads": len(warm_leads) if warm_leads else 0,
        "hot_leads": len(hot_leads) if hot_leads else 0,
        "reactivated_leads": len(reactivated_leads) if reactivated_leads else 0,
        "pending_escalations": len(pending_escalations) if pending_escalations else 0,
        "total_leads": (len(cold_leads) if cold_leads else 0) + 
                      (len(warm_leads) if warm_leads else 0) + 
                      (len(hot_leads) if hot_leads else 0),
    }


# ============ ERROR HANDLERS ============


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Manejador de excepciones HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Manejador general de excepciones"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error"},
    )
