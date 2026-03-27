# """
# Frontend Streamlit Mejorado para el Sistema de Reactivación de Leads
# """

# import streamlit as st
# import requests
# import pandas as pd
# from datetime import datetime
# import json
# import os
# import time

# # Configuración de la página
# st.set_page_config(
#     page_title="Sistema de Reactivacion de Leads",
#     page_icon="chart_with_upwards_trend",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # URL de la API
# API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# # ── session_state defaults ────────────────────────────────────────────────────
# if "chat_messages" not in st.session_state:
#     st.session_state.chat_messages = {}   # {conv_id: [{"role":..,"content":..}]}
# if "active_conv_id" not in st.session_state:
#     st.session_state.active_conv_id = None
# if "last_refresh" not in st.session_state:
#     st.session_state.last_refresh = time.time()
# if "auto_refresh" not in st.session_state:
#     st.session_state.auto_refresh = True
# if "leads_search" not in st.session_state:
#     st.session_state.leads_search = ""
# if "leads_channel_filter" not in st.session_state:
#     st.session_state.leads_channel_filter = "all"
# if "leads_sort" not in st.session_state:
#     st.session_state.leads_sort = "value_desc"

# AUTO_REFRESH_INTERVAL = 15  # segundos

# # Estilos CSS personalizados
# st.markdown("""
#     <style>
#     @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

#     html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

#     .stApp { background-color: #0d1117; color: #e2e8f0; }

#     [data-testid="stSidebar"] {
#         background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
#         border-right: 1px solid #21262d;
#     }
#     [data-testid="stSidebar"] .stMarkdown p,
#     [data-testid="stSidebar"] label,
#     [data-testid="stSidebar"] .stRadio label { color: #94a3b8 !important; }

#     .sidebar-brand { display:flex; align-items:center; gap:10px; padding:0.5rem 0 1rem 0; }
#     .sidebar-brand-icon {
#         width:38px; height:38px;
#         background: linear-gradient(135deg, #6366f1, #22d3ee);
#         border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:18px;
#     }
#     .sidebar-brand-text { font-size:15px; font-weight:700; color:#f1f5f9 !important; line-height:1.2; }
#     .sidebar-brand-sub  { font-size:11px; color:#64748b !important; font-weight:400; }

#     .api-status-ok {
#         display:inline-flex; align-items:center; gap:6px;
#         background:rgba(34,197,94,0.12); border:1px solid rgba(34,197,94,0.3);
#         color:#4ade80; padding:5px 12px; border-radius:20px; font-size:12px; font-weight:500;
#         width:100%; justify-content:center;
#     }
#     .api-status-ok::before {
#         content:''; width:7px; height:7px; background:#4ade80;
#         border-radius:50%; box-shadow:0 0 6px #4ade80;
#     }
#     .api-status-err {
#         display:inline-flex; align-items:center; gap:6px;
#         background:rgba(239,68,68,0.12); border:1px solid rgba(239,68,68,0.3);
#         color:#f87171; padding:5px 12px; border-radius:20px; font-size:12px; font-weight:500;
#         width:100%; justify-content:center;
#     }
#     .api-status-err::before { content:''; width:7px; height:7px; background:#f87171; border-radius:50%; }

#     /* Auto-refresh indicator */
#     .refresh-indicator {
#         display:inline-flex; align-items:center; gap:6px;
#         background:rgba(99,102,241,0.1); border:1px solid rgba(99,102,241,0.2);
#         color:#a5b4fc; padding:4px 10px; border-radius:20px; font-size:11px; font-weight:500;
#         margin-top:6px; width:100%; justify-content:center;
#     }
#     @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
#     .refresh-dot { width:6px; height:6px; background:#6366f1; border-radius:50%; animation:pulse 2s infinite; }

#     .page-header { margin-bottom:1.5rem; }
#     .page-title  { font-size:26px; font-weight:700; color:#f1f5f9; margin:0; line-height:1.2; }
#     .page-subtitle { font-size:13px; color:#64748b; margin-top:4px; }

#     .metric-card {
#         background:#161b22; border:1px solid #21262d; border-radius:14px;
#         padding:1.2rem 1.4rem; position:relative; overflow:hidden; transition:border-color 0.2s;
#     }
#     .metric-card:hover { border-color:#30363d; }
#     .metric-card-accent { position:absolute; bottom:0; left:0; right:0; height:3px; border-radius:0 0 14px 14px; }
#     .metric-label { font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.08em; color:#64748b; margin-bottom:8px; }
#     .metric-value { font-size:32px; font-weight:700; color:#f1f5f9; line-height:1; }
#     .metric-icon  { position:absolute; top:1rem; right:1.2rem; font-size:22px; opacity:0.5; }

#     .lead-card {
#         background:#161b22; border:1px solid #21262d; border-radius:12px;
#         padding:1rem 1.2rem; margin-bottom:0.6rem; border-left:3px solid #6366f1;
#         transition:border-color 0.2s, background 0.2s;
#     }
#     .lead-card:hover { background:#1c2128; }
#     .lead-card-cold        { border-left-color:#3b82f6; }
#     .lead-card-warm        { border-left-color:#f59e0b; }
#     .lead-card-hot         { border-left-color:#ef4444; }
#     .lead-card-reactivated { border-left-color:#22c55e; }
#     .lead-card-lost        { border-left-color:#475569; }
#     .lead-name { font-size:15px; font-weight:600; color:#f1f5f9; }
#     .lead-meta { font-size:12px; color:#64748b; margin-top:2px; }

#     .badge { display:inline-flex; align-items:center; gap:4px; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; }
#     .badge-cold        { background:rgba(59,130,246,0.15); color:#60a5fa; border:1px solid rgba(59,130,246,0.3); }
#     .badge-warm        { background:rgba(245,158,11,0.15); color:#fbbf24; border:1px solid rgba(245,158,11,0.3); }
#     .badge-hot         { background:rgba(239,68,68,0.15);  color:#f87171; border:1px solid rgba(239,68,68,0.3); }
#     .badge-reactivated { background:rgba(34,197,94,0.15);  color:#4ade80; border:1px solid rgba(34,197,94,0.3); }
#     .badge-lost        { background:rgba(71,85,105,0.15);  color:#94a3b8; border:1px solid rgba(71,85,105,0.3); }

#     .channel-badge {
#         display:inline-flex; align-items:center; gap:4px;
#         background:rgba(99,102,241,0.12); border:1px solid rgba(99,102,241,0.25);
#         color:#a5b4fc; padding:3px 9px; border-radius:20px; font-size:11px; font-weight:500;
#     }

#     .section-card { background:#161b22; border:1px solid #21262d; border-radius:14px; padding:1.4rem; margin-bottom:1rem; }
#     .section-title { font-size:14px; font-weight:600; color:#94a3b8; text-transform:uppercase; letter-spacing:0.07em; margin-bottom:1rem; }

#     .info-box {
#         background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.2);
#         border-radius:10px; padding:0.8rem 1rem; color:#a5b4fc; font-size:13px;
#     }

#     .stProgress > div > div { background:linear-gradient(90deg,#6366f1,#22d3ee) !important; border-radius:4px; }
#     .stProgress > div { background:#21262d !important; border-radius:4px; }

#     .stButton > button {
#         background:linear-gradient(135deg,#6366f1,#4f46e5); color:white; border:none;
#         border-radius:8px; font-weight:500; font-size:13px; padding:0.4rem 1rem;
#         transition:opacity 0.2s, transform 0.1s;
#     }
#     .stButton > button:hover { opacity:0.9; transform:translateY(-1px); border:none; color:white; }
#     .stButton > button:active { transform:translateY(0); }

#     .stTabs [data-baseweb="tab-list"] {
#         background:#161b22; border-radius:10px; padding:4px; gap:2px; border:1px solid #21262d;
#     }
#     .stTabs [data-baseweb="tab"] {
#         background:transparent; color:#64748b; border-radius:7px; font-size:13px; font-weight:500; padding:6px 16px;
#     }
#     .stTabs [aria-selected="true"] { background:linear-gradient(135deg,#6366f1,#4f46e5) !important; color:white !important; }

#     .stTextInput > div > div > input,
#     .stNumberInput > div > div > input,
#     .stTextArea > div > div > textarea,
#     .stSelectbox > div > div {
#         background:#0d1117 !important; border:1px solid #21262d !important;
#         border-radius:8px !important; color:#e2e8f0 !important;
#     }
#     .stTextInput > div > div > input:focus,
#     .stTextArea > div > div > textarea:focus {
#         border-color:#6366f1 !important; box-shadow:0 0 0 2px rgba(99,102,241,0.2) !important;
#     }

