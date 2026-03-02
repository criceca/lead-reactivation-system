"""
Manejador de Telegram para conversaciones con leads
"""

import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime
from telegram import Update, Chat, User
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction

from app.config import get_settings
from app.database.crud import (
    create_conversation,
    create_message,
    get_conversation,
    update_conversation_status,
    create_escalation,
)
from app.database.db import get_session
from app.agent.agent import LeadReactivationAgent

logger = logging.getLogger(__name__)


class TelegramHandler:
    """Manejador de conversaciones en Telegram"""
    
    def __init__(self):
        self.settings = get_settings()
        self.agent = LeadReactivationAgent()
        self.app: Optional[Application] = None
        self.user_conversations: Dict[int, int] = {}  # telegram_user_id -> conversation_id
    
    async def start(self):
        """Iniciar bot de Telegram"""
        if not self.settings.telegram_bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN no configurada")
            return
        
        try:
            self.app = Application.builder().token(self.settings.telegram_bot_token).build()
            
            # Handlers
            self.app.add_handler(CommandHandler("start", self.handle_start))
            self.app.add_handler(CommandHandler("help", self.handle_help))
            self.app.add_handler(CommandHandler("escalate", self.handle_escalate))
            self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            # Iniciar polling
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling()
            
            logger.info("Bot de Telegram iniciado correctamente")
        except Exception as e:
            logger.error(f"Error iniciando Telegram: {e}")
            raise
    
    async def stop(self):
        """Detener bot de Telegram"""
        if self.app:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()
    
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start - Iniciar conversación"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        logger.info(f"Usuario iniciando conversación: {user.id} ({user.first_name})")
        
        try:
            # Crear conversación en BD
            db = get_session()
            conversation = create_conversation(
                db,
                lead_name=user.first_name or "Usuario Telegram",
                lead_email=f"telegram_{user.id}@telegram.local",
                lead_phone=None,
                channel="telegram",
                telegram_user_id=user.id,
                telegram_chat_id=chat_id,
            )
            db.close()
            
            self.user_conversations[user.id] = conversation.id
            
            # Mensaje de bienvenida
            welcome_msg = (
                f"¡Hola {user.first_name}! 👋\n\n"
                "Soy un asistente de ventas. Estoy aquí para ayudarte con cualquier pregunta "
                "sobre nuestros productos y servicios.\n\n"
                "¿Cómo puedo ayudarte hoy?"
            )
            
            await context.bot.send_message(chat_id=chat_id, text=welcome_msg)
            
            # Generar respuesta inicial del agente
            initial_response = await self.agent.initiate_reactivation(conversation.id)\n            if initial_response:
                await context.bot.send_message(chat_id=chat_id, text=initial_response)
        
        except Exception as e:
            logger.error(f"Error en handle_start: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text="Lo siento, hubo un error. Por favor intenta más tarde."
            )
    
    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help - Mostrar ayuda"""
        help_text = (
            "Comandos disponibles:\n"
            "/start - Iniciar conversación\n"
            "/escalate - Escalar a un agente humano\n"
            "/help - Mostrar esta ayuda\n\n"
            "Simplemente escribe tu mensaje para continuar la conversación."
        )
        await update.message.reply_text(help_text)
    
    async def handle_escalate(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /escalate - Escalar a humano"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        try:
            conversation_id = self.user_conversations.get(user.id)
            if not conversation_id:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="No hay conversación activa. Usa /start para comenzar."
                )
                return
            
            db = get_session()
            
            # Crear escalación
            escalation = create_escalation(
                db,
                conversation_id=conversation_id,
                reason="Usuario solicitó escalación a agente humano",
                escalated_by="telegram_user",
            )
            
            # Actualizar estado de conversación
            update_conversation_status(db, conversation_id, "escalated")
            db.close()
            
            await context.bot.send_message(
                chat_id=chat_id,
                text="Tu caso ha sido escalado a un agente humano. "
                     "Un miembro del equipo se pondrá en contacto contigo pronto."
            )
            
            # Notificar a admin
            if self.settings.telegram_admin_chat_id:
                admin_msg = (
                    f"🔔 Nuevo caso escalado\n"
                    f"Usuario: {user.first_name} ({user.id})\n"
                    f"Conversación ID: {conversation_id}\n"
                    f"Razón: Usuario solicitó escalación"
                )
                await context.bot.send_message(
                    chat_id=self.settings.telegram_admin_chat_id,
                    text=admin_msg
                )
            
            logger.info(f"Caso escalado: {conversation_id}")
        
        except Exception as e:
            logger.error(f"Error en handle_escalate: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text="Error al escalar el caso. Por favor intenta más tarde."
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar mensajes de texto"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        message_text = update.message.text
        
        logger.info(f"Mensaje de {user.id}: {message_text}")
        
        try:
            # Obtener o crear conversación
            conversation_id = self.user_conversations.get(user.id)
            if not conversation_id:
                # Si no existe, crear una nueva
                db = get_session()
                conversation = create_conversation(
                    db,
                    lead_name=user.first_name or "Usuario Telegram",
                    lead_email=f"telegram_{user.id}@telegram.local",
                    lead_phone=None,
                    channel="telegram",
                    telegram_user_id=user.id,
                    telegram_chat_id=chat_id,
                )
                conversation_id = conversation.id
                self.user_conversations[user.id] = conversation_id
                db.close()
            
            # Mostrar indicador de escritura
            await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            
            # Guardar mensaje del usuario
            db = get_session()
            create_message(
                db,
                conversation_id=conversation_id,
                sender="user",
                content=message_text,
            )
            db.close()
            
            # Procesar con el agente
            agent_response = await self.agent.process_lead_response(
                conversation_id=conversation_id,
                user_message=message_text,
            )
            
            # Guardar respuesta del agente
            db = get_session()
            create_message(
                db,
                conversation_id=conversation_id,
                sender="agent",
                content=agent_response,
            )
            db.close()
            
            # Enviar respuesta
            await context.bot.send_message(chat_id=chat_id, text=agent_response)
        
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text="Lo siento, hubo un error procesando tu mensaje. Por favor intenta de nuevo."
            )
    
    async def send_message_to_user(self, telegram_user_id: int, message: str):
        """Enviar mensaje a un usuario específico"""
        try:
            if not self.app or not self.app.bot:
                logger.warning("Bot no inicializado")
                return
            
            await self.app.bot.send_message(chat_id=telegram_user_id, text=message)
        except Exception as e:
            logger.error(f"Error enviando mensaje a {telegram_user_id}: {e}")
    
    async def notify_admin(self, message: str):
        """Notificar al admin"""
        if self.settings.telegram_admin_chat_id:
            await self.send_message_to_user(
                int(self.settings.telegram_admin_chat_id),
                message
            )


# Instancia global
_telegram_handler: Optional[TelegramHandler] = None


def get_telegram_handler() -> TelegramHandler:
    """Obtener manejador de Telegram (singleton)"""
    global _telegram_handler
    if _telegram_handler is None:
        _telegram_handler = TelegramHandler()
    return _telegram_handler
