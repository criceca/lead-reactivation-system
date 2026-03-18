#!/bin/bash

echo "🚀 Iniciando Sistema de Reactivación de Leads"
echo "=============================================="
echo ""

# Activar ambiente virtual
echo "1️⃣ Activando ambiente virtual..."
source .venv/bin/activate

# Verificar que la base de datos existe
if [ ! -f "lead_reactivation.db" ]; then
    echo "2️⃣ Inicializando base de datos..."
    python -c "from app.database.db import init_db; init_db()"
    echo "   ✅ Base de datos creada"
else
    echo "2️⃣ Base de datos ya existe ✅"
fi

echo ""
echo "3️⃣ Iniciando API en puerto 8000..."
python run_api.py &
API_PID=$!
echo "   API PID: $API_PID"

# Esperar a que la API esté lista
echo ""
echo "4️⃣ Esperando a que la API esté lista..."
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ✅ API lista!"
        break
    fi
    echo "   Esperando... ($i/10)"
    sleep 2
done

# Verificar si la API está corriendo
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo ""
    echo "5️⃣ Iniciando Streamlit en puerto 8501..."
    echo ""
    echo "=============================================="
    echo "✅ Sistema iniciado correctamente"
    echo ""
    echo "URLs disponibles:"
    echo "  - API Docs:  http://localhost:8000/docs"
    echo "  - Streamlit: http://localhost:8501"
    echo ""
    echo "Presiona Ctrl+C para detener todo"
    echo "=============================================="
    echo ""
    
    streamlit run streamlit_app.py
    
    # Cuando Streamlit se cierra, matar la API
    echo ""
    echo "🛑 Deteniendo API..."
    kill $API_PID
    echo "✅ Sistema detenido"
else
    echo ""
    echo "❌ Error: La API no pudo iniciarse"
    echo "   Verifica los logs arriba para más detalles"
    kill $API_PID 2>/dev/null
    exit 1
fi
