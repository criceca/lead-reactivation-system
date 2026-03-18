#!/usr/bin/env python3
"""
Bot de prueba simple para verificar que Telegram funciona
"""

import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from app.config import get_settings

logging.basicConfig(
 level=logging.INFO,
 format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
 """Comando /start"""
 user = update.effective_user
 logger.info(f" /start recibido de {user.username} (ID: {user.id})")
 
 await update.message.reply_text(
 f"¡Hola {user.first_name}! \n\n"
 f"Tu username es: @{user.username}\n"
 f"Tu ID es: {user.id}\n\n"
 f" El bot está funcionando correctamente!"
 )


async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
 """Eco de mensajes"""
 user = update.effective_user
 text = update.message.text
 logger.info(f" Mensaje recibido de {user.username}: {text}")
 
 await update.message.reply_text(f"Recibí tu mensaje: {text}")


async def main():
 """Función principal"""
 settings = get_settings()
 
 if not settings.telegram_bot_token:
 logger.error(" TELEGRAM_BOT_TOKEN no configurada")
 return
 
 logger.info(" Iniciando bot de prueba...")
 logger.info(f"Token: {settings.telegram_bot_token[:20]}...")
 
 # Crear aplicación
 app = Application.builder().token(settings.telegram_bot_token).build()
 
 # Agregar handlers
 app.add_handler(CommandHandler("start", start_command))
 app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))
 
 # Iniciar bot
 logger.info(" Bot iniciado - Esperando mensajes...")
 logger.info("Envía /start al bot en Telegram")
 logger.info("Presiona Ctrl+C para detener")
 
 # Iniciar polling
 await app.initialize()
 await app.start()
 await app.updater.start_polling(
 allowed_updates=Update.ALL_TYPES,
 drop_pending_updates=True # Ignorar mensajes antiguos
 )
 
 # Mantener corriendo
 try:
 while True:
 await asyncio.sleep(1)
 except KeyboardInterrupt:
 logger.info("\n Deteniendo bot...")
 finally:
 await app.updater.stop()
 await app.stop()
 await app.shutdown()
 logger.info(" Bot detenido")


if __name__ == "__main__":
 asyncio.run(main())
