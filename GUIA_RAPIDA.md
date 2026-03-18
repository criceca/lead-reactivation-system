# 🚀 Guía Rápida - Sistema de Reactivación de Leads

## ✅ Estado: FUNCIONANDO

Sistema completamente operativo para reactivar leads fríos automáticamente por Telegram.

---

## ⚡ Inicio Ultra Rápido (2 minutos)

```bash
./quick_test_telegram.sh
```

Este script hace TODO automáticamente:
1. Te pide tu username de Telegram
2. Crea/actualiza un lead con tu username
3. Limpia el estado del bot
4. Inicia el bot con logging
5. Muestra logs en tiempo real

Luego:
1. Abre Telegram
2. Busca: @IgniteLeadsbot
3. Envía: `/start`
4. ¡El bot te identificará y comenzará la conversación!

---

## 📋 Inicio Manual Paso a Paso

### Paso 1: Activar Ambiente Virtual
```bash
source .venv/bin/activate
```

### Paso 2: Configurar LLM (elige UNO)

Edita `.env`:
```bash
nano .env
```

**Opción A: OpenRouter (Recomendado - Modelos Gratis)**
```bash
USE_OPENROUTER=True
OPENROUTER_API_KEY=sk-or-v1-tu-key-aqui
OPENROUTER_MODEL=qwen/qwen-2.5-72b-instruct

# Desactivar otros
USE_OPENAI=False
USE_DEEPSEEK=False
USE_BEDROCK=False
```

**Opción B: OpenAI**
```bash
USE_OPENAI=True
OPENAI_API_KEY=sk-tu-key-aqui
LLM_MODEL=gpt-4

# Desactivar otros
USE_OPENROUTER=False
USE_DEEPSEEK=False
USE_BEDROCK=False
```

**Opción C: DeepSeek (Muy Barato)**
```bash
USE_DEEPSEEK=True
DEEPSEEK_API_KEY=sk-tu-key-aqui
DEEPSEEK_MODEL=deepseek-chat

# Desactivar otros
USE_OPENROUTER=False
USE_OPENAI=False
USE_BEDROCK=False
```

**Opción D: AWS Bedrock**
```bash
USE_BEDROCK=True
AWS_ACCESS_KEY_ID=tu-access-key
AWS_SECRET_ACCESS_KEY=tu-secret-key
BEDROCK_MODEL=anthropic.claude-3-5-sonnet-20240620-v1:0

# Desactivar otros
USE_OPENROUTER=False
USE_OPENAI=False
USE_DEEPSEEK=False
```

### Paso 3: Configurar Telegram Bot

En `.env`:
```bash
TELEGRAM_BOT_TOKEN=tu-token-aqui
TELEGRAM_ADMIN_CHAT_ID=tu-chat-id
```

**¿Cómo obtener el token?**
1. Abre Telegram
2. Busca: @BotFather
3. Envía: `/newbot`
4. Sigue las instrucciones
5. Copia el token

**¿Cómo obtener tu Chat ID?**
1. Busca: @userinfobot
2. Envía: `/start`
3. Copia tu ID

### Paso 4: Inicializar Base de Datos

```bash
python -c "from app.database.db import init_db; init_db()"
```

### Paso 5: Iniciar el Sistema

**Opción 1: Todo en uno (Recomendado)**
```bash
./start_with_telegram.sh
```

Inicia:
- ✅ API en http://localhost:8000
- ✅ Bot de Telegram
- ✅ Streamlit en http://localhost:8501

**Opción 2: Solo el bot**
```bash
./restart_telegram_bot.sh
```

### Paso 6: Crear Lead con Tu Username

```bash
curl -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tu Nombre",
    "email": "tu@example.com",
    "phone": "@tu_username_telegram",
    "company": "Tu Empresa",
    "status": "cold",
    "value": 10000,
    "preferred_channel": "telegram",
    "notes": "Lead de prueba"
  }'
```

**Importante:** Reemplaza `@tu_username_telegram` con TU username real de Telegram.

### Paso 7: Probar en Telegram

1. Abre Telegram
2. Busca: @IgniteLeadsbot (o tu bot)
3. Envía: `/start`

El bot automáticamente:
- ✅ Te identifica como el lead
- ✅ Cambia tu estado de `cold` a `warm`
- ✅ Inicia la conversación de reactivación

