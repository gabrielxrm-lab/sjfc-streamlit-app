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
        /* ATUALIZAÇÃO: Aumenta o tamanho do número do dia */
        .birthday-day {
            font-size: 3.5rem;      /* Aumentado de 2.5rem para 3.5rem */
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

# --- Barra Lateral (Restante) ---
with st.sidebar:
    st.write("---")
    # O menu de navegação foi movido para o arquivo sidebar.py
    # Se precisar adicionar/remover páginas, edite lá.

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

if st.session_state.role == 'Diretoria':
    st.markdown("<h5 style='text-align: center;'>🔑 Você está no modo Diretoria.</h5>", unsafe_allow_html=True)
else:
    st.markdown("<h5 style='text-align: center;'>👁️ Você está no modo Jogador.</h5>", unsafe_allow_html=True)
st.write("---")

# --- SEÇÃO: ANIVERSARIANTES DO MÊS ---
now = datetime.now()
month_map_pt = {1:"Janeiro", 2:"Fevereiro", 3:"Março", 4:"Abril", 5:"Maio", 6:"Junho", 7:"Julho", 8:"Agosto", 9:"Setembro", 10:"Outubro", 11:"Novembro", 12:"Dezembro"}
current_month_name = month_map_pt.get(now.month, "")
st.header(f"🎂 Aniversariantes de {current_month_name}")

players = st.session_state.dados.get('players', [])
birthday_players = [p for p in players if p.get('date_of_birth') and len(p.get('date_of_birth').split('/')) == 3 and (datetime.strptime(p.get('date_of_birth'), "%d/%m/%Y").month == now.month)]
birthday_players.sort(key=lambda p: datetime.strptime(p.get('date_of_birth'), "%d/%m/%Y").day)

if not birthday_players:
    st.info("Nenhum aniversariante este mês.")
else:
    st.markdown('<div id="birthday-cards">', unsafe_allow_html=True)
    num_columns = min(len(birthday_players), 4)
    cols = st.columns(num_columns)
    for i, player in enumerate(birthday_players):
        with cols[i % num_columns]:
            with st.container(border=True):
                st.subheader(player['name'])
                image_url = data_manager.get_github_image_url(player.get('photo_file'))
                st.image(image_url, use_container_width=True)
                dob = datetime.strptime(player.get('date_of_birth'), "%d/%m/%Y")
                day_str = dob.strftime('%d')
                st.caption("Dia")
                st.markdown(f"<p class='birthday-day'>{day_str}</p>", unsafe_allow_html=True)
                if player.get('shirt_number'): st.markdown(f"**Camisa: {player.get('shirt_number')}**")
    st.markdown('</div>', unsafe_allow_html=True)
st.write("---")

# --- CONTADOR E CARROSSEL ---
st.header("⏳ Próximo Jogo")
countdown_html = """ ... """ # Omitido para encurtar
components.html(countdown_html, height=150)
st.write("---")
st.header("🖼️ Galeria do Time")
slideshow_html = """ ... """ # Omitido
components.html(slideshow_html, height=450)
st.write("---")
st.info("Use o menu na barra lateral para navegar. Para editar, selecione o perfil 'Diretoria' e insira a senha.")
