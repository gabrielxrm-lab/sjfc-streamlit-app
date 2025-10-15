# Home.py
import streamlit as st
import data_manager
import os
import streamlit.components.v1 as components
from datetime import datetime
import locale
import sidebar # Importa o novo arquivo da barra lateral

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
        /* Esconde o menu automático de páginas do Streamlit */
        [data-testid="stSidebarNav"] > ul {
            display: none;
        }
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

# --- CHAMA A BARRA LATERAL CENTRALIZADA ---
sidebar.create_sidebar()

# --- Inicializa os dados ---
data_manager.initialize_session_state()

# --- PÁGINA PRINCIPAL (CONTEÚDO RESTAURADO) ---

# --- TÍTULO CENTRALIZADO ---
logo_url = data_manager.get_github_image_url("logo_sao_jorge.png")
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

# --- CONTADOR REGRESSIVO ---
st.header("⏳ Próximo Jogo")
countdown_html = """<style>.countdown-container{font-family:'Consolas','Monaco',monospace;text-align:center;background-color:#262730;padding:20px;border-radius:10px;color:#FAFAFA;font-size:1.5rem}.countdown-time{font-size:2.5rem;font-weight:bold;color:#1E88E5;letter-spacing:5px}.countdown-label{font-size:1rem;text-transform:uppercase}</style><div class="countdown-container"><p class="countdown-label">Contagem regressiva para Domingo, 07:00</p><div id="countdown" class="countdown-time">Calculando...</div></div><script>function startCountdown(){const e=document.getElementById("countdown");if(e){const o=setInterval(()=>{const t=new Date,n=new Date;n.setDate(t.getDate()+(7-t.getDay())%7),n.setHours(7,0,0,0),n<t&&n.setDate(n.getDate()+7);const d=n-t;if(d<0)return e.innerHTML="É DIA DE JOGO!",void clearInterval(o);const a=Math.floor(d/864e5),s=Math.floor(d%864e5/36e5),l=Math.floor(d%36e5/6e4),i=Math.floor(d%6e4/1e3);e.innerHTML=`${a}d ${s.toString().padStart(2,"0")}h ${l.toString().padStart(2,"0")}m ${i.toString().padStart(2,"0")}s`},1e3)}}startCountdown();</script>"""
components.html(countdown_html, height=150)
st.write("---")

# --- CARROSSEL DE FOTOS ---
st.header("🖼️ Galeria do Time")
image_urls = [
    "https://raw.githubusercontent.com/gabrielxrm-lab/sjfc-streamlit-app/main/player_photos/slideshow/20250817_075933.jpg",
    "https://raw.githubusercontent.com/gabrielxrm-lab/sjfc-streamlit-app/main/player_photos/slideshow/20250817_080001.jpg",
    "https://raw.githubusercontent.com/gabrielxrm-lab/sjfc-streamlit-app/main/player_photos/slideshow/20250817_085832.jpg",
    "https://raw.githubusercontent.com/gabrielxrm-lab/sjfc-streamlit-app/main/player_photos/slideshow/20250817_085914.jpg",
    "https://raw.githubusercontent.com/gabrielxrm-lab/sjfc-streamlit-app/main/player_photos/slideshow/20250817_085945.jpg"
]
image_tags = "".join([f'<img class="slide" src="{url}">' for url in image_urls])
slideshow_html = f"""<style>.slideshow-container{{position:relative;width:100%;height:450px;overflow:hidden;border-radius:10px}}.slide{{position:absolute;width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity 1.5s ease-in-out}}.slide.active{{opacity:1}}</style><div class="slideshow-container">{image_tags}</div><script>let slideIndex=0;const slides=document.getElementsByClassName("slide");function showSlides(){{for(let e=0;e<slides.length;e++)slides[e].classList.remove("active");slideIndex++,slideIndex>slides.length&&(slideIndex=1),slides[slideIndex-1].classList.add("active"),setTimeout(showSlides,5e3)}}slides.length>0&&(slides[0].classList.add("active"),setTimeout(showSlides,5e3));</script>"""
components.html(slideshow_html, height=450)
st.write("---")
st.info("Use o menu na barra lateral para navegar. Para editar, selecione o perfil 'Diretoria' e insira a senha.")
