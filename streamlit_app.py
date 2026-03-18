"""
Frontend Streamlit Mejorado para el Sistema de Reactivación de Leads
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json
import os

# Configuración de la página
st.set_page_config(
 page_title="Sistema de Reactivacion de Leads",
 page_icon="chart_with_upwards_trend",
 layout="wide",
 initial_sidebar_state="expanded"
)

# URL de la API
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Estilos CSS personalizados
st.markdown("""
 <style>
 .main {
 padding: 2rem;
 }
 .metric-card {
 background-color: #f0f2f6;
 padding: 1.5rem;
 border-radius: 0.5rem;
 margin: 0.5rem 0;
 }
 .status-cold {
 color: #2196F3;
 font-weight: bold;
 }
 .status-warm {
 color: #FF9800;
 font-weight: bold;
 }
 .status-hot {
 color: #F44336;
 font-weight: bold;
 }
 .status-reactivated {
 color: #4CAF50;
 font-weight: bold;
 }
 .channel-badge {
 background-color: #E3F2FD;
 padding: 0.25rem 0.5rem;
 border-radius: 0.25rem;
 font-size: 0.85rem;
 }
 </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title(" Reactivación de Leads")
st.sidebar.markdown("---")

# Health check de la API
try:
 health = requests.get(f"{API_BASE_URL}/health", timeout=2)
 if health.status_code == 200:
 st.sidebar.success(" API Conectada")
 else:
 st.sidebar.error(" API No Responde")
except:
 st.sidebar.error(" API No Disponible")
 st.sidebar.caption(f"URL: {API_BASE_URL}")

st.sidebar.markdown("---")

page = st.sidebar.radio(
 "Navegación",
 [" Dashboard", " Gestionar Leads", " Conversaciones", " Escalaciones", " Análisis"]
)

# Funciones auxiliares
@st.cache_data(ttl=30)
def get_api_stats():
 """Obtener estadísticas del API"""
 try:
 response = requests.get(f"{API_BASE_URL}/api/dashboard/stats", timeout=5)
 if response.status_code == 200:
 return response.json()
 except Exception as e:
 st.error(f"Error conectando con la API: {e}")
 return None

def get_leads(status="cold"):
 """Obtener leads por estado"""
 try:
 response = requests.get(f"{API_BASE_URL}/api/leads?status={status}", timeout=5)
 if response.status_code == 200:
 return response.json()
 except Exception as e:
 st.error(f"Error obteniendo leads: {e}")
 return []

def create_lead(lead_data):
 """Crear nuevo lead"""
 try:
 response = requests.post(
 f"{API_BASE_URL}/api/leads",
 json=lead_data,
 timeout=5
 )
 return response
 except Exception as e:
 st.error(f"Error creando lead: {e}")
 return None

def initiate_reactivation(lead_id):
 """Iniciar proceso de reactivación"""
 try:
 response = requests.post(f"{API_BASE_URL}/api/leads/{lead_id}/reactivate", timeout=10)
 if response.status_code == 200:
 return response.json()
 except Exception as e:
 st.error(f"Error iniciando reactivación: {e}")
 return None

def get_conversation(conversation_id):
 """Obtener historial de conversación"""
 try:
 response = requests.get(f"{API_BASE_URL}/api/conversations/{conversation_id}", timeout=5)
 if response.status_code == 200:
 return response.json()
 except Exception as e:
 st.error(f"Error obteniendo conversación: {e}")
 return None

def send_message(conversation_id, message):
 """Enviar mensaje en una conversación"""
 try:
 response = requests.post(
 f"{API_BASE_URL}/api/conversations/{conversation_id}/message",
 json={"message": message}, # Corregido: usa "message" no "content"
 timeout=10
 )
 if response.status_code == 200:
 return response.json()
 else:
 st.error(f"Error del servidor: {response.status_code}")
 st.error(response.text)
 except Exception as e:
 st.error(f"Error enviando mensaje: {e}")
 return None

