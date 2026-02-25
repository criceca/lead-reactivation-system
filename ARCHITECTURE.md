# Arquitectura del Sistema de Reactivación de Leads

## Visión General

El Sistema de Reactivación de Leads es una aplicación de inteligencia artificial diseñada para automatizar el proceso de reactivación de clientes perdidos o enfriados. Utiliza un agente LangChain como núcleo central que orquesta conversaciones inteligentes, análisis de leads y escalado a negociadores humanos cuando sea necesario.

## Stack Tecnológico

### Backend
- **Framework API**: FastAPI (Python)
- **ORM**: SQLAlchemy
- **Base de Datos**: MySQL/TiDB
- **IA/ML**: LangChain + OpenAI GPT-4

### Frontend
- **Framework UI**: Streamlit (Python)

## Componentes Principales

### 1. Agente LangChain Central
El corazón del sistema que mantiene conversaciones contextuales con leads, analiza respuestas y determina cuándo escalar casos.

### 2. Tools de LangChain
Herramientas que el agente utiliza: query_crm, send_contact_email, capture_requirement, escalate_case, analyze_lead_history, update_lead_status.

### 3. API FastAPI
Interfaz REST que expone funcionalidades del sistema con endpoints para leads, conversaciones, requerimientos, escalaciones y estadísticas.

### 4. Base de Datos
Esquema relacional con 8 tablas: leads, conversations, messages, requirements, escalations, audit_logs, users.

### 5. Frontend Streamlit
Interfaz de usuario con 5 páginas: Dashboard, Gestionar Leads, Conversaciones, Escalaciones, Análisis.

## Flujo de Reactivación

1. Usuario selecciona Lead en Streamlit
2. Streamlit llama POST /api/leads/{id}/reactivate
3. FastAPI crea Conversation y obtiene Agent
4. Agent genera mensaje inicial usando tools
5. Respuesta se guarda en BD
6. Usuario envía respuesta del Lead
7. Agent analiza mensaje y crea Requirements si es necesario
8. Se escala si es necesario
9. Ciclo se repite hasta resolución o escalación

## Patrones de Diseño

- **Singleton Pattern**: Agente LangChain reutilizable
- **Dependency Injection**: FastAPI con sesiones de BD
- **CRUD Repository Pattern**: Operaciones centralizadas en crud.py
- **Schema Validation**: Pydantic para validación

## Seguridad

- Validación de entrada con Pydantic
- Credenciales en variables de entorno
- HTTPS en producción
- Audit logs para todas las acciones

## Escalabilidad

- FastAPI stateless para múltiples workers
- Base de datos centralizada
- Connection pooling
- Logging estructurado
