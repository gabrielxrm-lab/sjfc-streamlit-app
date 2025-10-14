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

# --- CSS para Fixar a Barra Lateral ---
st.markdown(
    """<style> section[data-testid="stSidebar"] {width: 300px; position: fixed; height: 100%; top: 0; left: 0;} </style>""",
    unsafe_allow_html=True,
)

# --- Lógica de Perfil e Login ---
def handle_profile_selection():
    if 'role' not in st.session_state: st.session_state.role = 'Visitante'
    st.sidebar.title("Perfil de Acesso")
    profile = st.sidebar.radio("Selecione seu perfil:", ('Visitante', 'Diretoria'), index=0 if st.session_state.role == 'Visitante' else 1)
    if profile == 'Diretoria':
        if st.session_state.role == 'Diretoria':
            st.sidebar.success("Logado como Diretoria.")
            if st.sidebar.button("Sair do modo Edição"): st.session_state.role = 'Visitante'; st.rerun()
        else:
            password = st.sidebar.text_input("Senha da Diretoria:", type="password")
            if st.sidebar.button("Entrar como Diretoria"):
                creds = st.secrets.get("credentials", {}); correct_password = creds.get("diretoria_password")
                if correct_password and password == correct_password: st.session_state.role = 'Diretoria'; st.rerun()
                else: st.sidebar.error("Senha incorreta ou não configurada.")
    else:
        if st.session_state.role == 'Diretoria': st.session_state.role = 'Visitante'; st.rerun()
        else: st.session_state.role = 'Visitante'

handle_profile_selection()
data_manager.initialize_session_state()

# --- Barra Lateral (Restante) ---
with st.sidebar:
    st.write("---"); logo_path = "logo_sao_jorge.png"
    if os.path.exists(logo_path): st.image(logo_path, width=150)
    st.title("São Jorge FC"); st.write("---"); st.caption("Desenvolvido por:")
    st.markdown("**Gabriel Conrado**"); st.caption("📱 (21) 97275-7256")

# --- PÁGINA PRINCIPAL ---
now = datetime.now()
month_map_pt = {1:"Janeiro", 2:"Fevereiro", 3:"Março", 4:"Abril", 5:"Maio", 6:"Junho", 7:"Julho", 8:"Agosto", 9:"Setembro", 10:"Outubro", 11:"Novembro", 12:"Dezembro"}
current_month_name = month_map_pt.get(now.month, "")
st.header(f"🎂 Aniversariantes de {current_month_name}")

players = st.session_state.dados.get('players', [])
birthday_players = []
for player in players:
    dob_str = player.get('date_of_birth')
    if dob_str and len(dob_str.split('/')) == 3:
        try:
            dob_date = datetime.strptime(dob_str, "%d/%m/%Y")
            if dob_date.month == now.month: birthday_players.append(player)
        except ValueError: continue
birthday_players.sort(key=lambda p: datetime.strptime(p.get('date_of_birth'), "%d/%m/%Y").day)

if not birthday_players:
    st.info("Nenhum aniversariante este mês.")
else:
    num_columns = 4
    cols = st.columns(num_columns)
    for i, player in enumerate(birthday_players):
        with cols[i % num_columns]:
            with st.container(border=True):
                st.subheader(player['name'])
                image_url = data_manager.get_github_image_url(player.get('photo_file'))
                
                # --- CORREÇÃO APLICADA AQUI ---
                st.image(image_url, use_column_width='auto')
                
                dob = datetime.strptime(player.get('date_of_birth'), "%d/%m/%Y")
                st.caption(f"Dia {dob.strftime('%d')}")
                if player.get('shirt_number'): st.markdown(f"**Camisa: {player.get('shirt_number')}**")
st.write("---")

col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.image("logo_sao_jorge.png", width=60)
with col2:
    st.title("Central de Dados do São Jorge FC")

if st.session_state.role == 'Diretoria': st.markdown("##### 🔑 Você está no modo **Diretoria**.")
else: st.markdown("##### 👁️ Você está no modo **Visitante**.")
st.write("---")

st.header("⏳ Próximo Jogo")
# (O código do contador foi omitido para encurtar a resposta)
countdown_html="..."
components.html(countdown_html, height=150)

st.write("---")
st.header("🖼️ Galeria do Time")
# (O código do carrossel foi omitido para encurtar a resposta)
slideshow_html="..."
components.html(slideshow_html, height=450)
st.write("---")
st.info("Use o menu na barra lateral para navegar. Para editar, selecione o perfil 'Diretoria' e insira a senha.")
