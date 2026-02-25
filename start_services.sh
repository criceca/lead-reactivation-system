#!/bin/bash

# Script para iniciar todos los servicios del sistema de reactivación de leads

set -e

echo "=========================================="
echo "Sistema de Reactivación de Leads"
echo "=========================================="
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "run_api.py" ]; then
    echo "Error: Este script debe ejecutarse desde el directorio raíz del proyecto"
    exit 1
fi

# Crear directorios necesarios
mkdir -p logs
mkdir -p data

echo "✓ Directorios creados"
echo ""

# Verificar variables de entorno
echo "Verificando variables de entorno..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY no está configurada"
fi

if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  DATABASE_URL no está configurada"
fi

echo ""
echo "=========================================="
echo "Iniciando servicios..."
echo "=========================================="
echo ""

# Inicializar base de datos
echo "Inicializando base de datos..."
python3 -c "from app.database.db import init_db; init_db()" || echo "Base de datos ya inicializada"

echo ""

# Iniciar FastAPI en background
echo "Iniciando FastAPI Server en puerto 8000..."
python3 run_api.py > logs/fastapi.log 2>&1 &
FASTAPI_PID=$!
echo "✓ FastAPI iniciado (PID: $FASTAPI_PID)"

# Esperar a que FastAPI esté listo
sleep 3

# Iniciar Streamlit en background
echo "Iniciando Streamlit en puerto 8501..."
streamlit run streamlit_app.py --server.port=8501 --logger.level=info > logs/streamlit.log 2>&1 &
STREAMLIT_PID=$!
echo "✓ Streamlit iniciado (PID: $STREAMLIT_PID)"

echo ""
echo "=========================================="
echo "Servicios iniciados correctamente"
echo "=========================================="
echo ""
echo "URLs de acceso:"
echo "  - API FastAPI: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Streamlit: http://localhost:8501"
echo ""
echo "Logs:"
echo "  - FastAPI: logs/fastapi.log"
echo "  - Streamlit: logs/streamlit.log"
echo ""
echo "Para detener los servicios, ejecuta:"
echo "  kill $FASTAPI_PID $STREAMLIT_PID"
echo ""

# Mantener el script en ejecución
wait