#     hr { border-color:#21262d !important; margin:1.2rem 0 !important; }

#     .footer { text-align:center; color:#334155; font-size:12px; padding:1rem 0 0.5rem 0; }
#     .footer span {
#         background:linear-gradient(90deg,#6366f1,#22d3ee);
#         -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-weight:600;
#     }

#     [data-testid="stChatMessage"] {
#         background:#161b22 !important; border:1px solid #21262d !important;
#         border-radius:12px !important; margin-bottom:0.5rem !important;
#     }

#     /* Chat input */
#     [data-testid="stChatInput"] textarea {
#         background:#161b22 !important; border:1px solid #21262d !important;
#         border-radius:12px !important; color:#e2e8f0 !important;
#     }
#     [data-testid="stChatInput"] textarea:focus {
#         border-color:#6366f1 !important; box-shadow:0 0 0 2px rgba(99,102,241,0.2) !important;
#     }

#     .streamlit-expanderHeader {
#         background:#161b22 !important; border:1px solid #21262d !important;
#         border-radius:10px !important; color:#94a3b8 !important;
#     }
#     .streamlit-expanderContent {
#         background:#0d1117 !important; border:1px solid #21262d !important; border-top:none !important;
#     }

#     [data-testid="stMetric"] { background:#161b22; border:1px solid #21262d; border-radius:12px; padding:1rem; }
#     [data-testid="stMetricLabel"] { color:#64748b !important; font-size:12px !important; }
#     [data-testid="stMetricValue"] { color:#f1f5f9 !important; }

#     [data-testid="stSidebar"] .stRadio > div { gap:4px; }
#     [data-testid="stSidebar"] .stRadio label {
#         background:transparent; border-radius:8px; padding:6px 10px;
#         transition:background 0.15s; font-size:13px !important;
#     }
#     [data-testid="stSidebar"] .stRadio label:hover { background:rgba(99,102,241,0.1); }

#     [data-testid="stSelectbox"] label { color:#94a3b8 !important; font-size:13px !important; }

#     [data-testid="stFormSubmitButton"] > button {
#         background:linear-gradient(135deg,#6366f1,#4f46e5) !important;
#         color:white !important; border:none !important; border-radius:8px !important; font-weight:600 !important;
#     }

#     .stSpinner > div { border-top-color:#6366f1 !important; }
#     .stCaption { color:#475569 !important; font-size:11px !important; }
#     .stAlert { border-radius:10px !important; border:none !important; }

#     /* Skeleton loader */
#     .skeleton {
#         background: linear-gradient(90deg, #161b22 25%, #1c2128 50%, #161b22 75%);
#         background-size: 200% 100%;
#         animation: shimmer 1.5s infinite;
#         border-radius: 10px;
#         height: 80px;
#         margin-bottom: 0.6rem;
#     }
#     @keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }
#     </style>
# """, unsafe_allow_html=True)


# # ============ AUTENTICACIÓN ============

# def do_login(email: str, password: str) -> bool:
#     """Llama al endpoint de login y guarda el usuario en session_state"""
#     try:
#         resp = requests.post(
#             f"{API_BASE_URL}/api/auth/login",
#             json={"email": email, "password": password},
#             timeout=5,
#         )
#         if resp.status_code == 200:
#             data = resp.json()
#             st.session_state["user"] = data["user"]
#             return True
#         return False
#     except Exception:
#         return False


# def show_login_page():
#     """Renderiza la pantalla de login"""
#     st.markdown("<h2 style='text-align:center;margin-bottom:0.5rem;'>Reactivación de Leads</h2>", unsafe_allow_html=True)
#     st.markdown("<p style='text-align:center;color:#666;margin-bottom:2rem;'>Inicia sesión para continuar</p>", unsafe_allow_html=True)

#     with st.form("login_form"):
#         email = st.text_input("Email", placeholder="usuario@empresa.com")
#         password = st.text_input("Contraseña", type="password", placeholder="••••••••")
#         submitted = st.form_submit_button("Iniciar sesión", use_container_width=True)

#         if submitted:
#             if not email or not password:
#                 st.error("Ingresa email y contraseña")
#             else:
#                 with st.spinner("Verificando..."):
#                     ok = do_login(email, password)
#                 if ok:
#                     st.rerun()
#                 else:
#                     st.error("Credenciales inválidas")

#     st.caption("Usuario por defecto: admin@leadreactivation.com / admin1234")


# # Verificar sesión activa
# if "user" not in st.session_state:
#     show_login_page()
#     st.stop()


# # ── Sidebar ───────────────────────────────────────────────────────────────────
# st.sidebar.markdown("""
#     <div class="sidebar-brand">
#         <div class="sidebar-brand-icon">📈</div>
#         <div>
#             <div class="sidebar-brand-text">ReactivaLeads</div>
#             <div class="sidebar-brand-sub">CRM Inteligente</div>
#         </div>
#     </div>
# """, unsafe_allow_html=True)

# st.sidebar.markdown("---")

# # Health check
# try:
#     health = requests.get(f"{API_BASE_URL}/health", timeout=2)
#     if health.status_code == 200:
#         st.sidebar.markdown('<div class="api-status-ok">API Conectada</div>', unsafe_allow_html=True)
#     else:
#         st.sidebar.markdown('<div class="api-status-err">API No Responde</div>', unsafe_allow_html=True)
# except:
#     st.sidebar.markdown('<div class="api-status-err">API No Disponible</div>', unsafe_allow_html=True)
#     st.sidebar.caption(f"URL: {API_BASE_URL}")

# # Auto-refresh toggle + indicator
# st.sidebar.markdown("---")
# st.session_state.auto_refresh = st.sidebar.toggle("Auto-refresh (15s)", value=st.session_state.auto_refresh)
# if st.session_state.auto_refresh:
#     elapsed = int(time.time() - st.session_state.last_refresh)
#     remaining = max(0, AUTO_REFRESH_INTERVAL - elapsed)
#     st.sidebar.markdown(
#         f'<div class="refresh-indicator"><div class="refresh-dot"></div>Actualiza en {remaining}s</div>',
#         unsafe_allow_html=True
#     )

# st.sidebar.markdown("---")

# page = st.sidebar.radio(
#     "Navegación",
#     ["📊 Dashboard", "👥 Gestionar Leads", "💬 Conversaciones", "🚨 Escalaciones", "📈 Análisis"]
# )

# # ── Auto-refresh logic ────────────────────────────────────────────────────────
# if st.session_state.auto_refresh and page == "📊 Dashboard":
#     if time.time() - st.session_state.last_refresh >= AUTO_REFRESH_INTERVAL:
#         st.session_state.last_refresh = time.time()
#         st.cache_data.clear()
#         st.rerun()

# # ── Funciones auxiliares ──────────────────────────────────────────────────────
# @st.cache_data(ttl=30)
# def get_api_stats():
#     try:
#         response = requests.get(f"{API_BASE_URL}/api/dashboard/stats", timeout=5)
#         if response.status_code == 200:
#             return response.json()
#     except Exception as e:
#         st.error(f"Error conectando con la API: {e}")
#     return None

# def get_leads(status="cold"):
#     try:
#         response = requests.get(f"{API_BASE_URL}/api/leads?status={status}", timeout=5)
#         if response.status_code == 200:
#             return response.json()
#     except Exception as e:
#         st.error(f"Error obteniendo leads: {e}")
#     return []

# def create_lead(lead_data):
#     try:
#         response = requests.post(f"{API_BASE_URL}/api/leads", json=lead_data, timeout=5)
#         return response
#     except Exception as e:
#         st.error(f"Error creando lead: {e}")
#     return None

# def initiate_reactivation(lead_id):
#     try:
#         response = requests.post(f"{API_BASE_URL}/api/leads/{lead_id}/reactivate", timeout=10)
#         if response.status_code == 200:
#             return response.json()
#     except Exception as e:
#         st.error(f"Error iniciando reactivación: {e}")
#     return None

# def get_conversation(conversation_id):
#     try:
#         response = requests.get(f"{API_BASE_URL}/api/conversations/{conversation_id}", timeout=5)
#         if response.status_code == 200:
#             return response.json()
#     except Exception as e:
#         st.error(f"Error obteniendo conversación: {e}")
#     return None