def get_escalations(status="pending"):
 """Obtener casos escalados"""
 try:
 response = requests.get(f"{API_BASE_URL}/api/escalations?status={status}", timeout=5)
 if response.status_code == 200:
 return response.json()
 except Exception as e:
 st.error(f"Error obteniendo escalaciones: {e}")
 return []

def format_status(status):
 """Formatear estado con color"""
 status_map = {
 "cold": ("", "Frío", "status-cold"),
 "warm": ("", "Tibio", "status-warm"),
 "hot": ("", "Caliente", "status-hot"),
 "reactivated": ("", "Reactivado", "status-reactivated"),
 "lost": ("", "Perdido", "")
 }
 icon, text, css_class = status_map.get(status, ("", status, ""))
 return f'<span class="{css_class}">{icon} {text}</span>'

def format_channel(channel):
 """Formatear canal con icono"""
 channel_map = {
 "telegram": " Telegram",
 "email": " Email",
 "api": " API",
 "whatsapp": " WhatsApp"
 }
 return channel_map.get(channel, channel)

# ============ PÁGINA: DASHBOARD ============
if page == " Dashboard":
 st.title(" Dashboard de Reactivación de Leads")
 
 # Botón de refresh
 if st.button(" Actualizar Datos"):
 st.cache_data.clear()
 st.rerun()
 
 # Obtener estadísticas
 stats = get_api_stats()
 
 if stats:
 # Mostrar métricas principales
 col1, col2, col3, col4, col5 = st.columns(5)
 
 with col1:
 st.metric(" Leads Fríos", stats.get("cold_leads", 0))
 
 with col2:
 st.metric(" Leads Tibios", stats.get("warm_leads", 0))
 
 with col3:
 st.metric(" Leads Calientes", stats.get("hot_leads", 0))
 
 with col4:
 st.metric(" Reactivados", stats.get("reactivated_leads", 0))
 
 with col5:
 st.metric(" Escalaciones", stats.get("pending_escalations", 0))
 
 st.divider()
 
 # Gráficos
 col1, col2 = st.columns(2)
 
 with col1:
 st.subheader("Distribución de Leads")
 data = {
 "Estado": ["Fríos", "Tibios", "Calientes", "Reactivados"],
 "Cantidad": [
 stats.get("cold_leads", 0),
 stats.get("warm_leads", 0),
 stats.get("hot_leads", 0),
 stats.get("reactivated_leads", 0)
 ]
 }
 df = pd.DataFrame(data)
 st.bar_chart(df.set_index("Estado"))
 
 with col2:
 st.subheader("Información del Agente")
 try:
 response = requests.get(f"{API_BASE_URL}/api/agent/info", timeout=5)
 if response.status_code == 200:
 agent_info = response.json()
 st.write(f"**Modelo LLM:** `{agent_info.get('model', 'N/A')}`")
 st.write(f"**Timeout:** {agent_info.get('timeout', 'N/A')}s")
 st.write(f"**Máx. Turnos:** {agent_info.get('max_turns', 'N/A')}")
 
 if 'tools' in agent_info:
 st.write(f"**Tools Disponibles:** {len(agent_info['tools'])}")
 with st.expander("Ver tools"):
 for tool in agent_info['tools']:
 st.write(f"- {tool}")
 except:
 st.warning("No se pudo obtener información del agente")
 
 # Tasa de conversión
 st.divider()
 total = stats.get("total_leads", 1)
 reactivated = stats.get("reactivated_leads", 0)
 if total > 0:
 rate = (reactivated / total) * 100
 st.metric(" Tasa de Reactivación", f"{rate:.1f}%")
 st.progress(rate / 100)
 else:
 st.error("No se pudieron cargar las estadísticas")

