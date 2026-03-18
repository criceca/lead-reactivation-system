# Sistema de Reactivación de Leads con IA (Python)

Un sistema completo impulsado por inteligencia artificial para reactivar leads perdidos o enfriados mediante conversaciones inteligentes, negociación automatizada y escalado a negociadores humanos cuando sea necesario. **Construido 100% en Python** usando FastAPI, Streamlit, LangChain y SQLAlchemy.

## 🎯 Características Principales

### 1. Agente LangChain Central
- **IA Negociadora**: Conversaciones naturales y contextuales con leads
- **Análisis Inteligente**: Comprende el historial del lead y adapta la estrategia
- **Toma de Decisiones**: Determina cuándo escalar a un negociador humano
- **Generación de Estrategia**: Crea enfoques personalizados para cada lead
- **Múltiples Proveedores LLM**: OpenAI, OpenRouter, DeepSeek, AWS Bedrock

### 2. Tools de LangChain
El agente tiene acceso a las siguientes herramientas:

- **get_lead_info**: Consulta información completa del lead
- **create_conversation**: Inicia nueva conversación con el lead
- **capture_requirement**: Documenta requerimientos mencionados
- **escalate_to_human**: Escala casos complejos a negociadores humanos
- **analyze_sentiment**: Analiza el sentimiento de la conversación

### 3. API REST con FastAPI
Endpoints para:
- Gestión de leads (crear, consultar, actualizar)
- Gestión de conversaciones
- Captura de requerimientos
- Escalación de casos
- Estadísticas y dashboard
- Información del agente
- **Validación de teléfono** para canales Telegram/WhatsApp

### 4. Frontend Interactivo con Streamlit
Interfaz amigable para:
- Dashboard con métricas en tiempo real
- Gestionar leads con filtros y búsqueda
- Chat UI con avatares para conversaciones
- Monitorear casos escalados
- Ver análisis y reportes
- **Validación automática** de teléfono para Telegram

### 5. Integración con Telegram
- **Bot de Telegram** (@IgniteLeadsbot) para comunicación directa
- Comandos: `/start`, `/help`, `/escalate`
- Conversaciones persistentes en base de datos
- Notificaciones automáticas (opcional)

### 6. Base de Datos Completa
Tablas para:
- **leads**: Información de leads del CRM
- **conversations**: Historial de conversaciones
- **messages**: Mensajes individuales
- **requirements**: Requerimientos capturados
- **escalations**: Casos escalados
- **audit_logs**: Registro de auditoría
- **users**: Usuarios del sistema

## 🚀 Instalación Rápida

### Requisitos Previos
- Python 3.11+ (recomendado 3.11.11)
- SQLite (incluido) o MySQL/TiDB (opcional)
- API Key de OpenAI, OpenRouter, DeepSeek o AWS Bedrock
- Git

### Instalación con uv (Recomendado)

1. **Clonar el repositorio**
```bash
git clone <repo-url>
cd lead-reactivation-system
```

2. **Crear entorno virtual con uv**
```bash
uv venv --python 3.11
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
uv pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
# Elige uno de los proveedores LLM:
# - OpenAI: USE_OPENAI=True, OPENAI_API_KEY=sk-...
# - OpenRouter: USE_OPENROUTER=True, OPENROUTER_API_KEY=sk-or-v1-...
# - DeepSeek: USE_DEEPSEEK=True, DEEPSEEK_API_KEY=sk-...
# - AWS Bedrock: USE_BEDROCK=True, AWS_ACCESS_KEY_ID=..., AWS_SECRET_ACCESS_KEY=...
# - Telegram: TELEGRAM_BOT_TOKEN=... (opcional)
```

5. **Inicializar la base de datos**
```bash
python -c "from app.database.db import init_db; init_db()"
```

6. **Iniciar el sistema completo**

**Opción 1: Todo en uno (API + Bot + Streamlit)**
```bash
./start_with_telegram.sh
```

**Opción 2: Sin Telegram (API + Streamlit)**
```bash
./start_all.sh
```

**Opción 3: Servicios individuales**
```bash
# Terminal 1 - API
python run_api.py

# Terminal 2 - Bot de Telegram (opcional)
python run_telegram_bot.py

# Terminal 3 - Streamlit
streamlit run streamlit_app.py
```

### URLs del Sistema
- **API Docs:** http://localhost:8000/docs
- **Streamlit:** http://localhost:8501
- **Telegram Bot:** @IgniteLeadsbot

