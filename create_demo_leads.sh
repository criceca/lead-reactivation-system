#!/bin/bash

# Script para crear leads ficticios de demostración

echo "=================================================="
echo "🎭 Creando Leads Ficticios para Demostración"
echo "=================================================="
echo ""

API_URL="http://localhost:8000"

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar que la API esté corriendo
echo "🔍 Verificando que la API esté corriendo..."
if ! curl -s $API_URL/health > /dev/null; then
    echo -e "${RED}❌ Error: La API no está corriendo${NC}"
    echo ""
    echo "Por favor, inicia la API primero:"
    echo "  ./start_with_telegram.sh"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ API corriendo${NC}"
echo ""

# Función para crear lead
create_lead() {
    local name=$1
    local email=$2
    local phone=$3
    local company=$4
    local status=$5
    local value=$6
    local channel=$7
    local notes=$8
    
    echo -e "${BLUE}📝 Creando lead: $name${NC}"
    
    RESPONSE=$(curl -s -X POST $API_URL/api/leads \
      -H "Content-Type: application/json" \
      -d "{
        \"name\": \"$name\",
        \"email\": \"$email\",
        \"phone\": \"$phone\",
        \"company\": \"$company\",
        \"status\": \"$status\",
        \"value\": $value,
        \"preferred_channel\": \"$channel\",
        \"notes\": \"$notes\"
      }")
    
    LEAD_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', 'error'))" 2>/dev/null)
    
    if [ "$LEAD_ID" != "error" ] && [ ! -z "$LEAD_ID" ]; then
        echo -e "${GREEN}   ✅ Lead creado con ID: $LEAD_ID${NC}"
        return 0
    else
        echo -e "${RED}   ❌ Error al crear lead${NC}"
        echo "   Respuesta: $RESPONSE"
        return 1
    fi
}

echo "=================================================="
echo "Creando 5 leads ficticios..."
echo "=================================================="
echo ""

# Lead 1: Frío - Telegram
create_lead \
    "Carlos López" \
    "carlos.lopez@example.com" \
    "@carloslopez" \
    "Software Inc" \
    "cold" \
    15000 \
    "telegram" \
    "Interesado en CRM para 500 clientes, perdió contacto hace 3 meses"

echo ""

# Lead 2: Frío - Telegram
create_lead \
    "María García" \
    "maria.garcia@example.com" \
    "@mariagarcia" \
    "Design Studio" \
    "cold" \
    8000 \
    "telegram" \
    "Interesada en automatización de marketing, presupuesto limitado"

echo ""

# Lead 3: Tibio - Email
create_lead \
    "Juan Pérez" \
    "juan.perez@example.com" \
    "" \
    "Tech Corp" \
    "warm" \
    12000 \
    "email" \
    "En proceso de evaluación, necesita demo"

echo ""

# Lead 4: Caliente - Telegram
create_lead \
    "Ana Martínez" \
    "ana.martinez@example.com" \
    "@anamartinez" \
    "Consulting Group" \
    "hot" \
    25000 \
    "telegram" \
    "Lista para cerrar, solo necesita cotización final"

echo ""

# Lead 5: Frío - Telegram
create_lead \
    "Roberto Silva" \
    "roberto.silva@example.com" \
    "@robertosilva" \
    "E-commerce Plus" \
    "cold" \
    18000 \
    "telegram" \
    "Perdió contacto hace 6 meses, interesado en integración con Shopify"

echo ""
echo "=================================================="
echo "✅ Leads Ficticios Creados"
echo "=================================================="
echo ""

# Obtener estadísticas
echo "📊 Estadísticas del Sistema:"
echo "---------------------------------------------------"
STATS=$(curl -s $API_URL/api/dashboard/stats)
echo "$STATS" | python3 -m json.tool

echo ""
echo "=================================================="
echo "🎯 Próximos Pasos"
echo "=================================================="
echo ""
echo -e "${YELLOW}Para probar el flujo de reactivación:${NC}"
echo ""
echo "1. Abre Streamlit: http://localhost:8501"
echo "   - Ve al Dashboard para ver los leads"
echo "   - Ve a 'Gestionar Leads' para ver detalles"
echo ""
echo "2. Prueba con Telegram:"
echo "   - Abre Telegram en tu teléfono"
echo "   - Busca tu bot (ej: @IgniteLeadsbot)"
echo "   - Envía: /start"
echo "   - El bot te identificará si tu username coincide"
echo ""
echo "3. Monitorea en Streamlit:"
echo "   - Ve a 'Conversaciones' para ver el chat"
echo "   - Ve a 'Escalaciones' si el agente escala"
echo ""
echo -e "${YELLOW}Nota Importante:${NC}"
echo "Los leads tienen usernames ficticios (@carloslopez, etc.)"
echo "Para probar, reemplaza uno con TU username de Telegram:"
echo ""
echo "  curl -X PUT $API_URL/api/leads/1 \\"
echo "    -H \"Content-Type: application/json\" \\"
echo "    -d '{\"phone\": \"@tu_username\"}'"
echo ""
echo "=================================================="
echo ""