# ============ PÁGINA: GESTIONAR LEADS ============
elif page == " Gestionar Leads":
 st.title(" Gestionar Leads")
 
 tab1, tab2, tab3 = st.tabs(["Ver Leads", "Crear Lead", "Buscar Lead"])
 
 with tab1:
 st.subheader("Leads por Estado")
 
 # Selector de estado
 status_filter = st.selectbox(
 "Filtrar por estado",
 ["cold", "warm", "hot", "reactivated", "lost"],
 format_func=lambda x: {
 "cold": " Fríos",
 "warm": " Tibios",
 "hot": " Calientes",
 "reactivated": " Reactivados",
 "lost": " Perdidos"
 }[x]
 )
 
 leads = get_leads(status_filter)
 
 if leads:
 st.info(f"Se encontraron {len(leads)} leads")
 
 # Crear tabla de leads
 for lead in leads[:20]: # Mostrar primeros 20
 with st.container():
 col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
 
 with col1:
 st.markdown(f"**{lead.get('name', 'N/A')}**")
 st.caption(f" {lead.get('email', 'N/A')}")
 if lead.get('phone'):
 st.caption(f" {lead['phone']}")
 
 with col2:
 if lead.get('company'):
 st.write(f" {lead['company']}")
 st.caption(f" ${lead.get('value', 0):,.0f}")
 
 with col3:
 st.markdown(format_status(lead.get('status', 'cold')), unsafe_allow_html=True)
 channel = lead.get('preferred_channel', 'api')
 st.caption(format_channel(channel))
 
 with col4:
 if lead.get('status') == 'cold':
 if st.button(" Reactivar", key=f"reactivate_{lead['id']}"):
 with st.spinner("Iniciando reactivación..."):
 result = initiate_reactivation(lead['id'])
 if result and result.get("success"):
 st.success(f" Reactivación iniciada")
 with st.expander("Ver respuesta del agente"):
 st.write(result.get('agent_response', ''))
 if 'tools_used' in result:
 st.caption(f"Tools usados: {', '.join(result['tools_used'])}")
 else:
 st.error(" Error iniciando reactivación")
 
 st.divider()
 else:
 st.info(f"No hay leads con estado '{status_filter}'")
 
 with tab2:
 st.subheader("Crear Nuevo Lead")
 
 with st.form("create_lead_form"):
 col1, col2 = st.columns(2)
 
 with col1:
 name = st.text_input("Nombre del Lead *", placeholder="Juan Pérez")
 email = st.text_input("Email *", placeholder="juan@example.com")
 phone = st.text_input("Teléfono", placeholder="+573001234567")
 
 with col2:
 company = st.text_input("Empresa", placeholder="Tech Corp")
 value = st.number_input("Valor Estimado ($)", min_value=0, value=5000)
 preferred_channel = st.selectbox(
 "Canal Preferido *",
 ["telegram", "email", "api", "whatsapp"],
 format_func=lambda x: format_channel(x)
 )
 
 status = st.selectbox(
 "Estado Inicial",
 ["cold", "warm", "hot"],
 format_func=lambda x: {
 "cold": " Frío",
 "warm": " Tibio",
 "hot": " Caliente"
 }[x]
 )
 
 notes = st.text_area("Notas", placeholder="Información adicional sobre el lead...")
 
 submitted = st.form_submit_button(" Crear Lead", use_container_width=True)
 
 if submitted:
 # Validaciones
 if not name or not email:
 st.error(" Nombre y email son obligatorios")
 elif preferred_channel in ["telegram", "whatsapp"] and not phone:
 st.error(f" El teléfono es obligatorio para el canal {format_channel(preferred_channel)}")
 else:
 lead_data = {
 "name": name,
 "email": email,
 "phone": phone if phone else None,
 "company": company if company else None,
 "value": value,
 "notes": notes if notes else None,
 "status": status,
 "preferred_channel": preferred_channel
 }
 
 response = create_lead(lead_data)
 
 if response and response.status_code == 200:
 st.success(" Lead creado exitosamente")
 st.balloons()
 st.json(response.json())
 elif response:
 error_data = response.json()
 st.error(f" Error: {error_data.get('error', 'Error desconocido')}")
 else:
 st.error(" Error creando lead")
 
 with tab3:
 st.subheader("Buscar Lead")
 
 search_type = st.radio("Buscar por:", ["ID", "Email"])
 
 if search_type == "ID":
 lead_id = st.number_input("ID del Lead", min_value=1)
 if st.button(" Buscar"):
 try:
 response = requests.get(f"{API_BASE_URL}/api/leads/{lead_id}", timeout=5)
 if response.status_code == 200:
 lead = response.json()
 st.success("Lead encontrado")
 
 col1, col2 = st.columns(2)
 with col1:
 st.write(f"**Nombre:** {lead.get('name')}")
 st.write(f"**Email:** {lead.get('email')}")
 st.write(f"**Teléfono:** {lead.get('phone', 'N/A')}")
 st.write(f"**Empresa:** {lead.get('company', 'N/A')}")
 
 with col2:
 st.markdown(f"**Estado:** {format_status(lead.get('status'))}", unsafe_allow_html=True)
 st.write(f"**Canal:** {format_channel(lead.get('preferred_channel'))}")
 st.write(f"**Valor:** ${lead.get('value', 0):,.0f}")
 st.write(f"**Creado:** {lead.get('created_at', 'N/A')[:10]}")
 
 if lead.get('notes'):
 st.write(f"**Notas:** {lead['notes']}")
 else:
 st.error("Lead no encontrado")
 except Exception as e:
 st.error(f"Error: {e}")
 else:
 search_email = st.text_input("Email del Lead")
 if st.button(" Buscar"):
 st.info("Funcionalidad de búsqueda por email próximamente")

