#!/usr/bin/env python3
"""
Script para limpiar y resetear el bot de Telegram
"""

import asyncio
import logging
from telegram import Bot
from app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fix_bot():
    """Limpiar estado del bot"""
    settings = get_settings()
    
    if not settings.telegram_bot_token:
        logger.error("ERROR: TELEGRAM_BOT_TOKEN no configurada")
        return
    
    print("=" * 60)
    print("Limpiando Estado del Bot de Telegram")
    print("=" * 60)
    print()
    
    bot = Bot(token=settings.telegram_bot_token)
    
    try:
        # 1. Obtener info del bot
        print("Conectando con Telegram...")
        me = await bot.get_me()
        print(f"Bot: @{me.username}")
        print()
        
        # 2. Eliminar webhook si existe
        print("Eliminando webhook...")
        result = await bot.delete_webhook(drop_pending_updates=True)
        if result:
            print("Webhook eliminado")
        else:
            print("No habia webhook configurado")
        print()
        
        # 3. Obtener y limpiar updates pendientes
        print("Obteniendo updates pendientes...")
        updates = await bot.get_updates()
        
        if updates:
            print(f"ADVERTENCIA: Hay {len(updates)} mensajes pendientes")
            print()
            print("Mensajes pendientes:")
            for update in updates:
                if update.message:
                    user = update.message.from_user
                    text = update.message.text
                    print(f" - De @{user.username}: {text}")
            print()
            
            # Limpiar mensajes pendientes
            print("Limpiando mensajes pendientes...")
            last_update_id = updates[-1].update_id
            await bot.get_updates(offset=last_update_id + 1)
            print("Mensajes pendientes limpiados")
        else:
            print("No hay mensajes pendientes")
        print()
        
        # 4. Verificar que todo está limpio
        print("Verificando estado final...")
        updates = await bot.get_updates()
        if not updates:
            print("Estado limpio - Bot listo para recibir mensajes")
        else:
            print(f"ADVERTENCIA: Aun hay {len(updates)} mensajes")
        
        print()
        print("=" * 60)
        print("Bot Limpiado Exitosamente")
        print("=" * 60)
        print()
        print("Proximos pasos:")
        print(" 1. Reinicia el bot: ./restart_telegram_bot.sh")
        print(" 2. Abre Telegram")
        print(f" 3. Busca: @{me.username}")
        print(" 4. Envia: /start")
        print()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(fix_bot())