### Paso 8: Monitorear en Streamlit

1. Abre: http://localhost:8501
2. Ve a "💬 Conversaciones"
3. Ve el historial completo en tiempo real

---

## 🌐 URLs del Sistema

- **Streamlit UI:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs
- **API Health:** http://localhost:8000/health
- **Telegram Bot:** @IgniteLeadsbot

---

## 🎯 Flujo Completo de Uso

### 1. Crear Lead Frío

```bash
curl -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Carlos López",
    "email": "carlos@example.com",
    "phone": "@carloslopez",
    "company": "Software Inc",
    "status": "cold",
    "value": 15000,
    "preferred_channel": "telegram",
    "notes": "Interesado en CRM, perdió contacto hace 3 meses"
  }'
```

### 2. Lead Envía /start

El lead abre Telegram y envía `/start` al bot.

### 3. Sistema Reactiva Automáticamente

```
Bot identifica: @carloslopez
Estado: cold → warm
Conversación: Creada
Agente: Inicia negociación
```

### 4. Conversación

```
Lead: Sí, necesito un CRM para 500 clientes

Agente: Entiendo perfectamente, 500 clientes es un volumen 
considerable. ¿Qué es lo que más te complica actualmente?

Lead: Principalmente el seguimiento

Agente: Perfecto, eso es algo que nuestro CRM maneja muy bien...
```

### 5. Resultado

```
Requerimientos: Capturados automáticamente
Estado: warm → hot (si es necesario)
Escalación: Creada (si es necesario)
Tiempo: ~5 minutos
Intervención manual: 0%
```

---

## 📊 Crear Leads Ficticios

```bash
./create_demo_leads.sh
```

Esto crea 5 leads:
1. **Carlos López** - Frío, Telegram, $15k
2. **María García** - Frío, Telegram, $8k
3. **Juan Pérez** - Tibio, Email, $12k
4. **Ana Martínez** - Caliente, Telegram, $25k
5. **Roberto Silva** - Frío, Telegram, $18k

---

## 🔧 Comandos Útiles

### Gestión del Bot

```bash
# Iniciar bot (recomendado)
./restart_telegram_bot.sh

# Prueba rápida completa
./quick_test_telegram.sh

# Ver logs en tiempo real
tail -f telegram_bot.log

# Detener bot
pkill -f "run_telegram_bot"

# Limpiar estado del bot
python3 fix_telegram_bot.py

# Verificar conexión
python3 test_telegram_bot.py
```

### Gestión de Leads

```bash
# Ver todos los leads
curl http://localhost:8000/api/leads

# Ver leads fríos
curl http://localhost:8000/api/leads?status=cold

# Actualizar lead con tu username
curl -X PUT http://localhost:8000/api/leads/1 \
  -H "Content-Type: application/json" \
  -d '{"phone": "@tu_username"}'

# Reactivar lead
curl -X POST http://localhost:8000/api/leads/1/reactivate

# Ver estadísticas
curl http://localhost:8000/api/dashboard/stats
```

### Gestión del Sistema

```bash
# Iniciar todo
./start_with_telegram.sh

# Iniciar solo API
python3 run_api.py

# Iniciar solo Streamlit
streamlit run streamlit_app.py

# Ver procesos corriendo
ps aux | grep -E "uvicorn|streamlit|telegram"

# Detener todo
pkill -f "uvicorn"
pkill -f "streamlit"
pkill -f "run_telegram_bot"
```

---

## 🔍 Verificar que Todo Funciona

### 1. Health Check
```bash
curl http://localhost:8000/health
```

Respuesta esperada:
```json
{"status": "healthy", "version": "2.0.0"}
```

### 2. Verificar Bot
```bash
python3 test_telegram_bot.py
```

Debe mostrar:
```
✅ Conexión exitosa!
📋 Información del Bot:
  • Username: @IgniteLeadsbot
```

### 3. Verificar LLM
```bash
python3 test_llm_config.py
```

Debe mostrar:
```
✅ Proveedor LLM inicializado correctamente:
  Provider: openrouter
  Model: qwen/qwen-2.5-72b-instruct
```

### 4. Verificar Streamlit

Abre: http://localhost:8501

