"""
Manejador mejorado de Telegram con manejo robusto de errores
"""

import logging
from typing import Optional, Dict
from telegram import Update 
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction

from app.config import get_settings
from app.database import crud
from app.database.db import get_db

logger = logging.getLogger(__name__)
settings = get_settings()

class ImprovedTelegramHandler:
    """Manejador mejorado de conversaciones en Telegram"""
    
    def __init__(self):
        self.settings = settings
        self.app: Optional[Application] = None
        self.user_conversations: Dict[int, int] = {}  # telegram_user_id -> conversation_id
    
    async def start(self):
        """Iniciar bot de Telegram"""
        if not self.settings.telegram_bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN no configurada - Bot no iniciado")
            return
    
        try:
            self.app = Application.builder().token(self.settings.telegram_bot_token).build()
    
            # Registrar handlers
            self.app.add_handler(CommandHandler("start", self.handle_start))
            self.app.add_handler(CommandHandler("help", self.handle_help))
            self.app.add_handler(CommandHandler("escalate", self.handle_escalate))
            self.app.add_handler(MessageHandler(
                filters.TEXT & ~filters.COMMAND, 
                self.handle_message
            ))
    
            # Iniciar polling con configuración correcta
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=False  # No ignorar mensajes pendientes
            )
            
            logger.info("Bot de Telegram iniciado correctamente")
            logger.info(f"Bot username: @{(await self.app.bot.get_me()).username}")
    
        except Exception as e:
            logger.error(f"Error iniciando Telegram bot: {e}", exc_info=True)
            raise
    
    async def stop(self):
        """Detener bot de Telegram"""
        try:
            if self.app:
                await self.app.updater.stop()
                await self.app.stop()
                await self.app.shutdown()
                logger.info("Bot de Telegram detenido")
        except Exception as e:
            logger.error(f"Error deteniendo bot: {e}")
    
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start - Iniciar conversación"""
        try:
            user = update.effective_user
            chat_id = update.effective_chat.id
            
            logger.info("=" * 60)
            logger.info(" /start recibido")
            logger.info(f"Usuario ID: {user.id}")
            logger.info(f"Username: @{user.username if user.username else 'sin username'}")
            logger.info(f"Nombre: {user.full_name}")
            logger.info(f"Chat ID: {chat_id}")
            logger.info("=" * 60)
            
            db = next(get_db())
            
            try:
                # PASO 1: Buscar lead existente por teléfono o username de Telegram
                lead = None
                
                # Buscar por username de Telegram
                if user.username:
                    logger.info(f"Buscando lead con username: @{user.username}")
                    all_leads = crud.get_all_leads(db)
                    for potential_lead in all_leads:
                        if potential_lead.phone and f"@{user.username}" in potential_lead.phone:
                            lead = potential_lead
                            logger.info(f"Lead encontrado por username: {lead.id} - {lead.name}")
                            break
                    
                    if not lead:
                        logger.info(f"No se encontró lead con @{user.username}")
                else:
                    logger.warning("Usuario no tiene username de Telegram")
                
                # Buscar por telegram_user_id en email temporal
                if not lead:
                    logger.info(f"Buscando lead por telegram_user_id: {user.id}")
                    lead = crud.get_lead_by_email(db, f"telegram_{user.id}@telegram.local")
                    if lead:
                        logger.info(f"Lead encontrado por user_id: {lead.id} - {lead.name}")
                
                # PASO 2: Si no existe, crear nuevo lead
                if not lead:
                    logger.info("Creando nuevo lead...")
                    lead = crud.create_lead(
                        db=db,
                        name=user.full_name or user.username or "Usuario Telegram",
                        email=f"telegram_{user.id}@telegram.local",
                        phone=f"@{user.username}" if user.username else None,
                        company=None,
                        status="warm",
                        preferred_channel="telegram"
                    )
                    logger.info(f"Nuevo lead creado: {lead.id} - {lead.name}")
                else:
                    if lead.status == "cold":
                        crud.update_lead(db, lead.id, status="warm")
                        logger.info(f"Lead {lead.id} reactivado de cold a warm")
                
                # PASO 3: Crear conversación
                logger.info("Creando conversación...")
                conversation = crud.create_conversation(
                    db=db,
                    lead_id=lead.id,
                    agent_id="telegram-agent",
                    channel="telegram",
                    telegram_user_id=user.id,
                    telegram_chat_id=chat_id,
                )
                logger.info(f"Conversación creada: {conversation.id}")
                
                # Guardar en contexto
                context.user_data['lead_id'] = lead.id
                context.user_data['conversation_id'] = conversation.id
                self.user_conversations[user.id] = conversation.id
                
                # PASO 4: Mensaje de bienvenida
                if lead.status == "cold":
                    welcome_message = f"""¡Hola {lead.name}! 

