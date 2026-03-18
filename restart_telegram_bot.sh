#!/bin/bash

# Script para reiniciar el bot de Telegram con logging detallado

echo "🔄 Reiniciando Bot de Telegram con Logging Detallado"
echo "=================================================="
echo ""

# Detener TODAS las instancias del bot
echo "🛑 Deteniendo todas las instancias del bot..."
pkill -9 -f "run_telegram_bot.py"
pkill -9 -f "start_with_telegram.sh"
sleep 2

# Verificar que no haya instancias corriendo
if ps aux | grep -E "run_telegram_bot" | grep -v grep > /dev/null; then
    echo "❌ Error: Aún hay instancias del bot corriendo"
    echo "Por favor, cierra manualmente:"
    ps aux | grep -E "run_telegram_bot" | grep -v grep
    exit 1
fi

echo "✅ Todas las instancias detenidas"
echo ""

# Activar ambiente virtual
echo "📦 Activando ambiente virtual..."
source .venv/bin/activate

# Limpiar estado del bot
echo "🧹 Limpiando estado del bot..."
python3 fix_telegram_bot.py
echo ""

# Iniciar bot con logging detallado
echo "🚀 Iniciando bot..."
echo ""
echo "=================================================="
echo "📋 LOGS DEL BOT (Ctrl+C para detener)"
echo "=================================================="
echo ""

python3 run_telegram_bot.py
