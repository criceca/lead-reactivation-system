#!/usr/bin/env python3
"""
Script para iniciar el bot de Telegram
"""

import asyncio
import logging
import signal
import sys
from app.telegram.telegram_handler import ImprovedTelegramHandler
from app.config import get_settings

# Configurar logging
logging.basicConfig(
 level=logging.INFO,
 format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Variable global para el handler
telegram_handler = None


async def main():
 """Función principal"""
 global telegram_handler
 
 settings = get_settings()
 
 # Verificar configuración
 if not settings.telegram_bot_token:
 logger.error(" TELEGRAM_BOT_TOKEN no configurada en .env")
 logger.error("Agrega tu token en .env:")
 logger.error("TELEGRAM_BOT_TOKEN=tu-token-aqui")
 sys.exit(1)
 
 logger.info(" Iniciando bot de Telegram...")
 logger.info(f"Token: {settings.telegram_bot_token[:20]}...")
 
 try:
 # Crear e iniciar handler
 telegram_handler = ImprovedTelegramHandler()
 await telegram_handler.start()
 
 logger.info(" Bot de Telegram corriendo")
 logger.info("Presiona Ctrl+C para detener")
 
 # Mantener el bot corriendo
 while True:
 await asyncio.sleep(1)
 
 except KeyboardInterrupt:
 logger.info("\n Deteniendo bot...")
 except Exception as e:
 logger.error(f" Error: {e}", exc_info=True)
 finally:
 if telegram_handler:
 await telegram_handler.stop()
 logger.info(" Bot detenido")


def signal_handler(sig, frame):
 """Manejar señales de interrupción"""
 logger.info("\n Señal de interrupción recibida")
 sys.exit(0)


if __name__ == "__main__":
 # Registrar manejador de señales
 signal.signal(signal.SIGINT, signal_handler)
 signal.signal(signal.SIGTERM, signal_handler)
 
 # Ejecutar bot
 try:
 asyncio.run(main())
 except KeyboardInterrupt:
 logger.info(" Bot detenido por usuario")