📖 **Guía completa:** Ver `GUIA_RAPIDA.md` para instrucciones detalladas

## 📊 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                    │
│         (Dashboard, Leads, Chat UI, Escalaciones)        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI REST API                       │
│    (Endpoints + Validaciones + Health Checks)            │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   LangChain  │ │   Telegram   │ │   Database   │
│    Agent     │ │   Bot Handler│ │   (SQLite)   │
│  + 5 Tools   │ │              │ │              │
└──────┬───────┘ └──────────────┘ └──────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│              Proveedores LLM (Unificados)                │
│  OpenAI | OpenRouter | DeepSeek | AWS Bedrock           │
└─────────────────────────────────────────────────────────┘
```

### Componentes Principales

1. **Streamlit Frontend**: Interfaz gráfica con chat UI, filtros, y visualizaciones
2. **FastAPI API**: REST API con validaciones y documentación automática
3. **LangChain Agent**: Agente IA con 5 tools para gestión de leads
4. **Telegram Bot**: Bot para comunicación directa con leads
5. **Database**: SQLite con 7 tablas (leads, conversations, messages, etc.)
6. **LLM Providers**: Arquitectura unificada para múltiples proveedores

## 🔧 Configuración

### Proveedores LLM Soportados

El sistema soporta múltiples proveedores LLM con arquitectura unificada:

#### OpenAI
```env
USE_OPENAI=True
OPENAI_API_KEY=sk-your-key
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7
```

#### OpenRouter (Modelos gratuitos y de pago)
```env
USE_OPENROUTER=True
OPENROUTER_API_KEY=sk-or-v1-your-key
OPENROUTER_MODEL=qwen/qwen-2.5-72b-instruct
OPENROUTER_SITE_URL=http://localhost:8000
OPENROUTER_APP_NAME=Lead Reactivation System
```

Modelos gratuitos populares:
- `qwen/qwen-2.5-72b-instruct` (Gratis, muy bueno)
- `meta-llama/llama-3.1-8b-instruct:free`
- `google/gemini-flash-1.5`

#### DeepSeek
```env
USE_DEEPSEEK=True
DEEPSEEK_API_KEY=sk-your-key
DEEPSEEK_MODEL=deepseek-chat
```

#### AWS Bedrock
```env
USE_BEDROCK=True
BEDROCK_MODEL=anthropic.claude-3-5-sonnet-20240620-v1:0
BEDROCK_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

### Otras Variables de Entorno

```env
# Database (SQLite por defecto)
DATABASE_URL=sqlite:///./lead_reactivation.db
DATABASE_ECHO=False

# Telegram (Opcional)
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ADMIN_CHAT_ID=your-chat-id

# Email (Opcional)
ENABLE_EMAIL_NOTIFICATIONS=False
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Agent
AGENT_TIMEOUT=300
MAX_CONVERSATION_TURNS=20
AGENT_DEBUG=False

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

📖 **Más información:** Ver `PROVEEDORES_LLM.md` para detalles de cada proveedor

## 📖 Uso

### 1. Acceder al Dashboard
```
http://localhost:8501
```

### 2. Crear un Lead

**Desde Streamlit:**
- Ir a "👥 Gestionar Leads" → "Crear Lead"
- Llenar formulario con información del lead
- **Importante:** Si eliges Telegram/WhatsApp, el teléfono es obligatorio
- Guardar

**Desde API:**
```bash
# Lead con Telegram (requiere teléfono)
curl -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Juan Pérez",
    "email": "juan@example.com",
    "phone": "+573001234567",
    "company": "Tech Corp",
    "status": "cold",
    "value": 5000,
    "preferred_channel": "telegram"
  }'

# Lead con email (no requiere teléfono)
curl -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "name": "María García",
    "email": "maria@example.com",
    "company": "Design Studio",
    "status": "warm",
    "value": 7500,
    "preferred_channel": "email"
  }'
