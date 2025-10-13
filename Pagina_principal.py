# Home.py
import streamlit as st
import data_manager
import os
import streamlit.components.v1 as components

# --- Configuração da Página ---
st.set_page_config(
    page_title="Central do São Jorge FC",
    page_icon="🛡️",
    layout="wide"
)

# --- LÓGICA DE PERFIL E LOGIN ---
def handle_profile_selection():
    """Gerencia a seleção de perfil e o login da diretoria na barra lateral."""
    if 'role' not in st.session_state:
        st.session_state.role = 'Visitante'

    st.sidebar.title("Perfil de Acesso")
    profile = st.sidebar.radio(
        "Selecione seu perfil:",
        ('Visitante', 'Diretoria'),
        index=0 if st.session_state.role == 'Visitante' else 1,
        key='profile_selection'
    )

    if profile == 'Diretoria':
        if st.session_state.role == 'Diretoria':
            st.sidebar.success(f"Logado como Diretoria.")
            if st.sidebar.button("Sair do modo Edição"):
                st.session_state.role = 'Visitante'
                st.rerun()
        else:
            password = st.sidebar.text_input("Senha da Diretoria:", type="password")
            if st.sidebar.button("Entrar como Diretoria"):
                # Use st.secrets.get para evitar erros se a seção não existir
                creds = st.secrets.get("credentials", {})
                correct_password = creds.get("diretoria_password")
                
                if correct_password and password == correct_password:
                    st.session_state.role = 'Diretoria'
                    st.rerun()
                else:
                    st.sidebar.error("Senha incorreta ou não configurada.")
    else:
        st.session_state.role = 'Visitante'

# --- Roda a lógica de perfil e inicializa os dados ---
handle_profile_selection()
data_manager.initialize_session_state()

# --- Barra Lateral (Restante) ---
with st.sidebar:
    st.write("---")
    logo_path = "logo_sao_jorge.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=150)
    
    st.title("São Jorge FC")
    
    # --- SEÇÃO DE CONTATO ADICIONADA AQUI ---
    st.write("---")
    st.caption("Desenvolvido por:Gabir")
    st.markdown("**Gabriel Conrado**") # Edite com seu nome
    st.caption("📱 (21) 9 7275-7256") # Edite com seu telefone

# --- Página Principal ---
st.title("🛡️ Central de Dados do São Jorge FC")
if st.session_state.role == 'Diretoria':
    st.markdown("##### 🔑 Você está no modo **Diretoria**. Todas as funções de edição estão ativadas.")
else:
    st.markdown("##### 👁️ Você está no modo **Visitante**. Apenas visualização está disponível.")
st.write("---")

# --- CONTADOR REGRESSIVO ---
st.header("⏳ Próximo Jogo")
countdown_html = """
<style>
    .countdown-container { font-family: 'Consolas', 'Monaco', monospace; text-align: center; background-color: #262730; padding: 20px; border-radius: 10px; color: #FAFAFA; font-size: 1.5rem; }
    .countdown-time { font-size: 2.5rem; font-weight: bold; color: #1E88E5; letter-spacing: 5px; }
    .countdown-label { font-size: 1rem; text-transform: uppercase; }
</style>
<div class="countdown-container">
  <p class="countdown-label">Contagem regressiva para Domingo, 07:00</p>
  <div id="countdown" class="countdown-time">Calculando...</div>
</div>
<script>
    function startCountdown() {
        const countdownElement = document.getElementById('countdown'); if (!countdownElement) return;
        const interval = setInterval(() => {
            const now = new Date(); let nextSunday = new Date(); nextSunday.setDate(now.getDate() + (7 - now.getDay()) % 7); nextSunday.setHours(7, 0, 0, 0);
            if (nextSunday < now) { nextSunday.setDate(nextSunday.getDate() + 7); }
            const distance = nextSunday - now;
            if (distance < 0) { countdownElement.innerHTML = "É DIA DE JOGO!"; clearInterval(interval); return; }
            const days = Math.floor(distance / (1000 * 60 * 60 * 24)); const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)); const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60)); const seconds = Math.floor((distance % (1000 * 60)) / 1000);
            const fHours = hours.toString().padStart(2, '0'); const fMinutes = minutes.toString().padStart(2, '0'); const fSeconds = seconds.toString().padStart(2, '0');
            countdownElement.innerHTML = `${days}d ${fHours}h ${fMinutes}m ${fSeconds}s`;
        }, 1000);
    }
    startCountdown();
</script>
"""
components.html(countdown_html, height=150)

st.write("---")
st.info("Use o menu na barra lateral para navegar. Para editar, selecione o perfil 'Diretoria' e insira a senha.")

