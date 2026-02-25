# Sistema de Reactivación de Leads con IA (Python)

Un sistema completo impulsado por inteligencia artificial para reactivar leads perdidos o enfriados mediante conversaciones inteligentes, negociación automatizada y escalado a negociadores humanos cuando sea necesario. **Construido 100% en Python** usando FastAPI, Streamlit, LangChain y SQLAlchemy.

## 🎯 Características Principales

### 1. Agente LangChain Central
- **IA Negociadora**: Conversaciones naturales y contextuales con leads
- **Análisis Inteligente**: Comprende el historial del lead y adapta la estrategia
- **Toma de Decisiones**: Determina cuándo escalar a un negociador humano
- **Generación de Estrategia**: Crea enfoques personalizados para cada lead

### 2. Tools de LangChain
El agente tiene acceso a las siguientes herramientas:

- **query_crm**: Consulta la base de datos CRM para obtener información del lead
- **send_contact_email**: Envía emails de contacto inicial personalizados
- **capture_requirement**: Documenta requerimientos mencionados durante la conversación
- **escalate_case**: Escala casos complejos a negociadores humanos
- **analyze_lead_history**: Analiza el historial completo del lead
- **update_lead_status**: Actualiza el estado del lead en el CRM

### 3. API REST con FastAPI
Endpoints para:
- Gestión de leads (crear, consultar, actualizar)
- Gestión de conversaciones
- Captura de requerimientos
- Escalación de casos
- Estadísticas y dashboard
- Información del agente

### 4. Frontend Interactivo con Streamlit
Interfaz amigable para:
- Visualizar dashboard con métricas
- Gestionar leads y conversaciones
- Monitorear casos escalados
- Ver análisis y reportes

### 5. Base de Datos Completa
Tablas para:
- **leads**: Información de leads del CRM
- **conversations**: Historial de conversaciones
- **messages**: Mensajes individuales
- **requirements**: Requerimientos capturados
- **escalations**: Casos escalados
- **audit_logs**: Registro de auditoría
- **users**: Usuarios del sistema

## 🚀 Instalación

### Requisitos Previos
- Python 3.11+
- MySQL/TiDB
- OpenAI API Key
- Git

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
cd /home/ubuntu/lead-reactivation-system
```

2. **Crear entorno virtual (opcional pero recomendado)**
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
# OPENAI_API_KEY=sk-...
# DATABASE_URL=mysql+pymysql://user:pass@localhost/lead_reactivation
# SMTP_HOST=smtp.gmail.com
# etc.
```

5. **Inicializar la base de datos**
```bash
python3 -c "from app.database.db import init_db; init_db()"
```

6. **Iniciar los servicios**

**Terminal 1 - API FastAPI:**
```bash
python3 run_api.py
```

**Terminal 2 - Frontend Streamlit:**
```bash
streamlit run streamlit_app.py
```

## 📊 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                    │
│              (Dashboard, Leads, Conversaciones)          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI REST API                       │
│         (Endpoints para gestionar leads y agente)        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              LangChain Agent Central                     │
│            (IA Negociadora + Tools)                      │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   ┌────────┐  ┌──────────┐  ┌──────────┐
   │  CRM   │  │   Email  │  │    S3    │
   │   DB   │  │  Service │  │ Storage  │
   └────────┘  └──────────┘  └──────────┘
```

## 🔧 Configuración

### Variables de Entorno Principales

```env
# LLM Configuration
OPENAI_API_KEY=sk-your-key
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7

# Database
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/lead_reactivation
DATABASE_ECHO=False

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@leadreactivation.com
SALES_TEAM_EMAIL=sales@company.com

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
API_RELOAD=True

# Streamlit
STREAMLIT_PORT=8501

# Agent
AGENT_TIMEOUT=300
MAX_CONVERSATION_TURNS=20

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## 📖 Uso

### 1. Acceder al Dashboard
```
http://localhost:8501
```

### 2. Crear un Lead
- Ir a "Gestionar Leads" → "Crear Lead"
- Llenar formulario con información del lead
- Guardar

### 3. Iniciar Reactivación
- Ir a "Gestionar Leads" → "Leads Fríos"
- Hacer clic en "Reactivar" para un lead
- El agente iniciará automáticamente la conversación

### 4. Monitorear Conversaciones
- Ir a "Conversaciones"
- Ingresar ID de conversación
- Ver historial y enviar mensajes

### 5. Gestionar Escalaciones
- Ir a "Escalaciones"
- Ver casos pendientes
- Asignar a negociador humano

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
│   ├── config.py                 # Configuración
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py            # Modelos SQLAlchemy
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py           # Schemas Pydantic
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db.py                # Configuración DB
│   │   └── crud.py              # CRUD operations
│   ├── agent/
│   │   ├── __init__.py
│   │   └── agent.py             # Agente LangChain
│   ├── tools/
│   │   ├── __init__.py
│   │   └── crm_tools.py         # Tools del agente
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py              # API FastAPI
│   └── services/
│       └── __init__.py
├── tests/                        # Tests unitarios
├── logs/                         # Logs de aplicación
├── data/                         # Datos locales
├── requirements.txt              # Dependencias Python
├── run_api.py                    # Script para ejecutar API
├── streamlit_app.py             # Frontend Streamlit
├── .env.example                 # Variables de entorno
├── README.md                    # Este archivo
└── todo.md                      # Lista de tareas
```

## 🧪 Testing

### Pruebas de API
```bash
# Obtener leads
curl http://localhost:8000/api/leads?status=cold

# Crear lead
curl -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com"}'

# Iniciar reactivación
curl -X POST http://localhost:8000/api/leads/1/reactivate
```

### Health Check
```bash
curl http://localhost:8000/health
```

## 🐛 Troubleshooting

### El agente no responde
1. Verificar que OPENAI_API_KEY está configurada
2. Revisar logs en la terminal
3. Verificar conexión a la base de datos

### Base de datos no conecta
1. Verificar DATABASE_URL
2. Asegurar que MySQL está corriendo
3. Revisar credenciales de acceso

### Streamlit no carga
1. Verificar que la API FastAPI está corriendo
2. Revisar que API_BASE_URL es correcto
3. Comprobar logs de Streamlit

## 📚 Documentación Adicional

- [LangChain Docs](https://python.langchain.com/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)

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