# def get_message(conversation_id):
#     """Obtener historial de conversación"""
#     try:
#         response = requests.get(f"{API_BASE_URL}/api/conversations/{conversation_id}/message", timeout=5)
#         if response.status_code == 200:
#             return response.json()
#     except Exception as e:
#         st.error(f"Error obteniendo mensaje de la conversacion: {e}")
#     return None

# def send_message(conversation_id, message):
#     try:
#         response = requests.post(
#             f"{API_BASE_URL}/api/conversations/{conversation_id}/message",
#             json={"message": message},
#             timeout=10
#         )
#         if response.status_code == 200:
#             return response.json()
#         else:
#             st.error(f"Error del servidor: {response.status_code}")
#             st.error(response.text)
#     except Exception as e:
#         st.error(f"Error enviando mensaje: {e}")
#     return None

# def get_escalations(status="pending"):
#     try:
#         response = requests.get(f"{API_BASE_URL}/api/escalations?status={status}", timeout=5)
#         if response.status_code == 200:
#             return response.json()
#     except Exception as e:
#         st.error(f"Error obteniendo escalaciones: {e}")
#     return []

# def format_status(status):
#     status_map = {
#         "cold":        ("❄️", "Frío",       "badge-cold"),
#         "warm":        ("🔥", "Tibio",      "badge-warm"),
#         "hot":         ("⚡", "Caliente",   "badge-hot"),
#         "reactivated": ("✅", "Reactivado", "badge-reactivated"),
#         "lost":        ("💀", "Perdido",    "badge-lost"),
#     }
#     icon, text, css = status_map.get(status, ("", status, "badge-lost"))
#     return f'<span class="badge {css}">{icon} {text}</span>'

# def format_channel(channel):
#     channel_map = {
#         "telegram": "✈️ Telegram",
#         "email":    "📧 Email",
#         "api":      "🔌 API",
#         "whatsapp": "💬 WhatsApp"
#     }
#     return channel_map.get(channel, channel)

# def metric_card(label, value, icon, accent_color):
#     return f"""
#     <div class="metric-card">
#         <div class="metric-icon">{icon}</div>
#         <div class="metric-label">{label}</div>
#         <div class="metric-value">{value}</div>
#         <div class="metric-card-accent" style="background:{accent_color};"></div>
#     </div>
#     """

# def lead_card_class(status):
#     return {
#         "cold": "lead-card-cold", "warm": "lead-card-warm",
#         "hot": "lead-card-hot", "reactivated": "lead-card-reactivated", "lost": "lead-card-lost",
#     }.get(status, "")

# def skeleton_loader(n=3):
#     return "".join(['<div class="skeleton"></div>' for _ in range(n)])


# # ============ PÁGINA: DASHBOARD ============
# if page == "📊 Dashboard":
#     col_title, col_refresh = st.columns([5, 1])
#     with col_title:
#         st.markdown("""
#             <div class="page-header">
#                 <div class="page-title">📊 Dashboard</div>
#                 <div class="page-subtitle">Resumen en tiempo real del sistema de reactivación</div>
#             </div>
#         """, unsafe_allow_html=True)
#     with col_refresh:
#         if st.button("🔄 Actualizar"):
#             st.session_state.last_refresh = time.time()
#             st.cache_data.clear()
#             st.rerun()

#     with st.spinner("Cargando estadísticas..."):
#         stats = get_api_stats()

#     if stats:
#         col1, col2, col3, col4, col5 = st.columns(5)
#         with col1:
#             st.markdown(metric_card("Leads Fríos",    stats.get("cold_leads", 0),         "❄️", "#3b82f6"), unsafe_allow_html=True)
#         with col2:
#             st.markdown(metric_card("Leads Tibios",   stats.get("warm_leads", 0),         "🔥", "#f59e0b"), unsafe_allow_html=True)
#         with col3:
#             st.markdown(metric_card("Leads Calientes",stats.get("hot_leads", 0),          "⚡", "#ef4444"), unsafe_allow_html=True)
#         with col4:
#             st.markdown(metric_card("Reactivados",    stats.get("reactivated_leads", 0),  "✅", "#22c55e"), unsafe_allow_html=True)
#         with col5:
#             st.markdown(metric_card("Escalaciones",   stats.get("pending_escalations", 0),"🚨", "#a855f7"), unsafe_allow_html=True)

#         st.markdown("<br>", unsafe_allow_html=True)
#         col1, col2 = st.columns(2)

#         with col1:
#             st.markdown('<div class="section-card"><div class="section-title">Distribución de Leads</div>', unsafe_allow_html=True)
#             data = pd.DataFrame({
#                 "Estado":   ["Fríos", "Tibios", "Calientes", "Reactivados"],
#                 "Cantidad": [stats.get("cold_leads",0), stats.get("warm_leads",0),
#                              stats.get("hot_leads",0),  stats.get("reactivated_leads",0)]
#             })
#             st.bar_chart(data.set_index("Estado"))
#             st.markdown('</div>', unsafe_allow_html=True)

#         with col2:
#             st.markdown('<div class="section-card"><div class="section-title">Información del Agente</div>', unsafe_allow_html=True)
#             try:
#                 response = requests.get(f"{API_BASE_URL}/api/agent/info", timeout=5)
#                 if response.status_code == 200:
#                     agent_info = response.json()
#                     st.write(f"**Modelo LLM:** `{agent_info.get('model', 'N/A')}`")
#                     st.write(f"**Timeout:** {agent_info.get('timeout', 'N/A')}s")
#                     st.write(f"**Máx. Turnos:** {agent_info.get('max_turns', 'N/A')}")
#                     if 'tools' in agent_info:
#                         st.write(f"**Tools Disponibles:** {len(agent_info['tools'])}")
#                         with st.expander("Ver tools"):
#                             for tool in agent_info['tools']:
#                                 st.write(f"- {tool}")
#             except:
#                 st.warning("No se pudo obtener información del agente")
#             st.markdown('</div>', unsafe_allow_html=True)

#         st.markdown("<br>", unsafe_allow_html=True)
#         total      = stats.get("total_leads", 1)
#         reactivated = stats.get("reactivated_leads", 0)
#         if total > 0:
#             rate = (reactivated / total) * 100
#             st.markdown(f"""
#                 <div class="section-card">
#                     <div class="section-title">Tasa de Reactivación Global</div>
#                     <div style="font-size:36px;font-weight:700;color:#f1f5f9;margin-bottom:0.8rem;">{rate:.1f}%</div>
#                 </div>
#             """, unsafe_allow_html=True)
#             st.progress(rate / 100)
#     else:
#         st.markdown(skeleton_loader(5), unsafe_allow_html=True)
#         st.markdown('<div class="info-box">⚠️ No se pudieron cargar las estadísticas. Verifica que la API esté activa.</div>', unsafe_allow_html=True)


# # ============ PÁGINA: GESTIONAR LEADS ============
# elif page == "👥 Gestionar Leads":
#     st.markdown("""
#         <div class="page-header">
#             <div class="page-title">👥 Gestionar Leads</div>
#             <div class="page-subtitle">Visualiza, crea y gestiona tus leads</div>
#         </div>
#     """, unsafe_allow_html=True)

#     tab1, tab2, tab3 = st.tabs(["📋 Ver Leads", "➕ Crear Lead", "🔍 Buscar Lead"])

#     with tab1:
#         # ── Filtros combinados ────────────────────────────────────────────────
#         fc1, fc2, fc3, fc4 = st.columns([3, 2, 2, 2])
#         with fc1:
#             search_query = st.text_input("🔍 Buscar por nombre o email", value=st.session_state.leads_search,
#                                          placeholder="Ej: Juan o juan@empresa.com")
#             st.session_state.leads_search = search_query
#         with fc2:
#             status_filter = st.selectbox(
#                 "Estado",
#                 ["cold", "warm", "hot", "reactivated", "lost"],
#                 format_func=lambda x: {"cold":"❄️ Fríos","warm":"🔥 Tibios","hot":"⚡ Calientes",
#                                         "reactivated":"✅ Reactivados","lost":"💀 Perdidos"}[x]
#             )
#         with fc3:
#             channel_filter = st.selectbox(
#                 "Canal",
#                 ["all", "telegram", "email", "api", "whatsapp"],
#                 format_func=lambda x: "🌐 Todos" if x == "all" else format_channel(x),
#                 index=["all","telegram","email","api","whatsapp"].index(st.session_state.leads_channel_filter)
#             )
#             st.session_state.leads_channel_filter = channel_filter
#         with fc4:
#             sort_option = st.selectbox(
#                 "Ordenar por",
#                 ["value_desc", "value_asc", "name_asc"],
#                 format_func=lambda x: {"value_desc":"💰 Valor (mayor)", "value_asc":"💰 Valor (menor)", "name_asc":"🔤 Nombre A-Z"}[x],
#                 index=["value_desc","value_asc","name_asc"].index(st.session_state.leads_sort)
#             )
#             st.session_state.leads_sort = sort_option

