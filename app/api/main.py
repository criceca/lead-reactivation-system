"""
API FastAPI mejorada para el sistema de reactivación de leads
"""

import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database.db import get_db, init_db
from app.schemas.schemas import (
 LeadCreate,
 LeadUpdate,
 Lead,
 Conversation,
 Message,
 Requirement,
 Escalation,
 DashboardStats,
 ConversationMessage,
 Channel,
)
from app.database import crud
from app.agent.agent import get_agent

# Configuración de logging
logging.basicConfig(
 level=logging.INFO,
 format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Crear aplicación FastAPI
app = FastAPI(
 title="Lead Reactivation System API",
 description="API mejorada para sistema de reactivación de leads con IA",
 version="2.0.0",
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
 logger.info("=" * 60)
 logger.info("Starting Lead Reactivation API v2.0...")
 logger.info("=" * 60)
 try:
 init_db()
 logger.info(" Database initialized")
 logger.info(f" LLM Provider: {settings.llm_provider if hasattr(settings, 'llm_provider') else 'OpenAI'}")
 logger.info(f" Environment: {settings.environment}")
 except Exception as e:
 logger.error(f" Error initializing database: {e}")


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
 "version": "2.0.0",
 "status": "online",
 "features": [
 "LangChain Agent with Tools",
 "Persistent Conversation Memory",
 "Automatic Requirement Capture",
 "Smart Escalation",
 "Multi-channel Support"
 ]
 }


@app.get("/health")
async def health_check():
 """Health check endpoint"""
 return {"status": "healthy", "version": "2.0.0"}


# ============ LEADS ENDPOINTS ============

@app.get("/api/leads", response_model=list[Lead])
async def get_leads(
 status: str = "cold",
 skip: int = 0,
 limit: int = 100,
 db: Session = Depends(get_db)
):
 """Obtener leads por estado"""
 try:
 leads = crud.get_leads_by_status(db, status, skip, limit)
 return leads if leads else []
 except Exception as e:
 logger.error(f" Error getting leads: {e}")
 raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/leads/{lead_id}", response_model=Lead)
async def get_lead(lead_id: int, db: Session = Depends(get_db)):
 """Obtener un lead específico"""
 lead = crud.get_lead(db, lead_id)
 if not lead:
 raise HTTPException(status_code=404, detail="Lead not found")
 return lead


@app.post("/api/leads", response_model=Lead)
async def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
 """Crear un nuevo lead"""
 try:
 # Validar que leads con canal Telegram tengan teléfono
 if lead.preferred_channel == Channel.TELEGRAM and not lead.phone:
 raise HTTPException(
 status_code=400, 
 detail="Phone number is required for Telegram channel"
 )
 
 existing_lead = crud.get_lead_by_email(db, lead.email)
 if existing_lead:
 raise HTTPException(
 status_code=400,
 detail="Lead with this email already exists"
 )
 
 new_lead = crud.create_lead(
 db=db,
 name=lead.name,
 email=lead.email,
 phone=lead.phone,
 company=lead.company,
 status=lead.status.value,
 value=lead.value,
 notes=lead.notes,
 preferred_channel=lead.preferred_channel.value,
 )
 
 # Log audit
 crud.create_audit_log(
 db=db,
 action="CREATE_LEAD",
 entity_type="lead",
 entity_id=new_lead.id,
 details=f"Created lead: {lead.name}",
 )
 
 logger.info(f" Lead created: {new_lead.id} - {new_lead.name}")
 return new_lead
 
 except HTTPException:
 raise
 except Exception as e:
 logger.error(f" Error creating lead: {e}")
 raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/leads/{lead_id}", response_model=Lead)
async def update_lead(
 lead_id: int,
 lead: LeadUpdate,
 db: Session = Depends(get_db)
):
 """Actualizar un lead"""
 try:
 existing_lead = crud.get_lead(db, lead_id)
 if not existing_lead:
 raise HTTPException(status_code=404, detail="Lead not found")
 
 # Convertir enums a valores
 update_data = lead.model_dump(exclude_unset=True)
 if 'status' in update_data and update_data['status']:
 update_data['status'] = update_data['status'].value
 if 'preferred_channel' in update_data and update_data['preferred_channel']:
 update_data['preferred_channel'] = update_data['preferred_channel'].value
 
 updated_lead = crud.update_lead(db, lead_id, **update_data)
 
 # Log audit
 crud.create_audit_log(
 db=db,
 action="UPDATE_LEAD",
 entity_type="lead",
 entity_id=lead_id,
 details=f"Updated lead: {existing_lead.name}",
 )
 
 logger.info(f" Lead updated: {lead_id}")
 return updated_lead
 
 except HTTPException:
 raise
 except Exception as e:
 logger.error(f" Error updating lead: {e}")
 raise HTTPException(status_code=500, detail=str(e))


# ============ REACTIVATION ENDPOINTS ============

@app.post("/api/leads/{lead_id}/reactivate")
async def initiate_reactivation(lead_id: int, db: Session = Depends(get_db)):
 """Iniciar proceso de reactivación de un lead"""
 try:
 lead = crud.get_lead(db, lead_id)
 if not lead:
 raise HTTPException(status_code=404, detail="Lead not found")
 
 # Verificar si el lead tiene Telegram como canal preferido
 if lead.preferred_channel == "telegram":
 # Intentar contacto proactivo por Telegram
 from app.telegram.telegram_handler import get_telegram_handler
 telegram_handler = get_telegram_handler()
 
 # Crear conversación primero
 conversation = crud.create_conversation(
 db=db,
 lead_id=lead_id,
 agent_id="lead-reactivation-agent",
 channel="telegram",
 )
 
 # Obtener agente para generar mensaje inicial
 agent = get_agent(db)
 result = agent.initiate_reactivation(
 lead_id=lead_id,
 conversation_id=conversation.id,
 )
 
 # Intentar enviar por Telegram
 telegram_sent = await telegram_handler.initiate_contact_with_lead(
 lead_id=lead_id,
 message=result.get("message", "Hola, ¿cómo estás?")
 )
 
 if telegram_sent:
 logger.info(f" Mensaje enviado por Telegram a lead {lead_id}")
 return {
 "success": True,
 "message": "Reactivation initiated via Telegram",
 "conversation_id": conversation.id,
 "agent_response": result.get("message", ""),
 "channel": "telegram",
 "telegram_sent": True,
 }
 else:
 logger.warning(f" No se pudo enviar por Telegram, el lead debe iniciar /start primero")
 return {
 "success": True,
 "message": "Reactivation prepared. Lead needs to start conversation with /start",
 "conversation_id": conversation.id,
 "agent_response": result.get("message", ""),
 "channel": "telegram",
 "telegram_sent": False,
 "note": "Lead must send /start to the bot first"
 }
 
 # Si no es Telegram, usar el flujo normal (API)
 conversation = crud.create_conversation(
 db=db,
 lead_id=lead_id,
 agent_id="lead-reactivation-agent",
 channel="api",
 )
 
 # Obtener agente mejorado con sesión de DB
 agent = get_agent(db)
 
 # Iniciar reactivación
 result = agent.initiate_reactivation(
 lead_id=lead_id,
 conversation_id=conversation.id,
 )
 
 # Log audit
 crud.create_audit_log(
 db=db,
 action="REACTIVATION_INITIATED",
 entity_type="conversation",
 entity_id=conversation.id,
 details=f"Initiated reactivation for lead: {lead.name}",
 )
 
 logger.info(f" Reactivation initiated for lead {lead_id}")
 
 return {
 "success": result.get("success", True),
 "message": "Reactivation process initiated",
 "conversation_id": conversation.id,
 "agent_response": result.get("message", ""),
 "tools_used": [str(step) for step in result.get("intermediate_steps", [])],
 "channel": "api",
 }
 
 except HTTPException:
 raise
 except Exception as e:
 logger.error(f" Error initiating reactivation: {e}", exc_info=True)
 raise HTTPException(status_code=500, detail=str(e))


# ============ CONVERSATIONS ENDPOINTS ============

@app.get("/api/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
 """Obtener una conversación"""
 conversation = crud.get_conversation(db, conversation_id)
 if not conversation:
 raise HTTPException(status_code=404, detail="Conversation not found")
 return conversation


@app.post("/api/conversations/{conversation_id}/message")
async def send_message(
 conversation_id: int,
 message: ConversationMessage,
 db: Session = Depends(get_db),
):
 """Enviar mensaje en una conversación"""
 try:
 conversation = crud.get_conversation(db, conversation_id)
 if not conversation:
 raise HTTPException(status_code=404, detail="Conversation not found")
 
 # Verificar si está escalada
 if conversation.status == "escalated":
 return {
 "success": False,
 "message": "Conversation is escalated to human negotiator",
 "agent_response": "Esta conversación ha sido escalada a un negociador humano.",
 }
 
 # Obtener agente mejorado
 agent = get_agent(db)
 
 # Procesar mensaje
 result = agent.process_message(
 conversation_id=conversation_id,
 lead_message=message.message,
 )
 
 # Log audit
 crud.create_audit_log(
 db=db,
 action="MESSAGE_PROCESSED",
 entity_type="message",
 details=f"Processed message in conversation {conversation_id}",
 )
 
 logger.info(f" Message processed in conversation {conversation_id}")
 logger.info(f" Tools used: {result.get('tools_used', [])}")
 
 return {
 "success": result.get("success", True),
 "message": "Message processed",
 "agent_response": result.get("message", ""),
 "requirements_captured": result.get("requirements_captured", False),
 "escalated": result.get("escalated", False),
 "tools_used": result.get("tools_used", []),
 }
 
 except HTTPException:
 raise
 except Exception as e:
 logger.error(f" Error processing message: {e}", exc_info=True)
 raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/conversations/{conversation_id}/summary")
async def get_conversation_summary(
 conversation_id: int,
 db: Session = Depends(get_db)
):
 """Obtener resumen de conversación generado por el agente"""
 try:
 conversation = crud.get_conversation(db, conversation_id)
 if not conversation:
 raise HTTPException(status_code=404, detail="Conversation not found")
 
 agent = get_agent(db)
 summary = agent.get_conversation_summary(conversation_id)
 
 return {
 "success": True,
 "conversation_id": conversation_id,
 "summary": summary,
 }
 
 except HTTPException:
 raise
 except Exception as e:
 logger.error(f" Error getting summary: {e}")
 raise HTTPException(status_code=500, detail=str(e))


# ============ REQUIREMENTS ENDPOINTS ============

@app.get("/api/requirements/{conversation_id}", response_model=list[Requirement])
async def get_requirements(conversation_id: int, db: Session = Depends(get_db)):
 """Obtener requerimientos de una conversación"""
 requirements = crud.get_requirements_by_conversation(db, conversation_id)
 return requirements if requirements else []


# ============ ESCALATIONS ENDPOINTS ============

@app.get("/api/escalations", response_model=list[Escalation])
async def get_escalations(status: str = "pending", db: Session = Depends(get_db)):
 """Obtener casos escalados"""
 escalations = crud.get_escalations_by_status(db, status)
 return escalations if escalations else []


# ============ AGENT ENDPOINTS ============

@app.get("/api/agent/info")
async def get_agent_info(db: Session = Depends(get_db)):
 """Obtener información del agente"""
 try:
 agent = get_agent(db)
 info = agent.get_agent_info()
 return info
 except Exception as e:
 logger.error(f" Error getting agent info: {e}")
 raise HTTPException(status_code=500, detail=str(e))


# ============ DASHBOARD ENDPOINTS ============

@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
 """Obtener estadísticas del dashboard"""
 try:
 cold_leads = crud.get_leads_by_status(db, "cold")
 warm_leads = crud.get_leads_by_status(db, "warm")
 hot_leads = crud.get_leads_by_status(db, "hot")
 reactivated_leads = crud.get_leads_by_status(db, "reactivated")
 pending_escalations = crud.get_escalations_by_status(db, "pending")
 
 # Contar conversaciones activas y requerimientos
 all_leads = crud.get_all_leads(db)
 active_conversations = 0
 total_requirements = 0
 
 if all_leads:
 for lead in all_leads:
 conversations = crud.get_conversations_by_lead(db, lead.id)
 if conversations:
 active_conversations += sum(
 1 for c in conversations if c.status == "active"
 )
 requirements = crud.get_requirements_by_lead(db, lead.id)
 if requirements:
 total_requirements += len(requirements)
 
 return {
 "total_leads": len(all_leads) if all_leads else 0,
 "cold_leads": len(cold_leads) if cold_leads else 0,
 "warm_leads": len(warm_leads) if warm_leads else 0,
 "hot_leads": len(hot_leads) if hot_leads else 0,
 "reactivated_leads": len(reactivated_leads) if reactivated_leads else 0,
 "active_conversations": active_conversations,
 "pending_escalations": len(pending_escalations) if pending_escalations else 0,
 "total_requirements": total_requirements,
 }
 except Exception as e:
 logger.error(f" Error getting dashboard stats: {e}")
 raise HTTPException(status_code=500, detail=str(e))


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
 logger.error(f" Unhandled exception: {exc}", exc_info=True)
 return JSONResponse(
 status_code=500,
 content={"success": False, "error": "Internal server error"},
 )