# ============ PÁGINA: CONVERSACIONES ============
elif page == " Conversaciones":
 st.title(" Conversaciones Activas")
 
 conversation_id = st.number_input("ID de Conversación", min_value=1, value=1)
 
 col1, col2 = st.columns([1, 4])
 with col1:
 load_button = st.button(" Cargar Conversación", use_container_width=True)
 
 if load_button:
 conv_data = get_conversation(conversation_id)
 
 if conv_data:
 # Información de la conversación
 st.info(f"**Lead ID:** {conv_data.get('lead_id')} | **Canal:** {format_channel(conv_data.get('channel'))} | **Estado:** {conv_data.get('status')}")
 
 st.divider()
 
 # Mostrar mensajes
 if conv_data.get("messages"):
 st.subheader("Historial de Mensajes")
 for msg in conv_data["messages"]:
 if msg["role"] == "agent":
 with st.chat_message("assistant", avatar=""):
 st.write(msg["content"])
 st.caption(f" {msg.get('created_at', '')[:19]}")
 elif msg["role"] == "lead":
 with st.chat_message("user", avatar=""):
 st.write(msg["content"])
 st.caption(f" {msg.get('created_at', '')[:19]}")
 elif msg["role"] == "system":
 st.info(f" {msg['content']}")
 else:
 st.warning("No hay mensajes en esta conversación")
 
 # Enviar nuevo mensaje
 st.divider()
 st.subheader("Enviar Mensaje del Lead")
 
 new_message = st.text_area("Mensaje", placeholder="Escribe el mensaje del lead aquí...")
 
 if st.button(" Enviar Mensaje", use_container_width=True):
 if new_message:
 with st.spinner("Procesando mensaje..."):
 result = send_message(conversation_id, new_message)
 if result and result.get("success"):
 st.success(" Mensaje procesado")
 
 with st.expander("Ver respuesta del agente", expanded=True):
 st.write(result.get('agent_response', ''))
 
 if result.get("requirements_captured"):
 st.success(" Requerimientos capturados")
 
 if result.get("escalated"):
 st.warning(" Caso escalado a negociador humano")
 
 if result.get("tools_used"):
 st.caption(f" Tools usados: {', '.join(result['tools_used'])}")
 else:
 st.error(" Error enviando mensaje")
 else:
 st.warning("Por favor escribe un mensaje")
 else:
 st.error("Conversación no encontrada")