#         with st.spinner("Cargando leads..."):
#             leads = get_leads(status_filter)

#         # Aplicar filtros locales
#         if search_query:
#             q = search_query.lower()
#             leads = [l for l in leads if q in l.get("name","").lower() or q in l.get("email","").lower()]
#         if channel_filter != "all":
#             leads = [l for l in leads if l.get("preferred_channel") == channel_filter]

#         # Ordenamiento
#         if sort_option == "value_desc":
#             leads = sorted(leads, key=lambda l: l.get("value", 0), reverse=True)
#         elif sort_option == "value_asc":
#             leads = sorted(leads, key=lambda l: l.get("value", 0))
#         elif sort_option == "name_asc":
#             leads = sorted(leads, key=lambda l: l.get("name", "").lower())

#         if leads:
#             st.markdown(f'<div class="info-box">Se encontraron <strong>{len(leads)}</strong> leads</div><br>', unsafe_allow_html=True)
#             for lead in leads[:20]:
#                 css_class = lead_card_class(lead.get('status', 'cold'))
#                 col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
#                 with col1:
#                     st.markdown(f"""
#                         <div class="lead-card {css_class}">
#                             <div class="lead-name">{lead.get('name','N/A')}</div>
#                             <div class="lead-meta">📧 {lead.get('email','N/A')}</div>
#                             {"<div class='lead-meta'>📱 " + lead['phone'] + "</div>" if lead.get('phone') else ""}
#                         </div>
#                     """, unsafe_allow_html=True)
#                 with col2:
#                     st.markdown(f"""
#                         <div style="padding-top:0.6rem;">
#                             {"<div style='color:#94a3b8;font-size:13px;'>🏢 " + lead['company'] + "</div>" if lead.get('company') else ""}
#                             <div style='color:#64748b;font-size:12px;margin-top:4px;'>💰 ${lead.get('value',0):,.0f}</div>
#                         </div>
#                     """, unsafe_allow_html=True)
#                 with col3:
#                     st.markdown(f"""
#                         <div style="padding-top:0.6rem;">
#                             {format_status(lead.get('status','cold'))}
#                             <div style="margin-top:6px;">
#                                 <span class="channel-badge">{format_channel(lead.get('preferred_channel','api'))}</span>
#                             </div>
#                         </div>
#                     """, unsafe_allow_html=True)
#                 with col4:
#                     if lead.get('status') == 'cold':
#                         if st.button("⚡ Reactivar", key=f"reactivate_{lead['id']}"):
#                             with st.spinner("Iniciando reactivación..."):
#                                 result = initiate_reactivation(lead['id'])
#                                 if result and result.get("success"):
#                                     st.success("✅ Reactivación iniciada")
#                                     with st.expander("Ver respuesta del agente"):
#                                         st.write(result.get('agent_response', ''))
#                 st.markdown("<hr>", unsafe_allow_html=True)
#         else:
#             st.markdown(skeleton_loader(3), unsafe_allow_html=True)
#             st.markdown('<div class="info-box">No se encontraron leads con esos filtros.</div>', unsafe_allow_html=True)

#     with tab2:
#         st.markdown('<div class="section-card"><div class="section-title">Nuevo Lead</div>', unsafe_allow_html=True)
#         with st.form("create_lead_form"):
#             col1, col2 = st.columns(2)
#             with col1:
#                 name  = st.text_input("Nombre del Lead *")
#                 email = st.text_input("Email *")
#                 phone = st.text_input("Teléfono")
#             with col2:
#                 company   = st.text_input("Empresa")
#                 value     = st.number_input("Valor Estimado ($)", min_value=0, value=5000)
#                 preferred_channel = st.selectbox("Canal Preferido *", ["telegram","email","api","whatsapp"], format_func=format_channel)
#             status    = st.selectbox("Estado Inicial", ["cold","warm","hot"])
#             notes     = st.text_area("Notas")
#             submitted = st.form_submit_button("➕ Crear Lead", use_container_width=True)
#             if submitted:
#                 if not name or not email:
#                     st.error("⚠️ Nombre y email son obligatorios")
#                 else:
#                     lead_data = {"name":name,"email":email,"phone":phone,"company":company,
#                                  "value":value,"notes":notes,"status":status,"preferred_channel":preferred_channel}
#                     response = create_lead(lead_data)
#                     if response and response.status_code == 200:
#                         st.success("✅ Lead creado exitosamente")
#                         st.balloons()
#                     else:
#                         st.error("❌ Error creando lead")
#         st.markdown('</div>', unsafe_allow_html=True)

#     with tab3:
#         st.markdown('<div class="section-card"><div class="section-title">Buscar Lead</div>', unsafe_allow_html=True)
#         search_type = st.radio("Buscar por:", ["ID", "Email"])
#         if search_type == "ID":
#             lead_id = st.number_input("ID del Lead", min_value=1)
#             if st.button("🔍 Buscar"):
#                 response = requests.get(f"{API_BASE_URL}/api/leads/{lead_id}")
#                 if response.status_code == 200:
#                     st.json(response.json())
#                 else:
#                     st.error("No encontrado")
#         st.markdown('</div>', unsafe_allow_html=True)


# # ============ PÁGINA: CONVERSACIONES ============
# elif page == "💬 Conversaciones":
#     st.markdown("""
#         <div class="page-header">
#             <div class="page-title">💬 Conversaciones Activas</div>
#             <div class="page-subtitle">Historial y gestión de conversaciones con leads</div>
#         </div>
#     """, unsafe_allow_html=True)

#     col_id, col_btn = st.columns([3, 1])
#     with col_id:
#         conversation_id = st.number_input("ID de Conversación", min_value=1, value=st.session_state.active_conv_id or 1)
#     with col_btn:
#         st.markdown("<br>", unsafe_allow_html=True)
#         load_btn = st.button("📂 Cargar")

#     if load_btn:
#         with st.spinner("Cargando conversación..."):
#             conv_data = get_conversation(conversation_id)
#         if conv_data:
#             st.session_state.active_conv_id = conversation_id
#             # Inicializar historial en session_state desde la API
#             if conversation_id not in st.session_state.chat_messages:
#                 st.session_state.chat_messages[conversation_id] = conv_data.get("messages", [])
#             st.markdown(f"""
#                 <div class="info-box">
#                     <strong>Lead ID:</strong> {conv_data.get('lead_id')} &nbsp;|&nbsp;
#                     <strong>Estado:</strong> {conv_data.get('status')}
#                 </div><br>
#             """, unsafe_allow_html=True)
#         else:
#             st.markdown(skeleton_loader(2), unsafe_allow_html=True)

#     # Mostrar chat si hay conversación activa
#     active_id = st.session_state.active_conv_id
#     if active_id and active_id in st.session_state.chat_messages:
#         messages = st.session_state.chat_messages[active_id]

#         chat_container = st.container()
#         with chat_container:
#             if messages:
#                 for msg in messages:
#                     with st.chat_message(msg["role"]):
#                         st.write(msg["content"])
#             else:
#                 st.markdown('<div class="info-box">💬 No hay mensajes aún en esta conversación.</div>', unsafe_allow_html=True)

#         # Chat input persistente
#         if user_input := st.chat_input("Escribe la respuesta del lead..."):
#             # Mostrar mensaje del usuario inmediatamente
#             st.session_state.chat_messages[active_id].append({"role": "user", "content": user_input})
#             with st.chat_message("user"):
#                 st.write(user_input)

#             # Enviar y mostrar respuesta del agente
#             with st.chat_message("assistant"):
#                 with st.spinner("El agente está respondiendo..."):
#                     result = send_message(active_id, user_input)
#                 if result:
#                     agent_reply = result.get("agent_response", result.get("message", ""))
#                     st.write(agent_reply)
#                     st.session_state.chat_messages[active_id].append({"role": "assistant", "content": agent_reply})
#                 else:
#                     st.error("No se pudo obtener respuesta del agente")