```

### 3. Iniciar Reactivación
- Ir a "👥 Gestionar Leads" → "Leads Fríos"
- Hacer clic en "🚀 Reactivar" para un lead
- El agente iniciará automáticamente la conversación

### 4. Monitorear Conversaciones
- Ir a "💬 Conversaciones"
- Ingresar ID de conversación
- Ver historial con avatares (🤖 Agente, 👤 Lead)
- Enviar mensajes y ver respuestas en tiempo real

### 5. Gestionar Escalaciones
- Ir a "⚠️ Escalaciones"
- Ver casos pendientes con filtros
- Asignar a negociador humano

### 6. Usar el Bot de Telegram

**Iniciar el bot:**
```bash
python run_telegram_bot.py
```

**En Telegram:**
1. Buscar: `@IgniteLeadsbot`
2. Enviar: `/start`
3. El bot responderá automáticamente

**Comandos disponibles:**
- `/start` - Iniciar conversación
- `/help` - Ver ayuda
- `/escalate` - Escalar a negociador humano

## 🤖 Cómo Funciona el Agente

### Flujo de Reactivación

1. **Consulta CRM**: El agente obtiene información del lead
2. **Análisis**: Analiza historial y razón de pérdida
3. **Estrategia**: Genera enfoque personalizado
4. **Contacto**: Envía email de contacto inicial
5. **Conversación**: Mantiene conversación natural
6. **Captura**: Documenta requerimientos mencionados
7. **Decisión**: Determina si escalar o continuar
8. **Escalación**: Si es necesario, escala a humano

### Criterios de Escalación

El agente escala automáticamente cuando:
- Los requerimientos son muy complejos
- El lead muestra frustración
- Se requieren decisiones especiales
- El valor del deal es muy alto
- Hay preguntas técnicas específicas

## 📊 API Endpoints

### Leads
- `GET /api/leads?status=cold` - Obtener leads por estado
- `GET /api/leads/{id}` - Obtener lead específico
- `POST /api/leads` - Crear nuevo lead
- `PUT /api/leads/{id}` - Actualizar lead
- `POST /api/leads/{id}/reactivate` - Iniciar reactivación

### Conversaciones
- `GET /api/conversations/{id}` - Obtener conversación
- `POST /api/conversations/{id}/message` - Enviar mensaje

### Requerimientos
- `GET /api/requirements/{conversationId}` - Obtener requerimientos

### Escalaciones
- `GET /api/escalations?status=pending` - Obtener escalaciones

### Dashboard
- `GET /api/dashboard/stats` - Obtener estadísticas
- `GET /api/agent/info` - Información del agente

## 📝 Estructura del Proyecto

```
lead-reactivation-system/
├── app/
│   ├── __init__.py
│   ├── config.py                 # Configuración centralizada
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py            # Modelos SQLAlchemy
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py           # Schemas Pydantic con enums
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db.py                # Configuración DB
│   │   └── crud.py              # CRUD operations
│   ├── agent/
│   │   ├── __init__.py
│   │   └── agent.py             # Agente LangChain
│   ├── tools/
│   │   ├── __init__.py
│   │   └── crm_tools.py         # 5 Tools del agente
│   ├── llm/
│   │   ├── __init__.py
│   │   └── llm_provider.py      # Proveedores LLM unificados
│   ├── telegram/
│   │   ├── __init__.py
│   │   └── telegram_handler.py  # Handler del bot
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py              # API FastAPI
│   └── services/
│       └── __init__.py
├── tests/                        # Tests unitarios
├── logs/                         # Logs de aplicación
├── data/                         # Datos locales
├── .venv/                        # Ambiente virtual
├── requirements.txt              # 122 dependencias
├── run_api.py                    # Script para ejecutar API
├── run_telegram_bot.py          # Script para ejecutar bot
├── streamlit_app.py             # Frontend Streamlit
├── start_all.sh                 # Iniciar API + Streamlit
├── start_with_telegram.sh       # Iniciar todo el sistema
├── test_api_curl.sh             # Tests de API
├── .env                         # Variables de entorno
├── .env.example                 # Ejemplo de configuración
├── GUIA_RAPIDA.md              # Guía de inicio rápido
├── PROVEEDORES_LLM.md          # Guía de proveedores LLM
├── TELEGRAM_BOT_GUIA.md        # Guía del bot
├── README.md                    # Este archivo
└── todo.md                      # Lista de tareas
```

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/health
# Respuesta: {"status":"healthy","version":"2.0.0"}
```

### Pruebas de API

**Crear lead con Telegram (requiere teléfono):**
```bash
curl -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Juan Pérez",
    "email": "juan@example.com",
    "phone": "+573001234567",
    "company": "Tech Corp",
    "status": "cold",
    "value": 5000,
    "preferred_channel": "telegram"
  }'
```

**Crear lead con email (no requiere teléfono):**
```bash
curl -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "name": "María García",
    "email": "maria@example.com",
    "company": "Design Studio",
    "status": "warm",
    "value": 7500,
    "preferred_channel": "email"
  }'
```

