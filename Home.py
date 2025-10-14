# Home.py
import streamlit as st
import data_manager
import os
import streamlit.components.v1 as components
from datetime import datetime

# --- Configuração da Página ---
st.set_page_config(
    page_title="Central do São Jorge FC",
    page_icon="logo_sao_jorge.png",
    layout="wide"
)

# --- CSS para Fixar a Barra Lateral ---
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 300px;
            position: fixed;
            height: 100%;
            top: 0;
            left: 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- LÓGICA DE PERFIL E LOGIN ---
def handle_profile_selection():
    if 'role' not in st.session_state: st.session_state.role = 'Visitante'
    st.sidebar.title("Perfil de Acesso")
    profile = st.sidebar.radio("Selecione seu perfil:", ('Visitante', 'Diretoria'), index=0 if st.session_state.role == 'Visitante' else 1)
    if profile == 'Diretoria':
        if st.session_state.role == 'Diretoria':
            st.sidebar.success(f"Logado como Diretoria.")
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

# --- Roda a lógica de perfil e inicializa os dados ---
handle_profile_selection()
data_manager.initialize_session_state()

# --- Barra Lateral (Restante) ---
with st.sidebar:
    st.write("---"); logo_path = "logo_sao_jorge.png"
    if os.path.exists(logo_path): st.image(logo_path, width=150)
    st.title("São Jorge FC"); st.write("---"); st.caption("Desenvolvido por:")
    st.markdown("**Gabriel Conrado**"); st.caption("📱 (21) 97140-0676")


# --- PÁGINA PRINCIPAL ---

# --- NOVA SEÇÃO: ANIVERSARIANTES DO MÊS ---
st.header("🎂 Aniversariantes do Mês")

# Pega o mês atual
current_month = datetime.now().month
players = st.session_state.dados.get('players', [])
birthday_players = []

for player in players:
    dob_str = player.get('date_of_birth')
    if dob_str:
        try:
            # Tenta converter a data de nascimento para objeto datetime
            dob_date = datetime.strptime(dob_str, "%d/%m/%Y")
            if dob_date.month == current_month:
                birthday_players.append(player)
        except ValueError:
            # Ignora datas em formato inválido
            continue

# Ordena os aniversariantes pelo dia
birthday_players.sort(key=lambda p: datetime.strptime(p.get('date_of_birth'), "%d/%m/%Y").day)

if not birthday_players:
    st.info("Nenhum aniversariante este mês.")
else:
    # Cria colunas para cada aniversariante (até 4 por linha)
    cols = st.columns(len(birthday_players))
    for i, player in enumerate(birthday_players):
        with cols[i]:
            with st.container(border=True):
                st.subheader(player['name'])
                
                image_url = data_manager.get_github_image_url(player.get('photo_file'))
                st.image(image_url, use_column_width=True)
                
                dob = datetime.strptime(player.get('date_of_birth'), "%d/%m/%Y")
                st.caption(f"Aniversário: {dob.strftime('%d/%m')}")

st.write("---")

# --- SEÇÃO DO TÍTULO ---
st.title("🛡️ Central de Dados do São Jorge FC")
if st.session_state.role == 'Diretoria':
    st.markdown("##### 🔑 Você está no modo **Diretoria**.")
else:
    st.markdown("##### 👁️ Você está no modo **Visitante**.")
st.write("---")

# --- CONTADOR REGRESSIVO ---
st.header("⏳ Próximo Jogo")
# (O código do contador continua aqui, sem alterações)
countdown_html = """ ... """ # Omitido para encurtar, mas está no seu código
components.html(countdown_html, height=150)

st.write("---")

# --- NOVA SEÇÃO: CARROSSEL DE FOTOS DO TIME ---
st.header("🖼️ Galeria do Time")

# IMPORTANTE: EDITE ESTA LISTA COM AS SUAS URLs
image_urls = [
    "https://raw.githubusercontent.com/gabrielxrm-lab/sjfc-streamlit-app/15f9ded2ab39af7dab782c27e6f164022169cf43/player_photos/slideshow/20250817_075933.jpg",
    "https://raw.githubusercontent.com/gabrielxrm-lab/sjfc-streamlit-app/main/player_photos/slideshow/20250817_080001.jpg",
    "https://raw.githubusercontent.com/gabrielxrm-lab/sjfc-streamlit-app/main/player_photos/slideshow/20250817_085832.jpg",
    "https://raw.githubusercontent.com/gabrielxrm-lab/sjfc-streamlit-app/main/player_photos/slideshow/20250817_085914.jpg",
    "https://raw.githubusercontent.com/gabrielxrm-lab/sjfc-streamlit-app/main/player_photos/slideshow/20250817_085945.jpg"
]

image_tags = "".join([f'<img class="slide" src="{url}">' for url in image_urls])
slideshow_html = f"""
<style>
    .slideshow-container {{ position: relative; width: 100%; height: 450px; overflow: hidden; border-radius: 10px; }}
    .slide {{ position: absolute; width: 100%; height: 100%; object-fit: cover; opacity: 0; transition: opacity 1.5s ease-in-out; }}
    .slide.active {{ opacity: 1; }}
</style>
<div class="slideshow-container">{image_tags}</div>
<script>
    let slideIndex = 0;
    const slides = document.getElementsByClassName("slide");
    function showSlides() {{
        for (let i = 0; i < slides.length; i++) {{ slides[i].classList.remove("active"); }}
        slideIndex++;
        if (slideIndex > slides.length) {{slideIndex = 1}}
        slides[slideIndex - 1].classList.add("active");
        setTimeout(showSlides, 5000); // Muda a imagem a cada 5 segundos
    }}
    if (slides.length > 0) {{
        slides[0].classList.add("active");
        setTimeout(showSlides, 5000);
    }}
</script>
"""
components.html(slideshow_html, height=450)

st.write("---")
st.info("Use o menu na barra lateral para navegar. Para editar, selecione o perfil 'Diretoria' e insira a senha.")