# # ============ PÁGINA: ESCALACIONES ============
# elif page == "🚨 Escalaciones":
#     st.markdown("""
#         <div class="page-header">
#             <div class="page-title">🚨 Casos Escalados</div>
#             <div class="page-subtitle">Gestión de casos que requieren atención humana</div>
#         </div>
#     """, unsafe_allow_html=True)

#     status_filter = st.selectbox("Filtrar por estado", ["pending","assigned","in_progress","resolved"])

#     with st.spinner("Cargando escalaciones..."):
#         escalations = get_escalations(status_filter)

#     if escalations:
#         for esc in escalations:
#             with st.expander(f"🚨 Caso #{esc['id']} — Lead: {esc['lead_id']}"):
#                 st.write(f"**Razón:** {esc.get('reason')}")
#                 st.write(f"**Asignado a:** {esc.get('assigned_to', 'Sin asignar')}")
#     else:
#         st.markdown(skeleton_loader(2), unsafe_allow_html=True)
#         st.markdown('<div class="info-box">✅ No hay casos escalados con ese estado.</div>', unsafe_allow_html=True)


# # ============ PÁGINA: ANÁLISIS ============
# elif page == "📈 Análisis":
#     st.markdown("""
#         <div class="page-header">
#             <div class="page-title">📈 Análisis y Reportes</div>
#             <div class="page-subtitle">Métricas de rendimiento del sistema</div>
#         </div>
#     """, unsafe_allow_html=True)

#     with st.spinner("Cargando análisis..."):
#         stats = get_api_stats()

#     if stats:
#         total_leads = stats.get("total_leads", 1)
#         reactivated = stats.get("reactivated_leads", 0)
#         rate = (reactivated / total_leads) * 100

#         st.markdown(f"""
#             <div class="section-card">
#                 <div class="section-title">Tasa de Reactivación Global</div>
#                 <div style="font-size:42px;font-weight:700;color:#f1f5f9;margin-bottom:0.8rem;">{rate:.1f}%</div>
#                 <div style="color:#64748b;font-size:13px;">{reactivated} de {total_leads} leads reactivados</div>
#             </div>
#         """, unsafe_allow_html=True)
#         st.progress(rate / 100)

#         st.markdown("<br>", unsafe_allow_html=True)
#         st.markdown('<div class="section-card"><div class="section-title">Distribución por Estado</div>', unsafe_allow_html=True)
#         data = pd.DataFrame({
#             "Estado":   ["Fríos","Tibios","Calientes","Reactivados"],
#             "Cantidad": [stats.get("cold_leads",0), stats.get("warm_leads",0),
#                          stats.get("hot_leads",0),  stats.get("reactivated_leads",0)]
#         })
#         st.bar_chart(data.set_index("Estado"))
#         st.markdown('</div>', unsafe_allow_html=True)
#     else:
#         st.markdown(skeleton_loader(3), unsafe_allow_html=True)
#         st.markdown('<div class="info-box">⚠️ No se pudieron cargar los datos de análisis.</div>', unsafe_allow_html=True)


# # ── Footer ────────────────────────────────────────────────────────────────────
# st.markdown("<hr>", unsafe_allow_html=True)
# st.markdown("""
#     <div class="footer">
#         Sistema de Reactivación de Leads &nbsp;|&nbsp;
#         Powered by <span>LangChain + FastAPI + Streamlit</span>
#     </div>
# """, unsafe_allow_html=True)

# # ── Auto-refresh trigger (al final para no bloquear render) ───────────────────
# if st.session_state.auto_refresh and page == "📊 Dashboard":
#     time.sleep(1)
#     st.rerun()