**Obtener leads:**
```bash
# Todos los leads
curl http://localhost:8000/api/leads

# Leads fríos
curl http://localhost:8000/api/leads?status=cold

# Lead específico
curl http://localhost:8000/api/leads/1
```

**Iniciar reactivación:**
```bash
curl -X POST http://localhost:8000/api/leads/1/reactivate
```

**Ver estadísticas:**
```bash
curl http://localhost:8000/api/dashboard/stats
```

### Script de Pruebas Automatizadas

```bash
./test_api_curl.sh
```

Esto probará:
- ✅ Crear lead con Telegram y teléfono (debe funcionar)
- ❌ Crear lead con Telegram sin teléfono (debe fallar)
- ✅ Crear lead con email sin teléfono (debe funcionar)
- 📋 Listar todos los leads

### Pruebas del Bot de Telegram

1. Iniciar el bot: `python run_telegram_bot.py`
2. Abrir Telegram y buscar: `@IgniteLeadsbot`
3. Enviar: `/start`
4. Verificar que el bot responde

### Tests Unitarios

```bash
# Ejecutar tests
python test_mejoras.py

# Resultado esperado: 6/6 tests passing
```

## 🐛 Troubleshooting

### El agente no responde
1. Verificar que tienes configurado al menos un proveedor LLM
2. Revisar logs en la terminal
3. Verificar conexión a la base de datos
4. Comprobar que la API key es válida

### Base de datos no conecta
1. Verificar DATABASE_URL en `.env`
2. Para SQLite, verificar que el archivo `.db` existe
3. Ejecutar: `python -c "from app.database.db import init_db; init_db()"`

### Streamlit no carga
1. Verificar que la API FastAPI está corriendo en puerto 8000
2. Ejecutar health check: `curl http://localhost:8000/health`
3. Comprobar logs de Streamlit

### Bot de Telegram no responde
1. **Verificar que el bot está corriendo:** `python run_telegram_bot.py`
2. Verificar TELEGRAM_BOT_TOKEN en `.env`
3. Comprobar que el token es válido (obtener de @BotFather)
4. Ver logs del bot para errores

### Error: "Phone number is required for Telegram channel"
Esto es correcto. Los leads con canal Telegram/WhatsApp DEBEN tener teléfono:
```bash
# ❌ Incorrecto
{"preferred_channel": "telegram"}  # Falta phone

# ✅ Correcto
{"phone": "+573001234567", "preferred_channel": "telegram"}
```

### Puerto 8000 ya en uso
```bash
# Encontrar proceso
lsof -i :8000

# Matar proceso
kill -9 <PID>

# O usar otro puerto
uvicorn app.api.main:app --port 8001
```

### Error con pydantic-core
Usar Python 3.11 para evitar problemas de compatibilidad:
```bash
uv venv --python 3.11
```

📖 **Más ayuda:** Ver `GUIA_RAPIDA.md` sección "Solución de Problemas"

## 📚 Documentación Adicional

- **Guía Rápida:** `GUIA_RAPIDA.md` - Instrucciones completas de instalación y uso
- **Proveedores LLM:** `PROVEEDORES_LLM.md` - Configuración de OpenAI, OpenRouter, DeepSeek, Bedrock
- **Bot de Telegram:** `TELEGRAM_BOT_GUIA.md` - Guía completa del bot
- **Integración Telegram:** `TELEGRAM_INTEGRACION.md` - Cómo funciona la integración
- **Ejemplos API:** `EJEMPLOS_API.md` - Ejemplos de uso de la API
- **Streamlit:** `README_STREAMLIT.md` - Guía de la interfaz gráfica
- **Arquitectura:** `ARCHITECTURE.md` - Arquitectura del sistema
- [LangChain Docs](https://python.langchain.com/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Streamlit Docs](https://docs.streamlit.io/)

## 🤝 Contribuir

Para contribuir al proyecto:
1. Crear una rama feature
2. Hacer commits con mensajes descriptivos
3. Enviar pull request

## 📄 Licencia

MIT License - Ver LICENSE para detalles

## 👥 Soporte

Para soporte o preguntas:
- Email: support@leadreactivation.com
- Issues: GitHub Issues
- Documentación: Wiki

---

**Desarrollado con ❤️ usando LangChain, FastAPI y Streamlit (100% Python)**
