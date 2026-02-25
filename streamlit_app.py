"""
Frontend Streamlit para el Sistema de Reactivación de Leads
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json
import os

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Reactivación de Leads",
    page_icon="🚀",
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
        color: #666;
    }
    .status-warm {
        color: #ff9800;
    }
    .status-hot {
        color: #f44336;
    }
    .status-reactivated {
        color: #4caf50;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("🎯 Reactivación de Leads")
page = st.sidebar.radio(
    "Navegación",
    ["Dashboard", "Gestionar Leads", "Conversaciones", "Escalaciones", "Análisis"]
)

# Funciones auxiliares
@st.cache_data(ttl=60)
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
            json={"content": message, "role": "lead"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
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

# ============ PÁGINA: DASHBOARD ============
if page == "Dashboard":
    st.title("📊 Dashboard de Reactivación de Leads")
    
    # Obtener estadísticas
    stats = get_api_stats()
    
    if stats:
        # Mostrar métricas principales
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Leads Fríos", stats.get("cold_leads", 0), delta=None)
        
        with col2:
            st.metric("Leads Tibios", stats.get("warm_leads", 0), delta=None)
        
        with col3:
            st.metric("Leads Calientes", stats.get("hot_leads", 0), delta=None)
        
        with col4:
            st.metric("Reactivados", stats.get("reactivated_leads", 0), delta=None)
        
        with col5:
            st.metric("Escalaciones Pendientes", stats.get("pending_escalations", 0), delta=None)
        
        st.divider()
        
        # Gráfico de distribución
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
                    st.write(f"**Modelo LLM:** {agent_info['model']}")
                    st.write(f"**Timeout:** {agent_info['timeout']}s")
                    st.write(f"**Máx. Turnos:** {agent_info['max_turns']}")
                    st.write(f"**Tools Disponibles:** {len(agent_info['tools'])}")
            except:
                st.warning("No se pudo obtener información del agente")

# ============ PÁGINA: GESTIONAR LEADS ============
elif page == "Gestionar Leads":
    st.title("👥 Gestionar Leads")
    
    tab1, tab2, tab3 = st.tabs(["Leads Fríos", "Crear Lead", "Buscar Lead"])
    
    with tab1:
        st.subheader("Leads Fríos Disponibles para Reactivación")
        
        leads = get_leads("cold")
        
        if leads:
            # Crear tabla de leads
            for lead in leads[:10]:  # Mostrar primeros 10
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                
                with col1:
                    st.write(f"**{lead.get('name', 'N/A')}**")
                    st.caption(lead.get('email', 'N/A'))
                
                with col2:
                    st.write(f"Empresa: {lead.get('company', 'N/A')}")
                    st.caption(f"Valor: ${lead.get('value', 0)}")
                
                with col3:
                    st.write(f"Teléfono: {lead.get('phone', 'N/A')}")
                
                with col4:
                    if st.button("Reactivar", key=f"reactivate_{lead['id']}"):
                        result = initiate_reactivation(lead['id'])
                        if result and result.get("success"):
                            st.success(f"Reactivación iniciada para {lead['name']}")
                            st.info(f"Respuesta del agente: {result.get('agent_response', '')[:200]}...")
                        else:
                            st.error("Error iniciando reactivación")
                
                st.divider()
        else:
            st.info("No hay leads fríos disponibles")
    
    with tab2:
        st.subheader("Crear Nuevo Lead")
        
        with st.form("create_lead_form"):
            name = st.text_input("Nombre del Lead")
            email = st.text_input("Email")
            phone = st.text_input("Teléfono")
            company = st.text_input("Empresa")
            value = st.number_input("Valor Estimado", min_value=0)
            notes = st.text_area("Notas")
            
            if st.form_submit_button("Crear Lead"):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/leads",
                        json={
                            "name": name,
                            "email": email,
                            "phone": phone,
                            "company": company,
                            "value": value,
                            "notes": notes,
                            "status": "cold"
                        },
                        timeout=5
                    )
                    if response.status_code == 200:
                        st.success("Lead creado exitosamente")
                        st.rerun()
                    else:
                        st.error("Error creando lead")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with tab3:
        st.subheader("Buscar Lead")
        search_term = st.text_input("Buscar por nombre o email")
        if search_term:
            st.info(f"Buscando: {search_term}")

# ============ PÁGINA: CONVERSACIONES ============
elif page == "Conversaciones":
    st.title("💬 Conversaciones Activas")
    
    conversation_id = st.number_input("ID de Conversación", min_value=1)
    
    if st.button("Cargar Conversación"):
        conv_data = get_conversation(conversation_id)
        
        if conv_data:
            st.subheader(f"Conversación #{conversation_id}")
            
            # Mostrar mensajes
            if conv_data.get("messages"):
                for msg in conv_data["messages"]:
                    if msg["role"] == "agent":
                        with st.chat_message("assistant"):
                            st.write(msg["content"])
                    elif msg["role"] == "lead":
                        with st.chat_message("user"):
                            st.write(msg["content"])
            
            # Enviar nuevo mensaje
            st.divider()
            new_message = st.text_area("Mensaje del Lead")
            
            if st.button("Enviar Mensaje"):
                result = send_message(conversation_id, new_message)
                if result and result.get("success"):
                    st.success("Mensaje procesado")
                    st.info(f"Respuesta del Agente: {result.get('agent_response', '')}")
                    if result.get("escalated"):
                        st.warning("⚠️ Caso escalado a negociador humano")
                else:
                    st.error("Error enviando mensaje")

# ============ PÁGINA: ESCALACIONES ============
elif page == "Escalaciones":
    st.title("⚠️ Casos Escalados")
    
    escalations = get_escalations("pending")
    
    if escalations:
        st.subheader(f"Casos Pendientes: {len(escalations)}")
        
        for esc in escalations:
            with st.expander(f"Caso #{esc['id']} - Lead ID: {esc['lead_id']}"):
                st.write(f"**Razón:** {esc.get('reason', 'N/A')}")
                st.write(f"**Estado:** {esc.get('status', 'N/A')}")
                st.write(f"**Asignado a:** {esc.get('assigned_to', 'Sin asignar')}")
                st.write(f"**Notas:** {esc.get('notes', 'N/A')}")
    else:
        st.success("✅ No hay casos escalados pendientes")

# ============ PÁGINA: ANÁLISIS ============
elif page == "Análisis":
    st.title("📈 Análisis y Reportes")
    
    st.subheader("Tasa de Reactivación")
    
    stats = get_api_stats()
    
    if stats:
        total_leads = stats.get("total_leads", 1)
        reactivated = stats.get("reactivated_leads", 0)
        
        if total_leads > 0:
            rate = (reactivated / total_leads) * 100
            st.metric("Tasa de Reactivación", f"{rate:.1f}%", delta=None)
            
            # Progreso
            st.progress(rate / 100)
        
        st.divider()
        
        st.subheader("Resumen de Actividades")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Leads", stats.get("total_leads", 0))
        
        with col2:
            st.metric("Leads Reactivados", stats.get("reactivated_leads", 0))
        
        with col3:
            st.metric("Escalaciones Pendientes", stats.get("pending_escalations", 0))

# Footer
st.divider()
st.caption("Sistema de Reactivación de Leads | Powered by LangChain + FastAPI + Streamlit")