"""
Frontend Streamlit Mejorado para el Sistema de Reactivación de Leads
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json
import os
import time

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Reactivacion de Leads",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL de la API
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# ── session_state defaults ────────────────────────────────────────────────────
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = {}   # {conv_id: [{"role":..,"content":..}]}
if "active_conv_id" not in st.session_state:
    st.session_state.active_conv_id = None
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True
if "leads_search" not in st.session_state:
    st.session_state.leads_search = ""
if "leads_channel_filter" not in st.session_state:
    st.session_state.leads_channel_filter = "all"
if "leads_sort" not in st.session_state:
    st.session_state.leads_sort = "value_desc"

AUTO_REFRESH_INTERVAL = 15  # segundos

# Estilos CSS personalizados
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp { background-color: #0d1117; color: #e2e8f0; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
        border-right: 1px solid #21262d;
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stRadio label { color: #94a3b8 !important; }

    .sidebar-brand { display:flex; align-items:center; gap:10px; padding:0.5rem 0 1rem 0; }
    .sidebar-brand-icon {
        width:38px; height:38px;
        background: linear-gradient(135deg, #6366f1, #22d3ee);
        border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:18px;
    }
    .sidebar-brand-text { font-size:15px; font-weight:700; color:#f1f5f9 !important; line-height:1.2; }
    .sidebar-brand-sub  { font-size:11px; color:#64748b !important; font-weight:400; }

    .api-status-ok {
        display:inline-flex; align-items:center; gap:6px;
        background:rgba(34,197,94,0.12); border:1px solid rgba(34,197,94,0.3);
        color:#4ade80; padding:5px 12px; border-radius:20px; font-size:12px; font-weight:500;
        width:100%; justify-content:center;
    }
    .api-status-ok::before {
        content:''; width:7px; height:7px; background:#4ade80;
        border-radius:50%; box-shadow:0 0 6px #4ade80;
    }
    .api-status-err {
        display:inline-flex; align-items:center; gap:6px;
        background:rgba(239,68,68,0.12); border:1px solid rgba(239,68,68,0.3);
        color:#f87171; padding:5px 12px; border-radius:20px; font-size:12px; font-weight:500;
        width:100%; justify-content:center;
    }
    .api-status-err::before { content:''; width:7px; height:7px; background:#f87171; border-radius:50%; }

    /* Auto-refresh indicator */
    .refresh-indicator {
        display:inline-flex; align-items:center; gap:6px;
        background:rgba(99,102,241,0.1); border:1px solid rgba(99,102,241,0.2);
        color:#a5b4fc; padding:4px 10px; border-radius:20px; font-size:11px; font-weight:500;
        margin-top:6px; width:100%; justify-content:center;
    }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
    .refresh-dot { width:6px; height:6px; background:#6366f1; border-radius:50%; animation:pulse 2s infinite; }

    .page-header { margin-bottom:1.5rem; }
    .page-title  { font-size:26px; font-weight:700; color:#f1f5f9; margin:0; line-height:1.2; }
    .page-subtitle { font-size:13px; color:#64748b; margin-top:4px; }

    .metric-card {
        background:#161b22; border:1px solid #21262d; border-radius:14px;
        padding:1.2rem 1.4rem; position:relative; overflow:hidden; transition:border-color 0.2s;
    }
    .metric-card:hover { border-color:#30363d; }
    .metric-card-accent { position:absolute; bottom:0; left:0; right:0; height:3px; border-radius:0 0 14px 14px; }
    .metric-label { font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.08em; color:#64748b; margin-bottom:8px; }
    .metric-value { font-size:32px; font-weight:700; color:#f1f5f9; line-height:1; }
    .metric-icon  { position:absolute; top:1rem; right:1.2rem; font-size:22px; opacity:0.5; }

    .lead-card {
        background:#161b22; border:1px solid #21262d; border-radius:12px;
        padding:1rem 1.2rem; margin-bottom:0.6rem; border-left:3px solid #6366f1;
        transition:border-color 0.2s, background 0.2s;
    }
    .lead-card:hover { background:#1c2128; }
    .lead-card-cold        { border-left-color:#3b82f6; }
    .lead-card-warm        { border-left-color:#f59e0b; }
    .lead-card-hot         { border-left-color:#ef4444; }
    .lead-card-reactivated { border-left-color:#22c55e; }
    .lead-card-lost        { border-left-color:#475569; }
    .lead-name { font-size:15px; font-weight:600; color:#f1f5f9; }
    .lead-meta { font-size:12px; color:#64748b; margin-top:2px; }

    .badge { display:inline-flex; align-items:center; gap:4px; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; }
    .badge-cold        { background:rgba(59,130,246,0.15); color:#60a5fa; border:1px solid rgba(59,130,246,0.3); }
    .badge-warm        { background:rgba(245,158,11,0.15); color:#fbbf24; border:1px solid rgba(245,158,11,0.3); }
    .badge-hot         { background:rgba(239,68,68,0.15);  color:#f87171; border:1px solid rgba(239,68,68,0.3); }
    .badge-reactivated { background:rgba(34,197,94,0.15);  color:#4ade80; border:1px solid rgba(34,197,94,0.3); }
    .badge-lost        { background:rgba(71,85,105,0.15);  color:#94a3b8; border:1px solid rgba(71,85,105,0.3); }

    .channel-badge {
        display:inline-flex; align-items:center; gap:4px;
        background:rgba(99,102,241,0.12); border:1px solid rgba(99,102,241,0.25);
        color:#a5b4fc; padding:3px 9px; border-radius:20px; font-size:11px; font-weight:500;
    }

    .section-card { background:#161b22; border:1px solid #21262d; border-radius:14px; padding:1.4rem; margin-bottom:1rem; }
    .section-title { font-size:14px; font-weight:600; color:#94a3b8; text-transform:uppercase; letter-spacing:0.07em; margin-bottom:1rem; }

    .info-box {
        background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.2);
        border-radius:10px; padding:0.8rem 1rem; color:#a5b4fc; font-size:13px;
    }

    .stProgress > div > div { background:linear-gradient(90deg,#6366f1,#22d3ee) !important; border-radius:4px; }
    .stProgress > div { background:#21262d !important; border-radius:4px; }

    .stButton > button {
        background:linear-gradient(135deg,#6366f1,#4f46e5); color:white; border:none;
        border-radius:8px; font-weight:500; font-size:13px; padding:0.4rem 1rem;
        transition:opacity 0.2s, transform 0.1s;
    }
    .stButton > button:hover { opacity:0.9; transform:translateY(-1px); border:none; color:white; }
    .stButton > button:active { transform:translateY(0); }

    .stTabs [data-baseweb="tab-list"] {
        background:#161b22; border-radius:10px; padding:4px; gap:2px; border:1px solid #21262d;
    }
    .stTabs [data-baseweb="tab"] {
        background:transparent; color:#64748b; border-radius:7px; font-size:13px; font-weight:500; padding:6px 16px;
    }
    .stTabs [aria-selected="true"] { background:linear-gradient(135deg,#6366f1,#4f46e5) !important; color:white !important; }

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background:#0d1117 !important; border:1px solid #21262d !important;
        border-radius:8px !important; color:#e2e8f0 !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color:#6366f1 !important; box-shadow:0 0 0 2px rgba(99,102,241,0.2) !important;
    }

    hr { border-color:#21262d !important; margin:1.2rem 0 !important; }

    .footer { text-align:center; color:#334155; font-size:12px; padding:1rem 0 0.5rem 0; }
    .footer span {
        background:linear-gradient(90deg,#6366f1,#22d3ee);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-weight:600;
    }

    [data-testid="stChatMessage"] {
        background:#161b22 !important; border:1px solid #21262d !important;
        border-radius:12px !important; margin-bottom:0.5rem !important;
    }

    /* Chat input */
    [data-testid="stChatInput"] textarea {
        background:#161b22 !important; border:1px solid #21262d !important;
        border-radius:12px !important; color:#e2e8f0 !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color:#6366f1 !important; box-shadow:0 0 0 2px rgba(99,102,241,0.2) !important;
    }

    .streamlit-expanderHeader {
        background:#161b22 !important; border:1px solid #21262d !important;
        border-radius:10px !important; color:#94a3b8 !important;
    }
    .streamlit-expanderContent {
        background:#0d1117 !important; border:1px solid #21262d !important; border-top:none !important;
    }

    [data-testid="stMetric"] { background:#161b22; border:1px solid #21262d; border-radius:12px; padding:1rem; }
    [data-testid="stMetricLabel"] { color:#64748b !important; font-size:12px !important; }
    [data-testid="stMetricValue"] { color:#f1f5f9 !important; }

    [data-testid="stSidebar"] .stRadio > div { gap:4px; }
    [data-testid="stSidebar"] .stRadio label {
        background:transparent; border-radius:8px; padding:6px 10px;
        transition:background 0.15s; font-size:13px !important;
    }
    [data-testid="stSidebar"] .stRadio label:hover { background:rgba(99,102,241,0.1); }

    [data-testid="stSelectbox"] label { color:#94a3b8 !important; font-size:13px !important; }

    [data-testid="stFormSubmitButton"] > button {
        background:linear-gradient(135deg,#6366f1,#4f46e5) !important;
        color:white !important; border:none !important; border-radius:8px !important; font-weight:600 !important;
    }

    .stSpinner > div { border-top-color:#6366f1 !important; }
    .stCaption { color:#475569 !important; font-size:11px !important; }
    .stAlert { border-radius:10px !important; border:none !important; }

    /* Skeleton loader */
    .skeleton {
        background: linear-gradient(90deg, #161b22 25%, #1c2128 50%, #161b22 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 10px;
        height: 80px;
        margin-bottom: 0.6rem;
    }
    @keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }
    </style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-icon">📈</div>
        <div>
            <div class="sidebar-brand-text">ReactivaLeads</div>
            <div class="sidebar-brand-sub">CRM Inteligente</div>
        </div>
    </div>
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

st.sidebar.markdown("---")

# Health check
try:
    health = requests.get(f"{API_BASE_URL}/health", timeout=2)
    if health.status_code == 200:
        st.sidebar.markdown('<div class="api-status-ok">API Conectada</div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<div class="api-status-err">API No Responde</div>', unsafe_allow_html=True)
except:
    st.sidebar.markdown('<div class="api-status-err">API No Disponible</div>', unsafe_allow_html=True)
    st.sidebar.caption(f"URL: {API_BASE_URL}")

# Auto-refresh toggle + indicator
st.sidebar.markdown("---")
st.session_state.auto_refresh = st.sidebar.toggle("Auto-refresh (15s)", value=st.session_state.auto_refresh)
if st.session_state.auto_refresh:
    elapsed = int(time.time() - st.session_state.last_refresh)
    remaining = max(0, AUTO_REFRESH_INTERVAL - elapsed)
    st.sidebar.markdown(
        f'<div class="refresh-indicator"><div class="refresh-dot"></div>Actualiza en {remaining}s</div>',
        unsafe_allow_html=True
    )

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navegación",
    ["📊 Dashboard", "👥 Gestionar Leads", "💬 Conversaciones", "🚨 Escalaciones", "📈 Análisis"]
)

# ── Auto-refresh logic ────────────────────────────────────────────────────────
if st.session_state.auto_refresh and page == "📊 Dashboard":
    if time.time() - st.session_state.last_refresh >= AUTO_REFRESH_INTERVAL:
        st.session_state.last_refresh = time.time()
        st.cache_data.clear()
        st.rerun()

# ── Funciones auxiliares ──────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def get_api_stats():
    try:
        response = requests.get(f"{API_BASE_URL}/api/dashboard/stats", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error conectando con la API: {e}")
    return None

def get_leads(status="cold"):
    try:
        response = requests.get(f"{API_BASE_URL}/api/leads?status={status}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error obteniendo leads: {e}")
    return []

def create_lead(lead_data):
    try:
        response = requests.post(f"{API_BASE_URL}/api/leads", json=lead_data, timeout=5)
        return response
    except Exception as e:
        st.error(f"Error creando lead: {e}")
    return None

def initiate_reactivation(lead_id):
    try:
        response = requests.post(f"{API_BASE_URL}/api/leads/{lead_id}/reactivate", timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error iniciando reactivación: {e}")
    return None

def get_conversation(conversation_id):
    try:
        response = requests.get(f"{API_BASE_URL}/api/conversations/{conversation_id}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error obteniendo conversación: {e}")
    return None

def get_message(conversation_id):
    """Obtener historial de conversación"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/conversations/{conversation_id}/message", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error obteniendo mensaje de la conversacion: {e}")
    return None

def send_message(conversation_id, message):
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
    try:
        response = requests.get(f"{API_BASE_URL}/api/escalations?status={status}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error obteniendo escalaciones: {e}")
    return []

