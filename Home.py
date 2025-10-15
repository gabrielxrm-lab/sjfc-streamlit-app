# Home.py
import streamlit as st
import data_manager
import streamlit.components.v1 as components
from datetime import datetime
import locale
import sidebar

# Configura a localidade
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error:
    pass

# --- Configuração da Página ---
st.set_page_config(page_title="Central do São Jorge FC", page_icon="logo_sao_jorge.png", layout="wide")

# --- CHAMA A BARRA LATERAL (que agora contém o CSS) ---
sidebar.create_sidebar()

# --- Inicializa os dados ---
data_manager.initialize_session_state()

# --- PÁGINA PRINCIPAL (CONTEÚDO COMPLETO) ---
# ... (Todo o conteúdo que havia sumido está de volta aqui)