Debe mostrar:
- 📊 Dashboard con métricas
- 👥 Gestionar Leads
- 💬 Conversaciones
- ⚠️ Escalaciones

---

## 🚨 Solución de Problemas

### Bot no responde

**Causa:** Múltiples instancias corriendo

**Solución:**
```bash
# Detener todas las instancias
pkill -9 -f "run_telegram_bot"
pkill -9 -f "start_with_telegram"

# Limpiar estado
python3 fix_telegram_bot.py

# Reiniciar
./restart_telegram_bot.sh
```

### Bot no identifica al lead

**Causa:** Username no coincide

**Solución:**
```bash
# Verificar lead
curl http://localhost:8000/api/leads/1

# Actualizar con tu username
curl -X PUT http://localhost:8000/api/leads/1 \
  -H "Content-Type: application/json" \
  -d '{"phone": "@tu_username"}'
```

### Error de LLM

**Causa:** Proveedor no configurado

**Solución:**
```bash
# Verificar configuración
cat .env | grep -E "USE_|API_KEY"

# Debe haber al menos uno en True
# Verificar que la API key sea válida
```

### Puerto 8000 en uso

```bash
# Encontrar proceso
lsof -i :8000

# Matar proceso
kill -9 <PID>
```

### Base de datos no existe

```bash
python -c "from app.database.db import init_db; init_db()"
```

---

## 📱 Comandos del Bot en Telegram

- `/start` - Iniciar conversación
- `/help` - Ver ayuda
- `/escalate` - Solicitar hablar con un humano

---

## 📊 Monitoreo en Streamlit

### Dashboard
- 🧊 Leads Fríos
- 🌡️ Leads Tibios
- 🔥 Leads Calientes
- 💬 Conversaciones Activas
- ⚠️ Escalaciones Pendientes

### Conversaciones
- Ver historial completo
- Chat UI con avatares (🤖 Agente, 👤 Lead)
- Requerimientos capturados
- Estado de escalación

### Escalaciones
- Filtrar por estado
- Ver detalles completos
- Asignar a negociadores

---

## 🎓 Mejores Prácticas

### Formato del Teléfono
```json
{
  "phone": "@username"  // ✅ Correcto
}
```

No uses:
```json
{
  "phone": "username"      // ❌ Sin @
  "phone": "+573001234"    // ❌ Número telefónico
}
```

### Estados de Lead
- `cold` - Lead frío, sin contacto reciente
- `warm` - Lead tibio, en conversación
- `hot` - Lead caliente, listo para cerrar
- `reactivated` - Lead reactivado exitosamente

### Canales Soportados
- `telegram` - Requiere teléfono con @username
- `email` - No requiere teléfono
- `api` - No requiere teléfono
- `whatsapp` - Requiere teléfono (futuro)

---

## 📚 Documentación Adicional

- **Sistema Funcionando:** `SISTEMA_FUNCIONANDO.md`
- **Resumen Implementación:** `RESUMEN_IMPLEMENTACION.md`
- **Flujo Telegram Completo:** `TELEGRAM_FLUJO_COMPLETO.md`
- **Ejemplo Visual:** `EJEMPLO_TELEGRAM_VISUAL.md`
- **Troubleshooting:** `TROUBLESHOOTING_TELEGRAM.md`
- **Inicio Rápido (5 min):** `INICIO_RAPIDO.md`
- **README Principal:** `README.md`

---

## 🎉 ¡Listo para Usar!

Tu sistema está completamente funcional. Ahora puedes:

1. ✅ Crear leads fríos con username de Telegram
2. ✅ Leads envían /start al bot
3. ✅ Bot identifica y reactiva automáticamente
4. ✅ Agente negocia y extrae requerimientos
5. ✅ Sistema escala cuando es necesario
6. ✅ Todo visible en Streamlit en tiempo real

**¡El sistema funciona 100% automático una vez que el lead envía /start!**

---

## 🚀 Próximos Pasos

1. Crea leads reales con usernames de tus clientes
2. Personaliza el agente editando `app/agent/agent.py`
3. Agrega más tools en `app/tools/crm_tools.py`
4. Configura notificaciones para escalaciones
5. Integra con tu CRM real

---

*Última actualización: 2024*
*Estado: FUNCIONANDO ✅*