def format_status(status):
    status_map = {
        "cold":        ("❄️", "Frío",       "badge-cold"),
        "warm":        ("🔥", "Tibio",      "badge-warm"),
        "hot":         ("⚡", "Caliente",   "badge-hot"),
        "reactivated": ("✅", "Reactivado", "badge-reactivated"),
        "lost":        ("💀", "Perdido",    "badge-lost"),
    }
    icon, text, css = status_map.get(status, ("", status, "badge-lost"))
    return f'<span class="badge {css}">{icon} {text}</span>'

def format_channel(channel):
    channel_map = {
        "telegram": "✈️ Telegram",
        "email":    "📧 Email",
        "api":      "🔌 API",
        "whatsapp": "💬 WhatsApp"
    }
    return channel_map.get(channel, channel)

def metric_card(label, value, icon, accent_color):
    return f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-card-accent" style="background:{accent_color};"></div>
    </div>
    """

def lead_card_class(status):
    return {
        "cold": "lead-card-cold", "warm": "lead-card-warm",
        "hot": "lead-card-hot", "reactivated": "lead-card-reactivated", "lost": "lead-card-lost",
    }.get(status, "")

def skeleton_loader(n=3):
    return "".join(['<div class="skeleton"></div>' for _ in range(n)])


# ============ PÁGINA: DASHBOARD ============
if page == "📊 Dashboard":
    col_title, col_refresh = st.columns([5, 1])
    with col_title:
        st.markdown("""
            <div class="page-header">
                <div class="page-title">📊 Dashboard</div>
                <div class="page-subtitle">Resumen en tiempo real del sistema de reactivación</div>
            </div>
        """, unsafe_allow_html=True)
    with col_refresh:
        if st.button("🔄 Actualizar"):
            st.session_state.last_refresh = time.time()
            st.cache_data.clear()
            st.rerun()

    with st.spinner("Cargando estadísticas..."):
        stats = get_api_stats()

    if stats:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(metric_card("Leads Fríos",    stats.get("cold_leads", 0),         "❄️", "#3b82f6"), unsafe_allow_html=True)
        with col2:
            st.markdown(metric_card("Leads Tibios",   stats.get("warm_leads", 0),         "🔥", "#f59e0b"), unsafe_allow_html=True)
        with col3:
            st.markdown(metric_card("Leads Calientes",stats.get("hot_leads", 0),          "⚡", "#ef4444"), unsafe_allow_html=True)
        with col4:
            st.markdown(metric_card("Reactivados",    stats.get("reactivated_leads", 0),  "✅", "#22c55e"), unsafe_allow_html=True)
        with col5:
            st.markdown(metric_card("Escalaciones",   stats.get("pending_escalations", 0),"🚨", "#a855f7"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="section-card"><div class="section-title">Distribución de Leads</div>', unsafe_allow_html=True)
            data = pd.DataFrame({
                "Estado":   ["Fríos", "Tibios", "Calientes", "Reactivados"],
                "Cantidad": [stats.get("cold_leads",0), stats.get("warm_leads",0),
                             stats.get("hot_leads",0),  stats.get("reactivated_leads",0)]
            })
            st.bar_chart(data.set_index("Estado"))
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="section-card"><div class="section-title">Información del Agente</div>', unsafe_allow_html=True)
            try:
                response = requests.get(f"{API_BASE_URL}/api/agent/info", timeout=5)
                if response.status_code == 200:
                    agent_info = response.json()
                    st.write(f"*Modelo LLM:* {agent_info.get('model', 'N/A')}")
                    st.write(f"*Timeout:* {agent_info.get('timeout', 'N/A')}s")
                    st.write(f"*Máx. Turnos:* {agent_info.get('max_turns', 'N/A')}")
                    if 'tools' in agent_info:
                        st.write(f"*Tools Disponibles:* {len(agent_info['tools'])}")
                        with st.expander("Ver tools"):
                            for tool in agent_info['tools']:
                                st.write(f"- {tool}")
            except:
                st.warning("No se pudo obtener información del agente")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        total      = stats.get("total_leads", 1)
        reactivated = stats.get("reactivated_leads", 0)
        if total > 0:
            rate = (reactivated / total) * 100
            st.markdown(f"""
                <div class="section-card">
                    <div class="section-title">Tasa de Reactivación Global</div>
                    <div style="font-size:36px;font-weight:700;color:#f1f5f9;margin-bottom:0.8rem;">{rate:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
            st.progress(rate / 100)
    else:
        st.markdown(skeleton_loader(5), unsafe_allow_html=True)
        st.markdown('<div class="info-box">⚠️ No se pudieron cargar las estadísticas. Verifica que la API esté activa.</div>', unsafe_allow_html=True)


# ============ PÁGINA: GESTIONAR LEADS ============
elif page == "👥 Gestionar Leads":
    st.markdown("""
        <div class="page-header">
            <div class="page-title">👥 Gestionar Leads</div>
            <div class="page-subtitle">Visualiza, crea y gestiona tus leads</div>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 Ver Leads", "➕ Crear Lead", "🔍 Buscar Lead"])

    with tab1:
        # ── Filtros combinados ────────────────────────────────────────────────
        fc1, fc2, fc3, fc4 = st.columns([3, 2, 2, 2])
        with fc1:
            search_query = st.text_input("🔍 Buscar por nombre o email", value=st.session_state.leads_search,
                                         placeholder="Ej: Juan o juan@empresa.com")
            st.session_state.leads_search = search_query
        with fc2:
            status_filter = st.selectbox(
                "Estado",
                ["cold", "warm", "hot", "reactivated", "lost"],
                format_func=lambda x: {"cold":"❄️ Fríos","warm":"🔥 Tibios","hot":"⚡ Calientes",
                                        "reactivated":"✅ Reactivados","lost":"💀 Perdidos"}[x]
            )
        with fc3:
            channel_filter = st.selectbox(
                "Canal",
                ["all", "telegram", "email", "api", "whatsapp"],
                format_func=lambda x: "🌐 Todos" if x == "all" else format_channel(x),
                index=["all","telegram","email","api","whatsapp"].index(st.session_state.leads_channel_filter)
            )
            st.session_state.leads_channel_filter = channel_filter
        with fc4:
            sort_option = st.selectbox(
                "Ordenar por",
                ["value_desc", "value_asc", "name_asc"],
                format_func=lambda x: {"value_desc":"💰 Valor (mayor)", "value_asc":"💰 Valor (menor)", "name_asc":"🔤 Nombre A-Z"}[x],
                index=["value_desc","value_asc","name_asc"].index(st.session_state.leads_sort)
            )
            st.session_state.leads_sort = sort_option

        with st.spinner("Cargando leads..."):
            leads = get_leads(status_filter)

        # Aplicar filtros locales
        if search_query:
            q = search_query.lower()
            leads = [l for l in leads if q in l.get("name","").lower() or q in l.get("email","").lower()]
        if channel_filter != "all":
            leads = [l for l in leads if l.get("preferred_channel") == channel_filter]

        # Ordenamiento
        if sort_option == "value_desc":
            leads = sorted(leads, key=lambda l: l.get("value", 0), reverse=True)
        elif sort_option == "value_asc":
            leads = sorted(leads, key=lambda l: l.get("value", 0))
        elif sort_option == "name_asc":
            leads = sorted(leads, key=lambda l: l.get("name", "").lower())

        if leads:
            st.markdown(f'<div class="info-box">Se encontraron <strong>{len(leads)}</strong> leads</div><br>', unsafe_allow_html=True)
            for lead in leads[:20]:
                css_class = lead_card_class(lead.get('status', 'cold'))
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                with col1:
                    st.markdown(f"""
                        <div class="lead-card {css_class}">
                            <div class="lead-name">{lead.get('name','N/A')}</div>
                            <div class="lead-meta">📧 {lead.get('email','N/A')}</div>
                            {"<div class='lead-meta'>📱 " + lead['phone'] + "</div>" if lead.get('phone') else ""}
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                        <div style="padding-top:0.6rem;">
                            {"<div style='color:#94a3b8;font-size:13px;'>🏢 " + lead['company'] + "</div>" if lead.get('company') else ""}
                            <div style='color:#64748b;font-size:12px;margin-top:4px;'>💰 ${lead.get('value',0):,.0f}</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                        <div style="padding-top:0.6rem;">
                            {format_status(lead.get('status','cold'))}
                            <div style="margin-top:6px;">
                                <span class="channel-badge">{format_channel(lead.get('preferred_channel','api'))}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                with col4:
                    if lead.get('status') == 'cold':
                        if st.button("⚡ Reactivar", key=f"reactivate_{lead['id']}"):
                            with st.spinner("Iniciando reactivación..."):
                                result = initiate_reactivation(lead['id'])
                                if result and result.get("success"):
                                    st.success("✅ Reactivación iniciada")
                                    with st.expander("Ver respuesta del agente"):
                                        st.write(result.get('agent_response', ''))
                st.markdown("<hr>", unsafe_allow_html=True)
        else:
            st.markdown(skeleton_loader(3), unsafe_allow_html=True)
            st.markdown('<div class="info-box">No se encontraron leads con esos filtros.</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="section-card"><div class="section-title">Nuevo Lead</div>', unsafe_allow_html=True)
        with st.form("create_lead_form"):
            col1, col2 = st.columns(2)
            with col1:
                name  = st.text_input("Nombre del Lead *")
                email = st.text_input("Email *")
                phone = st.text_input("Teléfono")
            with col2:
                company   = st.text_input("Empresa")
                value     = st.number_input("Valor Estimado ($)", min_value=0, value=5000)
                preferred_channel = st.selectbox("Canal Preferido *", ["telegram","email","api","whatsapp"], format_func=format_channel)
            status    = st.selectbox("Estado Inicial", ["cold","warm","hot"])
            notes     = st.text_area("Notas")
            submitted = st.form_submit_button("➕ Crear Lead", use_container_width=True)
            if submitted:
                if not name or not email:
                    st.error("⚠️ Nombre y email son obligatorios")
                else:
                    lead_data = {"name":name,"email":email,"phone":phone,"company":company,
                                 "value":value,"notes":notes,"status":status,"preferred_channel":preferred_channel}
                    response = create_lead(lead_data)
                    if response and response.status_code == 200:
                        st.success("✅ Lead creado exitosamente")
                        st.balloons()
                    else:
                        st.error("❌ Error creando lead")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="section-card"><div class="section-title">Buscar Lead</div>', unsafe_allow_html=True)
        search_type = st.radio("Buscar por:", ["ID", "Email"])
        if search_type == "ID":
            lead_id = st.number_input("ID del Lead", min_value=1)
            if st.button("🔍 Buscar"):
                response = requests.get(f"{API_BASE_URL}/api/leads/{lead_id}")
                if response.status_code == 200:
                    st.json(response.json())
                else:
                    st.error("No encontrado")
        st.markdown('</div>', unsafe_allow_html=True)


# ============ PÁGINA: CONVERSACIONES ============
elif page == "💬 Conversaciones":
    st.markdown("""
        <div class="page-header">
            <div class="page-title">💬 Conversaciones Activas</div>
            <div class="page-subtitle">Historial y gestión de conversaciones con leads</div>
        </div>
    """, unsafe_allow_html=True)

    col_id, col_btn = st.columns([3, 1])
    with col_id:
        conversation_id = st.number_input("ID de Conversación", min_value=1, value=st.session_state.active_conv_id or 1)
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        load_btn = st.button("📂 Cargar")

    if load_btn:
        with st.spinner("Cargando conversación..."):
            conv_data = get_conversation(conversation_id)
            # Cargar mensajes desde el endpoint dedicado
            try:
                msg_response = requests.get(
                    f"{API_BASE_URL}/api/conversations/{conversation_id}/message", timeout=5
                )
                raw_messages = msg_response.json() if msg_response.status_code == 200 else []
            except Exception:
                raw_messages = []

        if conv_data:
            st.session_state.active_conv_id = conversation_id
            # Normalizar roles: "agent" -> "assistant", "lead" -> "user"
            role_map = {"agent": "assistant", "lead": "user", "assistant": "assistant", "user": "user"}
            normalized = [
                {"role": role_map.get(m.get("role", "user"), "user"), "content": m.get("content", "")}
                for m in (raw_messages if isinstance(raw_messages, list) else [])
            ]
            st.session_state.chat_messages[conversation_id] = normalized
            st.markdown(f"""
                <div class="info-box">
                    <strong>Lead ID:</strong> {conv_data.get('lead_id')} &nbsp;|&nbsp;
                    <strong>Estado:</strong> {conv_data.get('status')} &nbsp;|&nbsp;
                    <strong>Mensajes:</strong> {len(normalized)}
                </div><br>
            """, unsafe_allow_html=True)
        else:
            st.markdown(skeleton_loader(2), unsafe_allow_html=True)

    # Mostrar chat si hay conversación activa
    active_id = st.session_state.active_conv_id
    if active_id and active_id in st.session_state.chat_messages:
        messages = st.session_state.chat_messages[active_id]

        chat_container = st.container()
        with chat_container:
            if messages:
                for msg in messages:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])
            else:
                st.markdown('<div class="info-box">💬 No hay mensajes aún en esta conversación.</div>', unsafe_allow_html=True)

        # Chat input persistente
        if user_input := st.chat_input("Escribe la respuesta del lead..."):
            # Mostrar mensaje del usuario inmediatamente
            st.session_state.chat_messages[active_id].append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)

            # Enviar y mostrar respuesta del agente
            with st.chat_message("assistant"):
                with st.spinner("El agente está respondiendo..."):
                    result = send_message(active_id, user_input)
                if result:
                    agent_reply = result.get("agent_response", result.get("message", ""))
                    st.write(agent_reply)
                    st.session_state.chat_messages[active_id].append({"role": "assistant", "content": agent_reply})
                else:
                    st.error("No se pudo obtener respuesta del agente")


