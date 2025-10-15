# Home.py
import streamlit as st
import data_manager
import os
import streamlit.components.v1 as components
from datetime import datetime
import locale

try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error:
    pass

st.set_page_config(page_title="Central do São Jorge FC", page_icon="logo_sao_jorge.png", layout="wide")

st.markdown(
    """<style>
        section[data-testid="stSidebar"] {width: 300px; position: fixed; height: 100%; top: 0; left: 0;}
        .main .block-container {display: flex; flex-direction: column; align-items: center; text-align: center;}
    </style>""",
    unsafe_allow_html=True,
)

def handle_profile_selection():
    if 'role' not in st.session_state: st.session_state.role = 'Jogador'
    st.sidebar.title("Perfil de Acesso")
    profile = st.sidebar.radio("Selecione seu perfil:", ('Jogador', 'Diretoria'), index=0 if st.session_state.role == 'Jogador' else 1)
    if profile == 'Diretoria':
        if st.session_state.role == 'Diretoria':
            st.sidebar.success("Logado como Diretoria.")
            if st.sidebar.button("Sair do modo Edição"): st.session_state.role = 'Jogador'; st.rerun()
        else:
            password = st.sidebar.text_input("Senha da Diretoria:", type="password")
            if st.sidebar.button("Entrar como Diretoria"):
                creds = st.secrets.get("credentials", {}); correct_password = creds.get("diretoria_password")
                if correct_password and password == correct_password: st.session_state.role = 'Diretoria'; st.rerun()
                else: st.sidebar.error("Senha incorreta ou não configurada.")
    else:
        if st.session_state.role == 'Diretoria': st.session_state.role = 'Jogador'; st.rerun()
        else: st.session_state.role = 'Jogador'

handle_profile_selection()
data_manager.initialize_session_state()
IS_DIRETORIA = st.session_state.get('role') == 'Diretoria'

with st.sidebar:
    st.write("---")
    
    # --- NAVEGAÇÃO MANUAL E CONDICIONAL ---
    st.page_link("Home.py", label="Página Principal", icon="🏠")
    st.page_link("pages/1_⚽_Gerenciar_Jogadores.py", label="Gerenciar Jogadores", icon="⚽")
    if IS_DIRETORIA:
        st.page_link("pages/2_💲_Mensalidades.py", label="Mensalidades", icon="💲")
    st.page_link("pages/3_📋_Nova_Súmula.py", label="Nova Súmula", icon="📋")
    st.page_link("pages/4_🎲_Sorteio_de_Times.py", label="Sorteio de Times", icon="🎲")
    st.page_link("pages/5_🏆_Ranking.py", label="Ranking", icon="🏆")

    st.write("---")
    logo_path = "logo_sao_jorge.png"
    if os.path.exists(logo_path): st.image(logo_path, width=150)
    st.title("São Jorge FC"); st.write("---"); st.caption("Desenvolvido por:")
    st.markdown("**Gabriel Conrado**"); st.caption("📱 (21) 97275-7256")

# --- O resto da página principal (sem alterações) ---
# ...