Me alegra volver a saber de ti. Soy tu asistente de reactivación.

Veo que anteriormente estuviste interesado en nuestros servicios. ¿Te gustaría que conversemos sobre cómo podemos ayudarte ahora?"""
                else:
                    welcome_message = f"""¡Hola {user.first_name}! 

Soy tu asistente de reactivación de leads. Estoy aquí para ayudarte a encontrar las mejores soluciones para tu negocio.

¿En qué puedo ayudarte hoy?"""
                
                welcome_message += """

Comandos disponibles:
/help - Ver ayuda
/escalate - Solicitar hablar con un humano"""
                
                logger.info("Enviando mensaje de bienvenida...")
                await update.message.reply_text(welcome_message)
                
                # PASO 5: Iniciar agente
                logger.info("Iniciando agente...")
                from app.agent.agent import get_agent
                agent = get_agent(db)

                result = agent.initiate_reactivation(
                    lead_id=lead.id,
                    conversation_id=conversation.id
                )
                
                if result.get("success"):
                    await update.message.reply_text(result["message"])
                else:
                    logger.error(f"Error en agente: {result.get('error')}")
                
                logger.info("=" * 60)
                logger.info(" /start procesado exitosamente")
                logger.info("=" * 60)
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error en handle_start: {e}", exc_info=True)
            try:
                await update.message.reply_text(
                    "Lo siento, hubo un error al iniciar la conversación. Por favor, intenta nuevamente."
                )
            except:
                pass
    
    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help - Mostrar ayuda"""
        try:
            help_text = """Comandos disponibles:

/start - Iniciar conversación
/help - Ver esta ayuda
/escalate - Solicitar hablar con un negociador humano

Simplemente escribe tu mensaje y yo te responderé."""
            await update.message.reply_text(help_text)
        except Exception as e:
            logger.error(f"Error en handle_help: {e}", exc_info=True)
    
    async def handle_escalate(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /escalate - Escalar a negociador humano"""
        try:
            conversation_id = context.user_data.get('conversation_id')
            lead_id = context.user_data.get('lead_id')
            
            if not conversation_id or not lead_id:
                await update.message.reply_text(
                    "Por favor, inicia una conversación primero con /start"
                )
                return
            
            db = next(get_db())
            try:
                # Crear escalación
                escalation = crud.create_escalation(
                    db=db,
                    conversation_id=conversation_id,
                    lead_id=lead_id,
                    reason="Escalación solicitada por el usuario vía Telegram",
                    status="pending"
                )
                
                crud.update_conversation(db, conversation_id, status="escalated")
                crud.update_lead(db, lead_id, status="hot")
                
                logger.info(f"Caso escalado: {escalation.id}")
                
                # Notificar admin
                try:
                    await self.notify_admin(
                        f" Nueva escalación #{escalation.id}\n"
                        f"Lead ID: {lead_id}\n"
                        f"Usuario: {update.effective_user.username}\n"
                        f"Razón: Solicitada por usuario"
                    )
                except Exception as notify_error:
                    logger.error(f"Error notificando admin: {notify_error}")
                
                await update.message.reply_text(
                    "Tu caso ha sido escalado a un negociador humano.\n"
                    "Alguien de nuestro equipo se pondrá en contacto contigo pronto."
                )
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error en handle_escalate: {e}", exc_info=True)
            await update.message.reply_text(
                "Lo siento, hubo un error al escalar tu caso. Por favor, intenta nuevamente."
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar mensajes de texto del usuario"""
        try:
            user = update.effective_user
            chat_id = update.effective_chat.id
            message_text = update.message.text
            
            logger.info(f"Mensaje de {user.id}: {message_text[:50]}...")
            
            conversation_id = context.user_data.get('conversation_id')
            lead_id = context.user_data.get('lead_id')
            
            if not conversation_id:
                await update.message.reply_text(
                    "Por favor, inicia una conversación con /start primero."
                )
                return
            
            await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            
            db = next(get_db())
            try:
                conversation = crud.get_conversation(db, conversation_id)
                if conversation.status == "escalated":
                    await update.message.reply_text(
                        "Tu caso ha sido escalado a un negociador humano. "
                        "Alguien se pondrá en contacto contigo pronto."
                    )
                    return
                
                from app.agent.agent import get_agent
                agent = get_agent(db)
                
                result = agent.process_message(
                    conversation_id=conversation_id,
                    lead_message=message_text
                )
                
                if result.get("success"):
                    await update.message.reply_text(result["message"])
                    
                    if result.get("escalated"):
                        await self.notify_admin(
                            f" Escalación automática\n"
                            f"Lead ID: {lead_id}\n"
                            f"Conversación: {conversation_id}\n"
                            f"Usuario: {user.username}"
                        )
                else:
                    await update.message.reply_text(
                        result.get("message", "Lo siento, hubo un error. ¿Podrías reformular tu mensaje?")
                    )
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}", exc_info=True)
            await update.message.reply_text(
                "Lo siento, hubo un error procesando tu mensaje. Por favor, intenta de nuevo."
            )
    
    async def send_message_to_user(self, telegram_user_id: int, message: str):
        """Enviar mensaje a un usuario específico"""
        try:
            if not self.app or not self.app.bot:
                logger.warning("Bot no inicializado")
                return False
            
            await self.app.bot.send_message(chat_id=telegram_user_id, text=message)
            logger.info(f"Mensaje enviado a usuario {telegram_user_id}")
            return True
        except Exception as e:
            logger.error(f"Error enviando mensaje a {telegram_user_id}: {e}")
            return False
    
    async def notify_admin(self, message: str):
        """Notificar al administrador"""
        if self.settings.telegram_admin_chat_id:
            try:
                await self.send_message_to_user(
                    int(self.settings.telegram_admin_chat_id),
                    message
                )
            except Exception as e:
                logger.error(f"Error notificando admin: {e}")
    
    async def initiate_contact_with_lead(self, lead_id: int, message: str) -> bool:
        """Iniciar contacto proactivo con un lead por Telegram"""
        try:
            db = next(get_db())
            try:
                lead = crud.get_lead(db, lead_id)
                if not lead:
                    logger.error(f"Lead {lead_id} no encontrado")
                    return False
                
                if not lead.phone or "@" not in lead.phone:
                    logger.error(f"Lead {lead_id} no tiene username de Telegram")
                    return False
                
                username = lead.phone.replace("@", "").strip()
                conversations = crud.get_conversations_by_lead(db, lead_id)
                telegram_chat_id = next((conv.telegram_chat_id for conv in conversations if conv.telegram_chat_id), None)
                
                if not telegram_chat_id:
                    logger.warning(f"Lead {lead_id} (@{username}) no ha iniciado conversación aún.")
                    return False
                
                success = await self.send_message_to_user(telegram_chat_id, message)
                if success and lead.status == "cold":
                    crud.update_lead(db, lead_id, status="warm")
                return success
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error iniciando contacto con lead {lead_id}: {e}")
            return False

# Instancia global (Singleton)
_telegram_handler: Optional[ImprovedTelegramHandler] = None

def get_telegram_handler() -> ImprovedTelegramHandler:
    """Obtener manejador de Telegram (singleton)"""
    global _telegram_handler
    if _telegram_handler is None:
        _telegram_handler = ImprovedTelegramHandler()
    return _telegram_handler