# ============ PÁGINA: ESCALACIONES ============
elif page == "🚨 Escalaciones":
    st.markdown("""
        <div class="page-header">
            <div class="page-title">🚨 Casos Escalados</div>
            <div class="page-subtitle">Gestión de casos que requieren atención humana</div>
        </div>
    """, unsafe_allow_html=True)

    status_filter = st.selectbox("Filtrar por estado", ["pending","assigned","in_progress","resolved"])

    with st.spinner("Cargando escalaciones..."):
        escalations = get_escalations(status_filter)

    if escalations:
        for esc in escalations:
            with st.expander(f"🚨 Caso #{esc['id']} — Lead: {esc['lead_id']}"):
                st.write(f"*Razón:* {esc.get('reason')}")
                st.write(f"*Asignado a:* {esc.get('assigned_to', 'Sin asignar')}")
    else:
        st.markdown(skeleton_loader(2), unsafe_allow_html=True)
        st.markdown('<div class="info-box">✅ No hay casos escalados con ese estado.</div>', unsafe_allow_html=True)


# ============ PÁGINA: ANÁLISIS ============
elif page == "📈 Análisis":
    st.markdown("""
        <div class="page-header">
            <div class="page-title">📈 Análisis y Reportes</div>
            <div class="page-subtitle">Métricas de rendimiento del sistema</div>
        </div>
    """, unsafe_allow_html=True)

    with st.spinner("Cargando análisis..."):
        stats = get_api_stats()

    if stats:
        total_leads = stats.get("total_leads", 1)
        reactivated = stats.get("reactivated_leads", 0)
        rate = (reactivated / total_leads) * 100

        st.markdown(f"""
            <div class="section-card">
                <div class="section-title">Tasa de Reactivación Global</div>
                <div style="font-size:42px;font-weight:700;color:#f1f5f9;margin-bottom:0.8rem;">{rate:.1f}%</div>
                <div style="color:#64748b;font-size:13px;">{reactivated} de {total_leads} leads reactivados</div>
            </div>
        """, unsafe_allow_html=True)
        st.progress(rate / 100)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-card"><div class="section-title">Distribución por Estado</div>', unsafe_allow_html=True)
        data = pd.DataFrame({
            "Estado":   ["Fríos","Tibios","Calientes","Reactivados"],
            "Cantidad": [stats.get("cold_leads",0), stats.get("warm_leads",0),
                         stats.get("hot_leads",0),  stats.get("reactivated_leads",0)]
        })
        st.bar_chart(data.set_index("Estado"))
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(skeleton_loader(3), unsafe_allow_html=True)
        st.markdown('<div class="info-box">⚠️ No se pudieron cargar los datos de análisis.</div>', unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
    <div class="footer">
        Sistema de Reactivación de Leads &nbsp;|&nbsp;
        Powered by <span>LangChain + FastAPI + Streamlit</span>
    </div>
""", unsafe_allow_html=True)

# ── Auto-refresh trigger (al final para no bloquear render) ───────────────────
if st.session_state.auto_refresh and page == "📊 Dashboard":
    time.sleep(1)
    st.rerun()