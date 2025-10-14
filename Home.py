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
        
        /* --- NOVOS ESTILOS PARA OS CARDS DE ANIVERSARIANTE --- */

        /* Define um tamanho máximo para os cards e os centraliza na coluna */
        #birthday-cards [data-testid="stVerticalBlockBorderWrapper"] {
            max-width: 220px; /* Largura máxima do card */
            margin: 0 auto;   /* Centraliza o card na sua coluna */
        }

        /* Estilo para dar destaque ao dia do aniversário */
        .birthday-day {
            font-size: 2.5rem;      /* Tamanho grande */
            font-weight: bold;      /* Negrito */
            color: #1E88E5;         /* Cor azul, a mesma do contador */
            line-height: 1;         /* Remove espaçamento extra */
            margin-bottom: 10px;    /* Espaço abaixo do número */
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
    st.write("---"); logo_path = "logo_sao_jorge.png"
    if os.path.exists(logo_path): st.image(logo_path, width=150)
    st.title("São Jorge FC"); st.write("---"); st.caption("Desenvolvido por:")
    st.markdown("**Gabriel Conrado**"); st.caption("📱 (21) 97275-7256")


# --- PÁGINA PRINCIPAL ---

# --- TÍTULO CENTRALIZADO ---
logo_url = data_manager.get_github_image_url("logo_sao_jorge.png")
st.markdown(f"""...""", unsafe_allow_html=True) # Omitido para encurtar
# ... (conteúdo do título, sem alterações)

if st.session_state.role == 'Diretoria': st.markdown("<h5 style='text-align: center;'>🔑 Você está no modo Diretoria.</h5>", unsafe_allow_html=True)
else: st.markdown("<h5 style='text-align: center;'>👁️ Você está no modo Jogador.</h5>", unsafe_allow_html=True)
st.write("---")

# --- SEÇÃO: ANIVERSARIANTES DO MÊS (COM AS NOVAS MUDANÇAS) ---
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
    # Adiciona um ID ao container da seção para o CSS funcionar
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
                # Usa HTML para aplicar o novo estilo de destaque
                st.markdown(f"<p class='birthday-day'>{day_str}</p>", unsafe_allow_html=True)

                if player.get('shirt_number'): st.markdown(f"**Camisa: {player.get('shirt_number')}**")
    
    st.markdown('</div>', unsafe_allow_html=True)
st.write("---")

# --- CONTADOR E CARROSSEL (sem alterações) ---
st.header("⏳ Próximo Jogo")
countdown_html = """...""" # Omitido para encurtar
components.html(countdown_html, height=150)
st.write("---")
st.header("🖼️ Galeria do Time")
slideshow_html = f"""...""" # Omitido
components.html(slideshow_html, height=450)
st.write("---")
st.info("Use o menu na barra lateral para navegar. Para editar, selecione o perfil 'Diretoria' e insira a senha.")
