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

# --- Inicialização dos Dados ---
data_manager.initialize_session_state()

# --- Barra Lateral (Sidebar) ---
with st.sidebar:
    logo_path = "logo_sao_jorge.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=150)
    
    st.title("São Jorge FC")
    st.write("---")
    
    # Botão de salvar fica sempre visível
    if st.button("💾 Salvar Alterações na Nuvem", use_container_width=True, type="primary"):
        data_manager.save_data_to_db()

# --- Página Principal ---
st.title("🛡️ Central de Dados do São Jorge FC")
st.markdown("##### // Monitoramento de Performance de Atletas //")
st.write("---")

# --- CONTADOR REGRESSIVO PARA O PRÓXIMO DOMINGO ---
st.header("⏳ Próximo Jogo")

# Usamos HTML e JavaScript para criar o contador dinâmico
countdown_html = """
<style>
    .countdown-container {
        font-family: 'Consolas', 'Monaco', monospace;
        text-align: center;
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        color: #FAFAFA;
        font-size: 1.5rem; /* Aumenta o tamanho da fonte */
    }
    .countdown-time {
        font-size: 2.5rem; /* Deixa os números maiores */
        font-weight: bold;
        color: #1E88E5; /* Um azul vibrante */
        letter-spacing: 5px;
    }
    .countdown-label {
        font-size: 1rem;
        text-transform: uppercase;
    }
</style>

<div class="countdown-container">
  <p class="countdown-label">Contagem regressiva para Domingo, 07:00</p>
  <div id="countdown" class="countdown-time">Calculando...</div>
</div>

<script>
    function startCountdown() {
        const countdownElement = document.getElementById('countdown');

        const interval = setInterval(() => {
            const now = new Date();
            
            // Encontra o próximo domingo
            let nextSunday = new Date();
            nextSunday.setDate(now.getDate() + (7 - now.getDay()) % 7);
            nextSunday.setHours(7, 0, 0, 0);

            // Se o próximo domingo calculado já passou (hoje é domingo depois das 7h)
            if (nextSunday < now) {
                nextSunday.setDate(nextSunday.getDate() + 7);
            }

            const distance = nextSunday - now;

            if (distance < 0) {
                countdownElement.innerHTML = "É DIA DE JOGO!";
                clearInterval(interval);
                return;
            }

            // Cálculos de tempo
            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);

            // Formata para ter sempre dois dígitos (ex: 09, 08, 07)
            const fHours = hours.toString().padStart(2, '0');
            const fMinutes = minutes.toString().padStart(2, '0');
            const fSeconds = seconds.toString().padStart(2, '0');

            countdownElement.innerHTML = `${days}d ${fHours}h ${fMinutes}m ${fSeconds}s`;

        }, 1000);
    }

    // Inicia o contador quando o script carrega
    startCountdown();
</script>
"""

# Renderiza o HTML/JS no Streamlit
components.html(countdown_html, height=150)

st.write("---")
st.success("Bem-vindo! O acesso está aberto para visualização e edição.")
st.info("Use o menu na barra lateral para navegar. Lembre-se de salvar suas alterações.")
