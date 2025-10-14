# Home.py
import streamlit as st
import data_manager
import os
import streamlit.components.v1 as components

st.set_page_config(page_title="Central do São Jorge FC", page_icon="🛡️", layout="wide")
data_manager.initialize_session_state()

with st.sidebar:
    logo_path = "logo_sao_jorge.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=150)
    st.title("São Jorge FC")
    st.write("---")
    if st.button("💾 Salvar Alterações na Nuvem", width='stretch', type="primary"):
        data_manager.save_data_to_db()

st.title("🛡️ Central de Dados do São Jorge FC")
st.markdown("##### // Monitoramento de Performance de Atletas //")
st.write("---")
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
st.success("Bem-vindo! O acesso está aberto para visualização e edição.")
st.info("Use o menu na barra lateral para navegar. Lembre-se de salvar suas alterações.")
