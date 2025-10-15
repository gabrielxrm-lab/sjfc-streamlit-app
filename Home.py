# Home.py
import streamlit as st
import data_manager
import streamlit.components.v1 as components
from datetime import datetime
import locale
import sidebar # Importa o novo arquivo da barra lateral

# Configurações da página e CSS
st.set_page_config(page_title="Central do São Jorge FC", page_icon="logo_sao_jorge.png", layout="wide")
st.markdown("""<style> [data-testid="stSidebarNav"] > ul {display: none;} section[data-testid="stSidebar"] {width: 300px; position: fixed; height: 100%; top: 0; left: 0;} .main .block-container {display: flex; flex-direction: column; align-items: center; text-align: center;} #birthday-cards [data-testid="stVerticalBlockBorderWrapper"] {max-width: 220px; margin: 0 auto;} .birthday-day {font-size: 2.5rem; font-weight: bold; color: #1E88E5; line-height: 1; margin-bottom: 10px;} </style>""", unsafe_allow_html=True)

# Cria a barra lateral a partir da função centralizada
sidebar.create_sidebar()

# Inicializa os dados
data_manager.initialize_session_state()

# --- PÁGINA PRINCIPAL ---
# (O conteúdo da página principal continua o mesmo, foi omitido para encurtar)
# ...
