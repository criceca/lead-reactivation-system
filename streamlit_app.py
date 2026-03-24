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
    .main { padding: 2rem; }
    .metric-card { background-color: #f0f2f6; padding: 1.5rem; border-radius: 0.5rem; margin: 0.5rem 0; }
    .status-cold { color: #2196F3; font-weight: bold; }
    .status-warm { color: #FF9800; font-weight: bold; }
    .status-hot { color: #F44336; font-weight: bold; }
    .status-reactivated { color: #4CAF50; font-weight: bold; }
    .channel-badge { background-color: #E3F2FD; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.85rem; }
    .login-container { max-width: 400px; margin: 4rem auto; padding: 2rem; border-radius: 1rem; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)


# ============ AUTENTICACIÓN ============

def do_login(email: str, password: str) -> bool:
    """Llama al endpoint de login y guarda el usuario en session_state"""
    try:
        resp = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json={"email": email, "password": password},
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            st.session_state["user"] = data["user"]
            return True
        return False
    except Exception:
        return False


def show_login_page():
    """Renderiza la pantalla de login"""
    st.markdown("<h2 style='text-align:center;margin-bottom:0.5rem;'>Reactivación de Leads</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#666;margin-bottom:2rem;'>Inicia sesión para continuar</p>", unsafe_allow_html=True)

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="usuario@empresa.com")
        password = st.text_input("Contraseña", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Iniciar sesión", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Ingresa email y contraseña")
            else:
                with st.spinner("Verificando..."):
                    ok = do_login(email, password)
                if ok:
                    st.rerun()
                else:
                    st.error("Credenciales inválidas")

    st.caption("Usuario por defecto: admin@leadreactivation.com / admin1234")


# Verificar sesión activa
if "user" not in st.session_state:
    show_login_page()
    st.stop()

# ============ APP PRINCIPAL (solo si está autenticado) ============

user = st.session_state["user"]

# Estilos CSS personalizados (ya incluidos arriba)

# Sidebar Navigation
st.sidebar.title(" Reactivación de Leads")
st.sidebar.markdown(f"Hola, **{user['name']}** ({user['role']})")
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
    + ([" Usuarios"] if user["role"] == "admin" else [])
)

if st.sidebar.button(" Cerrar sesión", use_container_width=True):
    del st.session_state["user"]
    st.rerun()

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
            json={"message": message},
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
    
    if st.button(" Actualizar Datos"):
        st.cache_data.clear()
        st.rerun()
    
    stats = get_api_stats()
    
    if stats:
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
        status_filter = st.selectbox(
            "Filtrar por estado",
            ["cold", "warm", "hot", "reactivated", "lost"],
            format_func=lambda x: {
                "cold": " Fríos", "warm": " Tibios", "hot": " Calientes",
                "reactivated": " Reactivados", "lost": " Perdidos"
            }[x]
        )
        
        leads = get_leads(status_filter)
        if leads:
            st.info(f"Se encontraron {len(leads)} leads")
            for lead in leads[:20]:
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    with col1:
                        st.markdown(f"**{lead.get('name', 'N/A')}**")
                        st.caption(f" {lead.get('email', 'N/A')}")
                        if lead.get('phone'): st.caption(f" {lead['phone']}")
                    with col2:
                        if lead.get('company'): st.write(f" {lead['company']}")
                        st.caption(f" ${lead.get('value', 0):,.0f}")
                    with col3:
                        st.markdown(format_status(lead.get('status', 'cold')), unsafe_allow_html=True)
                        st.caption(format_channel(lead.get('preferred_channel', 'api')))
                    with col4:
                        if lead.get('status') == 'cold':
                            if st.button(" Reactivar", key=f"reactivate_{lead['id']}"):
                                with st.spinner("Iniciando reactivación..."):
                                    result = initiate_reactivation(lead['id'])
                                    if result and result.get("success"):
                                        st.success(f" Reactivación iniciada")
                                        with st.expander("Ver respuesta del agente"):
                                            st.write(result.get('agent_response', ''))
                    st.divider()
        else:
            st.info(f"No hay leads con estado '{status_filter}'")

    with tab2:
        st.subheader("Crear Nuevo Lead")
        with st.form("create_lead_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Nombre del Lead *")
                email = st.text_input("Email *")
                phone = st.text_input("Teléfono")
            with col2:
                company = st.text_input("Empresa")
                value = st.number_input("Valor Estimado ($)", min_value=0, value=5000)
                preferred_channel = st.selectbox("Canal Preferido *", ["telegram", "email", "api", "whatsapp"], format_func=format_channel)
            
            status = st.selectbox("Estado Inicial", ["cold", "warm", "hot"])
            notes = st.text_area("Notas")
            submitted = st.form_submit_button(" Crear Lead", use_container_width=True)
            
            if submitted:
                if not name or not email:
                    st.error(" Nombre y email son obligatorios")
                else:
                    lead_data = {"name": name, "email": email, "phone": phone, "company": company, "value": value, "notes": notes, "status": status, "preferred_channel": preferred_channel}
                    response = create_lead(lead_data)
                    if response and response.status_code == 200:
                        st.success(" Lead creado exitosamente")
                        st.balloons()
                    else:
                        st.error(" Error creando lead")

    with tab3:
        st.subheader("Buscar Lead")
        search_type = st.radio("Buscar por:", ["ID", "Email"])
        if search_type == "ID":
            lead_id = st.number_input("ID del Lead", min_value=1)
            if st.button(" Buscar"):
                response = requests.get(f"{API_BASE_URL}/api/leads/{lead_id}")
                if response.status_code == 200:
                    lead = response.json()
                    st.json(lead)
                else:
                    st.error("No encontrado")

# ============ PÁGINA: CONVERSACIONES ============
elif page == " Conversaciones":
    st.title(" Conversaciones Activas")
    conversation_id = st.number_input("ID de Conversación", min_value=1, value=1)
    
    if st.button(" Cargar Conversación"):
        conv_data = get_conversation(conversation_id)
        if conv_data:
            st.info(f"**Lead ID:** {conv_data.get('lead_id')} | **Estado:** {conv_data.get('status')}")
            if conv_data.get("messages"):
                for msg in conv_data["messages"]:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])
            
            st.divider()
            new_message = st.text_area("Enviar respuesta del Lead")
            if st.button(" Enviar Mensaje"):
                result = send_message(conversation_id, new_message)
                if result: st.success("Mensaje enviado")

# ============ PÁGINA: ESCALACIONES ============
elif page == " Escalaciones":
    st.title(" Casos Escalados")
    status_filter = st.selectbox("Filtrar por estado", ["pending", "assigned", "in_progress", "resolved"])
    escalations = get_escalations(status_filter)
    if escalations:
        for esc in escalations:
            with st.expander(f" Caso #{esc['id']} - Lead: {esc['lead_id']}"):
                st.write(f"**Razón:** {esc.get('reason')}")
                st.write(f"**Asignado a:** {esc.get('assigned_to', 'Sin asignar')}")
    else:
        st.info("No hay casos escalados")

# ============ PÁGINA: ANÁLISIS ============
elif page == " Análisis":
    st.title(" Análisis y Reportes")
    stats = get_api_stats()
    if stats:
        total_leads = stats.get("total_leads", 1)
        reactivated = stats.get("reactivated_leads", 0)
        rate = (reactivated / total_leads) * 100
        st.metric("Tasa de Reactivación Global", f"{rate:.1f}%")
        st.progress(rate / 100)
        
        data = pd.DataFrame({
            "Estado": ["Fríos", "Tibios", "Calientes", "Reactivados"],
            "Cantidad": [stats.get("cold_leads", 0), stats.get("warm_leads", 0), stats.get("hot_leads", 0), stats.get("reactivated_leads", 0)]
        })
        st.bar_chart(data.set_index("Estado"))

# ============ PÁGINA: USUARIOS (solo admin) ============
elif page == " Usuarios":
    st.title(" Gestión de Usuarios")
    tab1, tab2 = st.tabs(["Crear Usuario", "Info"])

    with tab1:
        st.subheader("Nuevo Usuario")
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                u_name = st.text_input("Nombre *")
                u_email = st.text_input("Email *")
            with col2:
                u_password = st.text_input("Contraseña *", type="password")
                u_role = st.selectbox("Rol", ["user", "negotiator", "admin"])
            submitted = st.form_submit_button("Crear Usuario", use_container_width=True)
            if submitted:
                if not u_name or not u_email or not u_password:
                    st.error("Todos los campos son obligatorios")
                else:
                    try:
                        resp = requests.post(
                            f"{API_BASE_URL}/api/auth/register",
                            json={"name": u_name, "email": u_email, "password": u_password, "role": u_role},
                            timeout=5,
                        )
                        if resp.status_code == 200:
                            st.success(f"Usuario {u_email} creado correctamente")
                        else:
                            st.error(resp.json().get("detail", "Error creando usuario"))
                    except Exception as e:
                        st.error(f"Error: {e}")

    with tab2:
        st.info("Los roles disponibles son: user (acceso básico), negotiator (gestiona escalaciones), admin (acceso total).")

# Footer
st.divider()
st.caption(" Sistema de Reactivación de Leads | Powered by LangChain + FastAPI + Streamlit")