#!/bin/bash

# Script rápido para probar el bot de Telegram

echo "=================================================="
echo "🧪 Prueba Rápida del Bot de Telegram"
echo "=================================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Pedir username de Telegram
echo -e "${YELLOW}¿Cuál es tu username de Telegram?${NC}"
echo "(Sin el @, por ejemplo: juanperez)"
read -p "Username: " TELEGRAM_USERNAME

if [ -z "$TELEGRAM_USERNAME" ]; then
    echo "❌ Username no puede estar vacío"
    exit 1
fi

echo ""
echo "=================================================="
echo "📝 Paso 1: Creando/Actualizando Lead"
echo "=================================================="
echo ""

# Verificar que la API esté corriendo
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ La API no está corriendo"
    echo "Por favor, inicia la API primero:"
    echo "  python3 run_api.py"
    exit 1
fi

# Crear o actualizar lead
echo "Creando lead con username: @$TELEGRAM_USERNAME"

LEAD_RESPONSE=$(curl -s -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Test User\",
    \"email\": \"test_$TELEGRAM_USERNAME@example.com\",
    \"phone\": \"@$TELEGRAM_USERNAME\",
    \"company\": \"Test Company\",
    \"status\": \"cold\",
    \"value\": 10000,
    \"preferred_channel\": \"telegram\",
    \"notes\": \"Lead de prueba para verificar bot\"
  }")

LEAD_ID=$(echo "$LEAD_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

if [ -z "$LEAD_ID" ]; then
    echo "⚠️  No se pudo crear lead nuevo, intentando actualizar lead existente..."
    # Obtener primer lead y actualizarlo
    LEAD_ID=1
    curl -s -X PUT http://localhost:8000/api/leads/$LEAD_ID \
      -H "Content-Type: application/json" \
      -d "{\"phone\": \"@$TELEGRAM_USERNAME\"}" > /dev/null
fi

echo -e "${GREEN}✅ Lead configurado con ID: $LEAD_ID${NC}"
echo -e "${GREEN}✅ Username: @$TELEGRAM_USERNAME${NC}"
echo ""

echo "=================================================="
echo "🤖 Paso 2: Iniciando Bot"
echo "=================================================="
echo ""

# Detener bots existentes
pkill -9 -f "run_telegram_bot.py" 2>/dev/null
pkill -9 -f "start_with_telegram.sh" 2>/dev/null
sleep 2

# Activar ambiente virtual
source .venv/bin/activate

# Limpiar estado del bot
echo "🧹 Limpiando estado del bot..."
python3 fix_telegram_bot.py > /dev/null 2>&1
echo ""

# Iniciar bot en background
echo "🚀 Iniciando bot en background..."
nohup python3 run_telegram_bot.py > telegram_bot.log 2>&1 &
BOT_PID=$!

sleep 3

# Verificar que el bot esté corriendo
if ps -p $BOT_PID > /dev/null; then
    echo -e "${GREEN}✅ Bot iniciado (PID: $BOT_PID)${NC}"
else
    echo "❌ Error al iniciar bot"
    cat telegram_bot.log
    exit 1
fi

echo ""
echo "=================================================="
echo "📱 Paso 3: Probar en Telegram"
echo "=================================================="
echo ""
echo -e "${YELLOW}Ahora haz lo siguiente:${NC}"
echo ""
echo "1. Abre Telegram en tu teléfono"
echo "2. Busca: @IgniteLeadsbot"
echo "3. Envía: /start"
echo ""
echo "El bot debe:"
echo "  ✅ Identificarte como 'Test User'"
echo "  ✅ Cambiar tu estado de 'cold' a 'warm'"
echo "  ✅ Iniciar la conversación de reactivación"
echo ""
echo "=================================================="
echo "📋 Ver Logs del Bot"
echo "=================================================="
echo ""
echo "Para ver los logs en tiempo real:"
echo "  tail -f telegram_bot.log"
echo ""
echo "Para detener el bot:"
echo "  kill $BOT_PID"
echo ""
echo "=================================================="
echo ""

# Mostrar logs en tiempo real
echo "Mostrando logs (Ctrl+C para salir)..."
echo ""
tail -f telegram_bot.log
