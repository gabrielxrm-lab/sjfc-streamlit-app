# Home.py
import streamlit as st
import data_manager
import os
import streamlit.components.v1 as components
from datetime import datetime
import locale

# Configura a localidade para português, com um fallback
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error:
    pass

# --- Configuração da Página ---
st.set_page_config(
    page_title="Central do São Jorge FC",
    page_icon="logo_sao_jorge.png",
    layout="wide"
)

# --- CSS para Estilos da Página ---
st.markdown(
    """
    <style>
        /* Fixa a barra lateral */
        section[data-testid="stSidebar"] {
            width: 300px;
            position: fixed;
            height: 100%;
            top: 0;
            left: 0;
        }
        /* Centraliza o conteúdo da página principal */
        .main .block-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
        }
        /* Ajusta os cards de aniversariante */
        #birthday-cards [data-testid="stVerticalBlockBorderWrapper"] {
            max-width: 220px;
            margin: 0 auto;
        }
        .birthday-day {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1E88E5;
            line-height: 1;
            margin-bottom: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Lógica de Perfil e Login ---
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

# --- Barra Lateral (Restante) ---
with st.sidebar:
    st.write("---")
    st.page_link("Home.py", label="Página Principal", icon="🏠")
    st.page_link("pages/1_Gerenciar_Jogadores.py", label="Gerenciar Jogadores", icon="⚽")
    if IS_DIRETORIA:
        st.page_link("pages/2_Mensalidades.py", label="Mensalidades", icon="💲")
    st.page_link("pages/Nova_Súmula.py", label="Nova Súmula", icon="📋")
    st.page_link("pages/sorteio_de_times.py", label="Sorteio de Times", icon="🎲")
    st.page_link("pages/Ranking.py", label="Ranking", icon="🏆")

    st.write("---")
    logo_path = "logo_sao_jorge.png"
    if os.path.exists(logo_path): st.image(logo_path, width=150)
    st.title("São Jorge FC"); st.write("---"); st.caption("Desenvolvido por:")
    st.markdown("**Gabriel Conrado**"); st.caption("📱 (21) 97275-7256")


# --- PÁGINA PRINCIPAL ---

# --- TÍTULO CENTRALIZADO (COM URL DO LOGO CORRIGIDA) ---
logo_url = f"https://raw.githubusercontent.com/{data_manager.GITHUB_USER}/{data_manager.GITHUB_REPO}/main/logo_sao_jorge.png"
st.markdown(f"""
    <div style="text-align: center;">
        <img src="{logo_url}" alt="Logo SJFC" width="80">
        <h1 style="font-weight:bold; margin-bottom:0px;">Central de Dados do São Jorge FC</h1>
        <p style="margin-top:0px; font-size:1.2rem; color: #D3D3D3;">DESDE 1980</p>
    </div>
""", unsafe_allow_html=True)
# ... (o resto do arquivo, sem alterações)
