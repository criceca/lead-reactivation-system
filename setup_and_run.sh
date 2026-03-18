#!/bin/bash

# Script completo para configurar y ejecutar el sistema

echo "=================================================="
echo "🚀 Setup Completo - Sistema de Reactivación de Leads"
echo "=================================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para verificar comando
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅ $1 instalado${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 no encontrado${NC}"
        return 1
    fi
}

# Paso 1: Verificar requisitos
echo "📋 Paso 1: Verificando Requisitos"
echo "---------------------------------------------------"
check_command python3
check_command curl
echo ""

# Paso 2: Verificar ambiente virtual
echo "📦 Paso 2: Verificando Ambiente Virtual"
echo "---------------------------------------------------"
if [ -d ".venv" ]; then
    echo -e "${GREEN}✅ Ambiente virtual existe${NC}"
else
    echo -e "${RED}❌ Ambiente virtual no existe${NC}"
    echo "Creando ambiente virtual..."
    python3 -m venv .venv
fi

# Activar ambiente virtual
source .venv/bin/activate
echo -e "${GREEN}✅ Ambiente virtual activado${NC}"
echo ""

# Paso 3: Verificar .env
echo "⚙️  Paso 3: Verificando Configuración"
echo "---------------------------------------------------"
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ Archivo .env existe${NC}"
    
    # Verificar que al menos un LLM esté configurado
    if grep -q "USE_OPENROUTER=True" .env || \
       grep -q "USE_OPENAI=True" .env || \
       grep -q "USE_DEEPSEEK=True" .env || \
       grep -q "USE_BEDROCK=True" .env; then
        echo -e "${GREEN}✅ Proveedor LLM configurado${NC}"
    else
        echo -e "${YELLOW}⚠️  Ningún proveedor LLM activado${NC}"
        echo "Por favor, edita .env y activa un proveedor"
        exit 1
    fi
    
    # Verificar Telegram
    if grep -q "TELEGRAM_BOT_TOKEN=.*[a-zA-Z0-9]" .env; then
        echo -e "${GREEN}✅ Token de Telegram configurado${NC}"
    else
        echo -e "${YELLOW}⚠️  Token de Telegram no configurado${NC}"
        echo "El bot de Telegram no funcionará sin token"
    fi
else
    echo -e "${RED}❌ Archivo .env no existe${NC}"
    echo "Copiando .env.example a .env..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Por favor, edita .env con tus credenciales${NC}"
    exit 1
fi
echo ""

# Paso 4: Inicializar base de datos
echo "🗄️  Paso 4: Inicializando Base de Datos"
echo "---------------------------------------------------"
if [ -f "lead_reactivation.db" ]; then
    echo -e "${YELLOW}⚠️  Base de datos ya existe${NC}"
    read -p "¿Deseas recrearla? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        rm lead_reactivation.db
        python -c "from app.database.db import init_db; init_db()"
        echo -e "${GREEN}✅ Base de datos recreada${NC}"
    else
        echo -e "${BLUE}ℹ️  Usando base de datos existente${NC}"
    fi
else
    python -c "from app.database.db import init_db; init_db()"
    echo -e "${GREEN}✅ Base de datos creada${NC}"
fi
echo ""

# Paso 5: Iniciar servicios
echo "🚀 Paso 5: Iniciando Servicios"
echo "---------------------------------------------------"
echo "Iniciando API, Bot de Telegram y Streamlit..."
echo ""

# Dar permisos de ejecución
chmod +x start_with_telegram.sh
chmod +x create_demo_leads.sh

# Iniciar servicios en background
./start_with_telegram.sh &
SERVICES_PID=$!

# Esperar a que la API esté lista
echo "⏳ Esperando a que la API esté lista..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API lista!${NC}"
        break
    fi
    sleep 1
    echo -n "."
done
echo ""

# Paso 6: Crear leads ficticios
echo ""
echo "🎭 Paso 6: ¿Deseas crear leads ficticios para pruebas?"
echo "---------------------------------------------------"
read -p "Crear leads de demostración? (S/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    sleep 2  # Esperar un poco más para asegurar que todo esté listo
    ./create_demo_leads.sh
fi

echo ""
echo "=================================================="
echo "✅ Sistema Completamente Configurado y Corriendo"
echo "=================================================="
echo ""
echo "🌐 URLs Disponibles:"
echo "---------------------------------------------------"
echo "  • Streamlit UI:  http://localhost:8501"
echo "  • API Docs:      http://localhost:8000/docs"
echo "  • API Health:    http://localhost:8000/health"
echo ""
echo "📱 Bot de Telegram:"
echo "---------------------------------------------------"
echo "  • Busca tu bot en Telegram"
echo "  • Envía: /start"
echo "  • El bot te responderá automáticamente"
echo ""
echo "🎯 Próximos Pasos:"
echo "---------------------------------------------------"
echo "  1. Abre Streamlit: http://localhost:8501"
echo "  2. Ve al Dashboard para ver los leads"
echo "  3. Abre Telegram y envía /start a tu bot"
echo "  4. Monitorea las conversaciones en Streamlit"
echo ""
echo "📚 Documentación:"
echo "---------------------------------------------------"
echo "  • Guía Rápida:        GUIA_RAPIDA.md"
echo "  • Flujo Telegram:     TELEGRAM_FLUJO_COMPLETO.md"
echo "  • Ejemplo Visual:     EJEMPLO_TELEGRAM_VISUAL.md"
echo ""
echo "🛑 Para detener el sistema:"
echo "---------------------------------------------------"
echo "  Presiona Ctrl+C"
echo ""
echo "=================================================="
echo ""

# Mantener el script corriendo
wait $SERVICES_PID