# ============ PÁGINA: ESCALACIONES ============
elif page == " Escalaciones":
 st.title(" Casos Escalados")
 
 status_filter = st.selectbox(
 "Filtrar por estado",
 ["pending", "assigned", "in_progress", "resolved"],
 format_func=lambda x: {
 "pending": " Pendiente",
 "assigned": " Asignado",
 "in_progress": " En Progreso",
 "resolved": " Resuelto"
 }[x]
 )
 
 escalations = get_escalations(status_filter)
 
 if escalations:
 st.info(f"Se encontraron {len(escalations)} casos escalados")
 
 for esc in escalations:
 with st.expander(f" Caso #{esc['id']} - Lead ID: {esc['lead_id']} - {esc.get('status', 'N/A').upper()}"):
 col1, col2 = st.columns(2)
 
 with col1:
 st.write(f"**Razón:** {esc.get('reason', 'N/A')}")
 st.write(f"**Estado:** {esc.get('status', 'N/A')}")
 st.write(f"**Conversación ID:** {esc.get('conversation_id', 'N/A')}")
 
 with col2:
 st.write(f"**Asignado a:** {esc.get('assigned_to', 'Sin asignar')}")
 st.write(f"**Creado:** {esc.get('created_at', 'N/A')[:19]}")
 st.write(f"**Actualizado:** {esc.get('updated_at', 'N/A')[:19]}")
 
 if esc.get('notes'):
 st.write(f"**Notas:** {esc['notes']}")
 else:
 st.success(" No hay casos escalados con estado '{}'".format(status_filter))

# ============ PÁGINA: ANÁLISIS ============
elif page == " Análisis":
 st.title(" Análisis y Reportes")
 
 stats = get_api_stats()
 
 if stats:
 # Tasa de reactivación
 st.subheader("Tasa de Reactivación")
 
 total_leads = stats.get("total_leads", 1)
 reactivated = stats.get("reactivated_leads", 0)
 
 if total_leads > 0:
 rate = (reactivated / total_leads) * 100
 
 col1, col2, col3 = st.columns(3)
 with col1:
 st.metric("Total de Leads", total_leads)
 with col2:
 st.metric("Leads Reactivados", reactivated)
 with col3:
 st.metric("Tasa de Reactivación", f"{rate:.1f}%")
 
 st.progress(rate / 100)
 
 st.divider()
 
 # Resumen de actividades
 st.subheader("Resumen de Actividades")
 
 col1, col2, col3, col4 = st.columns(4)
 
 with col1:
 st.metric(" Leads Fríos", stats.get("cold_leads", 0))
 
 with col2:
 st.metric(" Leads Tibios", stats.get("warm_leads", 0))
 
 with col3:
 st.metric(" Leads Calientes", stats.get("hot_leads", 0))
 
 with col4:
 st.metric(" Escalaciones", stats.get("pending_escalations", 0))
 
 st.divider()
 
 # Distribución visual
 st.subheader("Distribución de Leads")
 
 data = pd.DataFrame({
 "Estado": ["Fríos", "Tibios", "Calientes", "Reactivados"],
 "Cantidad": [
 stats.get("cold_leads", 0),
 stats.get("warm_leads", 0),
 stats.get("hot_leads", 0),
 stats.get("reactivated_leads", 0)
 ]
 })
 
 st.bar_chart(data.set_index("Estado"))

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
 st.caption(" Sistema de Reactivación de Leads")
with col2:
 st.caption("Powered by LangChain + FastAPI + Streamlit")
with col3:
 st.caption(f"API: {API_BASE_URL}")
